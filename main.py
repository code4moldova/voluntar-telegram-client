"""This is the main entry point that starts the whole thing"""

import logging
import sys
import os

from telegram.ext import Updater, PicklePersistence

from constants import VERSION
from backend_api import Backender
from ajubot import Ajubot

log = logging.getLogger("main")

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)5s %(name)5s - %(message)s"
)

# you might want to re-enable these two lines if you really need to debug the bot's internals
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("JobQueue").setLevel(logging.WARNING)

log.info("Starting Ajubot v%s", VERSION)

try:
    token = os.environ["TELEGRAM_TOKEN"]
    covid_backend_url = os.environ["COVID_BACKEND"]
    covid_backend_user = os.environ["COVID_BACKEND_USER"]
    covid_backend_pass = os.environ["COVID_BACKEND_PASS"]
except KeyError as key:
    sys.exit(f"Set {key} environment variable before running the bot")

covid_backend = Backender(covid_backend_url, covid_backend_user, covid_backend_pass)

# this will be used to keep some state-related info in a file that survives across bot restarts
pickler = PicklePersistence("state.bin")

updater = Updater(token=token, use_context=True, persistence=pickler)
ajubot = Ajubot(updater, covid_backend)

try:
    ajubot.serve()
except KeyboardInterrupt:
    log.debug("Interactive quit")
    sys.exit()
finally:
    log.info("Quitting")
