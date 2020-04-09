"""This implements the core logic of the Telegram bot, all the message and command handlers are here"""

import logging
import os
from random import choice
from tempfile import NamedTemporaryFile

from telegram.ext import (
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
)
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, ParseMode
from telegram.ext.dispatcher import run_async


import constants as c
import keyboards as k
import restapi

log = logging.getLogger("ajubot")  # pylint: disable=invalid-name


# pylint: disable=too-many-public-methods
class Ajubot:
    """This class comprises the Telegram bot, a REST server for receiving input from external systems, as well as
    a client that sends data back to the backend."""

    def __init__(self, updater, backend):
        """Constructor
        :param updater: instance of Telegram updater object
        :param backend: instance of a Backender object, responsible for dealing with the Covid server"""
        self.updater = updater
        self.backend = backend
        self.rest = restapi.BotRestApi(
            self.hook_request_assistance,
            self.hook_cancel_assistance,
            self.hook_assign_assistance,
            self.hook_introspect,
        )

    def serve(self):
        """The main loop"""
        log.info("Starting REST API in separate thread")

        # NOTE: The bandit security checker will rightfully complain that we're binding to all interfaces.
        # TODO discuss this detail once we have a better idea about the deployment environment
        restapi.run_background(self.rest, "0.0.0.0", 5001)  # nosec

        log.info("Starting bot handlers")
        self.init_bot()
        self.updater.start_polling()
        self.updater.idle()

    @staticmethod
    def get_params(raw):
        """Retrieve the parameters that were transmitted along with the
        command, if any.
        :param raw: str, the raw text sent by the user"""
        parts = raw.split(" ", 1)
        return None if len(parts) == 1 else parts[1]

    @staticmethod
    def on_bot_start(update, context):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        log.info(
            "ADD %s, %s, %s, %s",
            user.username,
            user.full_name,
            update.effective_chat.id,
            user.language_code,
        )

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=c.MSG_PHONE_QUERY,
            reply_markup=ReplyKeyboardMarkup([[k.contact_keyboard]], one_time_keyboard=True),
        )

        # set some context data about this user, so we can rely on this later
        context.user_data["state"] = c.State.EXPECTING_PHONE_NUMBER

    @staticmethod
    def on_bot_help(update, _context):
        """Send a message when the command /help is issued."""
        update.message.reply_text(c.MSG_HELP)

    @staticmethod
    def on_bot_about(update, _context):
        """Send a message when the command /about is issued."""
        update.message.reply_text(c.MSG_ABOUT)

    @staticmethod
    def on_bot_offer_to_help(update, _context):
        """This is invoked when a volunteer explicitly tells us they are open for new requests."""
        # TODO consider notifying the backend about it
        update.message.reply_text(c.MSG_STANDBY)

    @staticmethod
    def on_bot_error(update, context):
        """Log Errors caused by Updates."""
        log.warning('Update "%s" caused error "%s"', update, context.error)

    @staticmethod
    def on_status(update, context):
        """Invoked when the user sends the /status command. At the moment this is only intended for debugging
        purposes, but it may be handy if the user has a queue of multiple requests"""
        current_state = context.user_data["state"]
        current_request = context.user_data.get("current_request", None)
        message = f"State: {current_state}\nRequest: {current_request}"

        context.bot.send_message(chat_id=update.message.chat_id, text=message)

    def init_bot(self):
        """Initialize the bot's handlers, which will be invoked when certain commands or messages are received"""
        dispatcher = self.updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.on_bot_start))
        dispatcher.add_handler(CommandHandler("help", self.on_bot_help))
        dispatcher.add_handler(CommandHandler("about", self.on_bot_about))
        dispatcher.add_handler(CommandHandler("vreausaajut", self.on_bot_offer_to_help))
        dispatcher.add_handler(CommandHandler("status", self.on_status))
        dispatcher.add_handler(CommandHandler("Da", self.on_accept))
        dispatcher.add_handler(CommandHandler("Nu", self.on_reject))

        dispatcher.add_handler(CallbackQueryHandler(self.negotiate_time, pattern="^eta.*"))
        dispatcher.add_handler(CallbackQueryHandler(self.confirm_dispatch, pattern="^caution.*"))
        dispatcher.add_handler(CallbackQueryHandler(self.confirm_handle, pattern="^handle.*"))
        dispatcher.add_handler(CallbackQueryHandler(self.confirm_wellbeing, pattern="^state.*"))
        dispatcher.add_handler(CallbackQueryHandler(self.confirm_symptom, pattern="^symptom.*"))
        dispatcher.add_handler(CallbackQueryHandler(self.confirm_wouldyou, pattern="^wouldyou.*"))
        dispatcher.add_handler(CallbackQueryHandler(self.confirm_further, pattern="^further.*"))

        dispatcher.add_handler(MessageHandler(Filters.photo, self.on_photo))
        dispatcher.add_handler(MessageHandler(Filters.contact, self.on_contact))
        dispatcher.add_handler(MessageHandler(Filters.text, self.on_text_message))
        dispatcher.add_error_handler(self.on_bot_error)

    def confirm_further(self, update, context):
        """This is invoked when they clicked "No further comments" in the end"""
        response_code = update.callback_query["data"]  # wouldyou_{yes|no}
        request_id = context.user_data["current_request"]
        log.info("No further comments req:%s %s", request_id, response_code)
        self.finalize_request(update, context, request_id)

    def confirm_wouldyou(self, update, context):
        """This is invoked when they answer yes/no to a "would you help again? question"""
        chat_id = update.effective_chat.id
        response_code = update.callback_query["data"]  # wouldyou_{yes|no}
        request_id = context.user_data["current_request"]
        log.info("Wouldyou req:%s %s", request_id, response_code)

        if response_code == "wouldyou_yes":
            # they want to keep returning to this beneficiary
            context.bot_data[request_id]["would_return"] = True
        else:
            context.bot_data[request_id]["would_return"] = False

        # Send the next question, asking if they have any special comments for future volunteers
        self.updater.bot.send_message(
            chat_id=chat_id,
            text=c.MSG_FEEDBACK_FURTHER_COMMENTS % context.bot_data[request_id]["beneficiary"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(k.further_comments_choices),
        )
        context.user_data["state"] = c.State.EXPECTING_FURTHER_COMMENTS

    def confirm_symptom(self, update, context):
        """This is invoked when the user reported the observed symptoms, if any"""
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        response_code = update.callback_query["data"]  # symptom_{fever|cough|heavybreathing}
        request_id = context.user_data["current_request"]
        log.info("Symptom req:%s %s", request_id, response_code)

        if response_code in ["symptom_none", "symptom_next", "symptom_noidea"]:
            # they pressed "Continue" or marked the end of all the symptoms list, move on to the next question
            self.updater.bot.send_message(
                chat_id=chat_id,
                text=c.MSG_WOULD_YOU_DO_THIS_AGAIN % context.bot_data[request_id]["beneficiary"],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(k.would_you_do_it_again_choices),
            )
            # remove the last state of the symptom keyboard from this user, such that the next time they receive an
            # assistance request, the keyboard is fresh
            if "symptom_keyboard" in context.user_data:
                del context.user_data["symptom_keyboard"]

        else:
            # they ticked an actual symptom, send an ACK to them as feedback. Note that we can get into this part of
            # the code multiple times, depending on how they tick the checkboxes - so we have to keep track of the
            # state and update the inline keyboard accordingly
            previous_keyboard = context.user_data.get("symptom_keyboard", k.symptom_choices)
            updated_keyboard = k.update_dynamic_keyboard_symptom(previous_keyboard, response_code)

            self.updater.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup(updated_keyboard),
            )

            # Update list of symptoms so we can send it to the server later in one swoop
            if "symptoms" in context.bot_data[request_id]:
                if response_code in context.bot_data[request_id]["symptoms"]:
                    # it is already in the list, which means that the user unticked the checkmark, so we remove it
                    context.bot_data[request_id]["symptoms"].remove(response_code)
                else:
                    # it isn't there, which means this is the first time the symptom is mentioned
                    context.bot_data[request_id]["symptoms"].append(response_code)
            else:
                # the list isn't there yet, we create a new one
                context.bot_data[request_id]["symptoms"] = [response_code]

    def confirm_wellbeing(self, update, context):
        """This is invoked when the user esimated the wellbeing of the assisted beneficiary"""
        chat_id = update.effective_chat.id
        response_code = int(update.callback_query["data"].split("_")[-1])  # state_{0..4}
        request_id = context.user_data["current_request"]
        log.info("Wellbeing req:%s %s", request_id, response_code)

        # Write this amount to the persistent state, so we can rely on it later
        context.bot_data[request_id]["wellbeing"] = response_code

        self.updater.bot.send_message(
            chat_id=chat_id,
            text=c.MSG_SYMPTOMS % context.bot_data[request_id]["beneficiary"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(k.symptom_choices, one_time_keyboard=True),
        )

    def finalize_request(self, update, context, request_id):
        """Thank the volunteer, send the final metadata to the server and then send the volunteer a happy GIF"""
        self.send_message_ex(update.effective_chat.id, c.MSG_THANKS_FINAL)

        # Instead of sending the whole shebang with the state of this request, send a clean dictionary that
        # only contains the necessary parts
        # request_payload = context.bot_data[request_id]
        request_payload = {
            "request_id": request_id,
            "amount": context.bot_data[request_id].get("amount", 0),
            "further_comments": context.bot_data[request_id].get("further_comments", ""),
            "symptoms": context.bot_data[request_id].get("symptoms", []),
            "wellbeing": context.bot_data[request_id]["wellbeing"],
            "would_return": context.bot_data[request_id]["would_return"],
        }

        self.backend.send_request_result(request_id, request_payload)

        # reset the user state so they're clean and ready for new assignments
        context.user_data["state"] = c.State.AVAILABLE
        context.user_data["current_request"] = None
        context.user_data["reviewed_request"] = None
        del context.bot_data[request_id]

        # cherry on top
        self.send_thanks_image(update.effective_chat.id)

    def send_thanks_image(self, chat_id):
        """Send a random thank you GIF from our local collection, as an added bonus"""
        gifs = os.listdir(os.path.join("res", "gifs"))
        # Bandit complains this is not a proper randomizer, but this is OK for the given use case
        specific_gif = os.path.join("res", "gifs", choice(gifs))  # nosec
        random_gif = open(specific_gif, "rb")
        self.updater.bot.send_animation(chat_id, random_gif, disable_notification=True)

    def on_text_message(self, update, context):
        """Invoked when the user sends an arbitrary text to the bot. We expect this to happen when they
        - send the receipt and indicate the amount
        - provide some feedback about the beneficiary"""
        chat_id = update.effective_chat.id
        log.info("Msg from:%s `%s`", chat_id, update.effective_message.text)

        if context.user_data["state"] == c.State.EXPECTING_AMOUNT:
            log.info("Vol:%s spent %s MDL on this request", chat_id, update.effective_message.text)
            # TODO validate the message and make sure it is a number, discuss whether this is necessary at all
            # TODO send this to the server, we need to define an API for that
            request_id = context.user_data["current_request"]

            # Write this amount to the persistent state, so we can rely on it later
            context.bot_data[request_id]["amount"] = update.effective_message.text

            # Then we have to ask them to send a receipt.
            self.send_message_ex(update.message.chat_id, c.MSG_FEEDBACK_RECEIPT)
            context.user_data["state"] = c.State.EXPECTING_RECEIPT
            return

        if context.user_data["state"] == c.State.EXPECTING_FURTHER_COMMENTS:
            log.info("Vol:%s has further comments: %s", chat_id, update.effective_message.text)
            request_id = context.user_data["current_request"]
            context.bot_data[request_id]["further_comments"] = update.effective_message.text
            self.finalize_request(update, context, request_id)
            return

        # if we got this far it means it is some sort of an arbitrary message that we weren't yet expecting
        log.warning("unexpected message ..........")

    def on_reject(self, update, _context):
        """Invoked when the user presses `No` after receiving a request for help"""
        self.send_message(update.message.chat_id, c.MSG_THANKS_NOTHANKS)

    def on_accept(self, update, _context):
        """Invoked when a user presses `Yes` after receiving a request for help"""
        self.updater.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Alege timpul",
            reply_markup=InlineKeyboardMarkup(k.build_dynamic_keyboard_first_responses()),
        )

    def confirm_handle(self, update, context):
        """Invoked when the volunteer confirmed that they are on their way to the beneficiary or while the request
        is in progress"""
        chat_id = update.effective_chat.id
        response_code = update.callback_query["data"]  # caution_ok or caution_cancel
        request_id = context.user_data["reviewed_request"]
        log.info("In progress req:%s %s", request_id, response_code)

        if response_code == "handle_onmyway":
            # they pressed "I am 'on my way' in the GUI"
            self.updater.bot.send_message(
                chat_id=chat_id,
                text=f"{c.MSG_SAFETY_INSTRUCTIONS} \n\n {c.MSG_LET_ME_KNOW_ARRIVE} \n\n p.s. {c.MSG_SAFETY_REMINDER}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(k.inprogress_choices),
            )
            self.backend.update_request_status(request_id, "onProgress")

        elif response_code == "handle_done":
            # they pressed 'Mission accomplished' in the GUI
            self.send_message_ex(chat_id, c.MSG_THANKS_FEEDBACK)
            self.updater.bot.send_message(
                chat_id=chat_id,
                text=c.MSG_FEEDBACK_EXPENSES,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(k.endgame_choices),
            )
            context.user_data["state"] = c.State.EXPECTING_AMOUNT
            self.backend.update_request_status(request_id, "done")

        elif response_code == "handle_no_expenses":
            # they indicated no compensation is required; proceed to the exit survey and ask some additional questions
            # about this request
            self.send_exit_survey(update, context)
            context.user_data["state"] = c.State.EXPECTING_EXIT_SURVEY

        elif response_code == "handle_cancel":
            # they bailed out at some point while the request was in progress
            self.send_message(chat_id, c.MSG_NO_WORRIES_LATER)
            context.user_data["reviewed_request"] = None
            context.user_data["state"] = c.State.AVAILABLE
            self.backend.update_request_status(request_id, "CANCELLED")

    def confirm_dispatch(self, update, context):
        """This is invoked when the responded to the "are you sure you are healthy?" message"""
        chat_id = update.effective_chat.id
        response_code = update.callback_query["data"]  # caution_ok or caution_cancel
        request_id = context.user_data["reviewed_request"]
        log.info("Confirm req:%s %s", request_id, response_code)

        request_details = context.bot_data[request_id]

        if response_code == "caution_ok":
            # They're in good health, let's go

            # send a location message, if this info is available in the request
            if "latitude" in request_details:
                self.updater.bot.send_location(
                    chat_id, request_details["latitude"], request_details["longitude"]
                )

            # then send the rest of the details as text
            message = c.MSG_FULL_DETAILS % request_details

            if "remarks" in request_details:
                message += "\n" + c.MSG_OTHER_REMARKS
                for remark in request_details["remarks"]:
                    message += "- %s\n" % remark

            message += "\n" + c.MSG_LET_ME_KNOW
            self.updater.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(k.handling_choices),
            )

        else:  # caution_cancel
            # eventually they chose not to handle this request
            # TODO ask them why, maybe they're sick and they need help? Discuss whether this is relevant
            self.send_message(chat_id, c.MSG_NO_WORRIES_LATER)
            context.user_data["reviewed_request"] = None
            context.user_data["state"] = c.State.AVAILABLE
            self.backend.update_request_status(request_id, "CANCELLED")

    def negotiate_time(self, update, context):
        """This is invoked when the user chooses one of the responses to an assistance request; it can be an ETA or
        a rejection."""
        chat_id = update.effective_chat.id
        response_code = update.callback_query["data"]  # eta_later, eta_never, eta_20:45, etc.
        log.info("Offer @%s @%s", update.effective_chat.id, response_code)

        if response_code == "eta_never":
            # the user pressed the button to say they're cancelling their offer
            self.send_message(chat_id, c.MSG_THANKS_NOTHANKS)
            context.user_data["reviewed_request"] = None
            context.user_data["state"] = c.State.AVAILABLE

        elif response_code == "eta_later":
            # Show them more options in the interactive menu
            self.updater.bot.send_message(
                chat_id=chat_id,
                text="Alege timpul",
                reply_markup=InlineKeyboardMarkup(k.build_dynamic_keyboard()),
            )
        else:
            # This is an actual offer, ot looks like `eta_20:40`, extract the actual timestamp
            offer = response_code.split("_")[-1]

            # tell the backend about it
            request_id = context.user_data["reviewed_request"]
            self.backend.relay_offer(request_id, chat_id, offer)

            # tell the user that this is now processed by the server
            self.send_message(chat_id, (c.MSG_ACK_TIME % offer) + c.MSG_COORDINATING)

    def on_contact(self, update, context):
        """This is invoked when the user sends us their contact information, which includes their phone number."""
        user = update.effective_user
        phone = update.message.contact.phone_number
        log.info(
            "TEL from %s, %s, @%s, %s",
            user.username,
            user.full_name,
            update.effective_chat.id,
            phone,
        )

        # Here's an example of what else you can find in update['message'].contact.to_dict()
        # {'phone_number': '+4500072470000', 'first_name': 'Alex', 'user_id': 253150000}
        # And some user-related details in update.effective_user.to_dict()
        # {'first_name': 'Alex', 'id': 253150000, 'is_bot': False, 'language_code': 'en', 'username': 'ralienpp'}

        # Tell the backend about it, such that from now on it knows which chat_id corresponds to this user
        self.backend.link_chatid_to_volunteer(user.username, update.effective_chat.id, phone)

        # Acknowledge receipt and tell the user that we'll contact them when new requests arrive
        update.message.reply_text(c.MSG_STANDBY)

        # Mark the user as available once onboarding is complete
        context.user_data["state"] = c.State.AVAILABLE

    def on_photo(self, update, context):
        """Invoked when the user sends a photo to the bot. In our case, photos are always shopping receipts. Keep in
        mind that there could be multiple photos in a message."""
        user = update.effective_user
        photo_count = len(update.message.photo)
        log.info(
            "PIC from %s, %s, @%s, #%i",
            user.username,
            user.full_name,
            update.effective_chat.id,
            photo_count,
        )

        if context.user_data["state"] != c.State.EXPECTING_RECEIPT:
            # Got an image from someone we weren't expecting to send any. We log this, and TODO decide what
            log.debug("Got image when I was not expecting one")
            return

        # Process each photo
        for entry in update.message.photo:
            raw_image = entry.get_file().download_as_bytearray()

            # At this point the image is in the memory
            with NamedTemporaryFile(delete=False, prefix=str(update.effective_chat.id)) as pic:
                pic.write(raw_image)
                log.debug("Image written to %s", pic.name)

            # Note: you can disable this line when testing locally, if you don't have an actual backend that will
            # serve this request
            self.backend.upload_shopping_receipt(raw_image, context.user_data["current_request"])

        # if we got this far it means that we're ready to proceed to the exit survey and ask some additional questions
        # about this request
        self.send_exit_survey(update, context)
        context.user_data["state"] = c.State.EXPECTING_EXIT_SURVEY

    def send_exit_survey(self, update, context):
        """Initiate the questionnaire that asks about the beneficiary's mood and symptoms"""
        chat_id = update.effective_chat.id
        request_id = context.user_data["current_request"]

        self.updater.bot.send_message(
            chat_id=chat_id,
            text=c.MSG_FEEDBACK_BENEFICIARY_MOOD % context.bot_data[request_id]["beneficiary"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(k.wellbeing_choices, one_time_keyboard=True),
        )

    @run_async
    def hook_request_assistance(self, data):
        """This will be invoked by the REST API when a new request for
        assistance was received from the backend.
        :param data: dict, the format is defined in `assistance_request`, see readme"""
        request_id = data["request_id"]
        log.info("NEW request for assistance %s", request_id)
        volunteers_to_contact = data["volunteers"]

        needs = ""
        for item in data["needs"]:
            needs += f"- {item}\n"

        assistance_request = c.MSG_REQUEST_ANNOUNCEMENT % (data["address"], needs)

        for chat_id in volunteers_to_contact:
            if chat_id not in self.updater.persistence.user_data:
                log.debug("User %s hasn't added the updater to their contacts, skipping.", chat_id)
                continue

            current_state = self.updater.persistence.user_data[chat_id].get("state", None)

            if current_state in [c.State.REQUEST_IN_PROGRESS, c.State.REQUEST_ASSIGNED]:
                log.debug("Vol%s is already working on a request, skippint")
                continue

            self.updater.bot.send_message(
                chat_id=chat_id,
                text=assistance_request,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardMarkup(k.initial_responses, one_time_keyboard=True),
            )

            # update this user's state and keep the request_id as well, so we can use it later
            updated_state = {"state": c.State.REQUEST_SENT, "reviewed_request": request_id}
            self.updater.dispatcher.user_data[chat_id].update(updated_state)

        self.updater.dispatcher.bot_data.update({request_id: data})
        self.updater.dispatcher.update_persistence()

    def hook_introspect(self):
        """Return a dictionary with the user_data and bot_data, to make introspection easier"""
        # NOTE that this doesn't use @run_async, unlike other hooks, because it has to return right away
        user_state = self.updater.persistence.user_data
        bot_state = self.updater.persistence.bot_data
        return {"volunteers": user_state, "requests": bot_state}

    @run_async
    def hook_cancel_assistance(self, data):
        """This will be invoked by the REST API when an assigned request for
        assistance was CANCELED from the backend.
        :param data: dict, see `cancel_help_request` in the readme"""
        request_id = data["request_id"]
        assignee_chat_id = data["volunteer"]
        log.info("CANCEL req:%s", request_id)
        self.send_message(assignee_chat_id, c.MSG_REQUEST_CANCELED)

        self.updater.dispatcher.user_data[assignee_chat_id].update(
            {"current_request": None, "reviewed_request": None, "state": c.State.AVAILABLE}
        )
        del self.updater.dispatcher.bot_data[request_id]
        self.updater.dispatcher.update_persistence()

    @run_async
    def hook_assign_assistance(self, data):
        """This will be invoked by the REST API when a new request for
        assistance was ASSIGNED to a specific volunteer.
        :param data: dict, see `assign_assistance` in the readme"""
        request_id = data["request_id"]
        assignee_chat_id = data["volunteer"]
        log.info("ASSIGN req:%s to vol:%s", request_id, assignee_chat_id)

        try:
            request_details = self.updater.persistence.bot_data[request_id]
        except KeyError:
            log.debug("No such request %s, ignoring", request_id)
            return
        else:
            self.updater.dispatcher.bot_data[request_id].update({"time": data["time"]})

        # first of all, notify the others that they are off the hook and update their state accordingly
        for chat_id in request_details["volunteers"]:
            if chat_id != assignee_chat_id:
                self.send_message(chat_id, c.MSG_ANOTHER_ASSIGNEE)
                updated_state = {"state": c.State.AVAILABLE, "reviewed_request": None}
                self.updater.dispatcher.user_data[chat_id].update(updated_state)

        self.updater.dispatcher.user_data[assignee_chat_id].update({"current_request": request_id})
        self.updater.dispatcher.update_persistence()

        # notify the assigned volunteer, so they know they're responsible; at this point they still have to confirm
        # that they're in good health and they still have an option to cancel
        self.updater.bot.send_message(
            chat_id=assignee_chat_id,
            text=c.MSG_CAUTION,
            reply_markup=InlineKeyboardMarkup(k.caution_choices),
        )

    @run_async
    def send_message(self, chat_id, text):
        """Send a message to a specific chat session. Note that this is an async sender, these messages may arrive
        slightly out of order
        :param chat_id: int, chat identifier
        :param text: str, the text to be sent to the user"""
        self.updater.bot.sendMessage(chat_id=chat_id, text=text)
        log.info("Send msg @%s: %s..", chat_id, text[:20])

    def send_message_ex(self, chat_id, text, parse_mode=ParseMode.MARKDOWN):
        """Send a message to a specific chat session, in Markdown by default. This is a synchronous sender, it will
        send it right away.
        :param chat_id: int, chat identifier
        :param text: str, the text to be sent to the user
        :param parse_mode: e.g. ParseMode.MARKDOWN"""
        self.updater.bot.sendMessage(chat_id=chat_id, text=text, parse_mode=parse_mode)
        log.info("SendEx msg @%s: %s..", chat_id, text[:20])
