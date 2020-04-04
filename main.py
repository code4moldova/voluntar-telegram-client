import logging
import sys
import os
from tempfile import NamedTemporaryFile

from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import ReplyKeyboardMarkup
from telegram.ext.dispatcher import run_async


import constants as c
import keyboards as k
import restapi
from backend_api import Backender

log = logging.getLogger("ajubot")


class Ajubot:
    def __init__(self, bot, backend):
        """Constructor
        :param bot: instance of Telegram bot object
        :param backend: instance of a Backender object, responsible for dealing with the Covid server"""
        self.bot = bot
        self.backend = backend
        self.rest = restapi.BotRestApi(
            self.hook_request_assistance, self.hook_cancel_assistance, self.hook_assign_assistance,
        )

    def serve(self):
        """The main loop"""
        log.info("Starting REST API in separate thread")

        # NOTE: The bandit security checker will rightfully complain that we're binding to all interfaces.
        # TODO discuss this detail once we have a better idea about the deployment environment
        restapi.run_background(self.rest, "0.0.0.0", 5001)  # nosec

        log.info("Starting bot handlers")
        self.init_bot()
        self.bot.start_polling()
        self.bot.idle()

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
        # TODO add this to some local storage, maybe sqlite?
        log.info(
            f"ADD {user.username}, {user.full_name}, @{update.effective_chat.id}, {user.language_code}"
        )
        update.message.reply_text(f"Bine ai venit, {user.username or user.full_name}.")

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=c.MSG_PHONE_QUERY,
            reply_markup=ReplyKeyboardMarkup([[k.contact_keyboard]], one_time_keyboard=True),
        )

        # TODO mark this user's context, that we're expecting their phone number

    @staticmethod
    def on_bot_help(update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text(c.MSG_HELP)

    @staticmethod
    def on_bot_about(update, context):
        """Send a message when the command /about is issued."""
        update.message.reply_text(c.MSG_ABOUT)

    @staticmethod
    def on_bot_offer_to_help(update, context):
        """This is invoked when a volunteer explicitly tells us they are open for new requests."""
        # TODO consider notifying the backend about it
        update.message.reply_text(c.MSG_STANDBY)

    @staticmethod
    def on_bot_error(update, context):
        """Log Errors caused by Updates."""
        log.warning('Update "%s" caused error "%s"', update, context.error)

    def init_bot(self):
        dispatcher = self.bot.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.on_bot_start))
        dispatcher.add_handler(CommandHandler("help", self.on_bot_help))
        dispatcher.add_handler(CommandHandler("about", self.on_bot_about))
        dispatcher.add_handler(CommandHandler("vreausaajut", self.on_bot_offer_to_help))

        dispatcher.add_handler(MessageHandler(Filters.photo, self.on_photo))
        dispatcher.add_handler(MessageHandler(Filters.contact, self.on_contact))
        dispatcher.add_error_handler(self.on_bot_error)

    def on_contact(self, update, _context):
        """This is invoked when the user sends us their contact information, which includes their phone number."""
        user = update.effective_user
        phone = update.message.contact.phone_number
        log.info(
            f"TEL from {user.username}, {user.full_name}, @{update.effective_chat.id}, {phone}"
        )

        # Here's an example of what else you can find in update['message'].contact.to_dict()
        # {'phone_number': '+4500072470000', 'first_name': 'Alex', 'user_id': 253150000}
        # And some user-related details in update.effective_user.to_dict()
        # {'first_name': 'Alex', 'id': 253150000, 'is_bot': False, 'language_code': 'en', 'username': 'ralienpp'}

        # Tell the backend about it, such that from now on it knows which chat_id corresponds to this user
        self.backend.link_chatid_to_volunteer(user.username, update.effective_chat.id, phone)

        # Acknowledge receipt and tell the user that we'll contact them when new requests arrive
        update.message.reply_text(c.MSG_STANDBY)

    @staticmethod
    def on_photo(update, _context):
        """Invoked when the user sends a photo to the bot. In our case, photos are always shopping receipts. Keep in
        mind that there could be multiple photos in a message."""
        user = update.effective_user
        photo_count = len(update.message.photo)
        log.info(
            f"PHOTO from {user.username}, {user.full_name}, @{update.effective_chat.id}, #{photo_count}"
        )

        # Process each photo
        for entry in update.message.photo:
            raw_image = entry.get_file().download_as_bytearray()

            # At this point the image is in the memory
            with NamedTemporaryFile(delete=False, prefix=update.effective_chat.id) as f:
                f.write(raw_image)
                log.debug("Image written to %s", f.name)

        # TODO Send it to the server via REST

    @run_async
    def hook_request_assistance(self, raw_data):
        """This will be invoked by the REST API when a new request for
        assistance was received from the backend.
        :param raw_data: TODO: discuss payload format, see readme"""
        log.info("NEW request for assistance")

    @run_async
    def hook_cancel_assistance(self, raw_data):
        """This will be invoked by the REST API when a new request for
        assistance was CANCELED from the backend.
        :param raw_data: TODO: discuss payload format, see readme"""
        log.info("CANCEL request for assistance")

    @run_async
    def hook_assign_assistance(self, raw_data):
        """This will be invoked by the REST API when a new request for
        assistance was ASSIGNED to a specific volunteer.
        :param raw_data: TODO: discuss payload format, see readme"""
        volunteer = "hardcoded for now"
        log.info("ASSIGN request for assistance to %s", volunteer)
        # self.send_message("")

    @run_async
    def send_message(self, chat_id, text):
        """Send a message to a specific chat session
        :param chat_id: int, chat identifier
        :param text: str, the text to be sent to the user"""
        self.bot.bot.sendMessage(chat_id=chat_id, text=text)
        log.info("Send msg @%s: %s", chat_id, text)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(levelname)5s %(name)5s - %(message)s"
    )

    # you might want to re-enable these two lines if you really need to debug the bot's internals
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("JobQueue").setLevel(logging.WARNING)

    log.info("Starting Ajubot v%s", c.VERSION)

    try:
        token = os.environ["TELEGRAM_TOKEN"]
        covid_backend_url = os.environ["COVID_BACKEND"]
        covid_backend_user = os.environ["COVID_BACKEND_USER"]
        covid_backend_pass = os.environ["COVID_BACKEND_PASS"]
    except KeyError as key:
        sys.exit(f"Set {key} environment variable before running the bot")

    covid_backend = Backender(covid_backend_url, covid_backend_user, covid_backend_pass)

    bot = Updater(token=token, use_context=True)
    ajubot = Ajubot(bot, covid_backend)

    try:
        ajubot.serve()
    except KeyboardInterrupt:
        log.debug("Interactive quit")
        sys.exit()
    finally:
        log.info("Quitting")
