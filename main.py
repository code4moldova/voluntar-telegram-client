import logging
import sys
import os

from telegram.ext import (
    Updater,
    CommandHandler,
)
from telegram import ReplyKeyboardMarkup
from telegram.ext.dispatcher import run_async

import constants as c
import keyboards as k
import restapi

log = logging.getLogger("ajubot")


class Ajubot:
    def __init__(self, bot):
        """Constructor
        :param bot: instance of Telegram bot object"""
        self.bot = bot
        self.rest = restapi.BotRestApi(
            self.hook_request_assistance,
            self.hook_cancel_assistance,
            self.hook_assign_assistance,
        )

    def serve(self):
        """The main loop"""
        log.info("Starting REST API in separate thread")
        restapi.run_background(self.rest)

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

        context.bot.sendMessage(
            chat_id=update.message.chat_id,
            text="test",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(k.default_board, one_time_keyboard=True),
        )

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

        dispatcher.add_error_handler(self.on_bot_error)

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
    except KeyError:
        sys.exit("Set TELEGRAM_TOKEN environment variable before running the bot")

    bot = Updater(token=token, use_context=True)
    ajubot = Ajubot(bot)

    try:
        ajubot.serve()
    except KeyboardInterrupt:
        log.debug("Interactive quit")
        sys.exit()
    finally:
        log.info("Quitting")
