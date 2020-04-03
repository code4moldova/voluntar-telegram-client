# Telegram bot that connects volunteers to beneficiaries

- See `doc/chat_interaction.svg` to get an idea of the workflow
- Code derived from https://github.com/roataway/telegram-bot

## The big picture

```
                                                                          (start here)

                                                                      +--------------------+
                                                                      |    pool of fixers  |
                          +--------------------------------+          |  F1, F2, .. Fn     |
                          |                                |          +--+-----------------+
                          |   +-----------------+          |             |
                          |   | nickname-chat   |          |             |  the fixer uses the UI to
                          |   |   KV-store      |          |             |  add new help requests
                          |   +---------^-------+          |             |  to the system
+--------------+          |             |                  |             |
|              |  notify  |             |                  |         +---v---------------+
|   pool of    |  and     |   +---------v-------+          |         |    frontend       |
|   volunteers |  interact|   |   Telegram bot  |     feedack via    |                   |
|              <-------------->                 |     REST API       +-------------------+
|   Vol_1      |          |   |                 +----------+----+             |new
|   Vol_2      |          |   +-----^-----------+          |    |             |request
|   ..         |          |         |                      |    |    +--------v----------+
|   Vol_n      |          |         |  notify              +    +---->     backend       |
|              |          |         |                notify bot      |                   |
|              |          |   +-----+-----------+    about a new  +--+                   |
+--------------+          |   |   REST API      |    help request |  +-------------------+
                          |   |                 <----------+------+
                          |   |                 |          |
                          |   +-----------------+          |
                          |                                |
                          |                                |
                          |                 (this repo)    |
                          +--------------------------------+


```

Legend:

- `REST API` is invoked by the backend to notify the bot about new requests for assistance. This eliminates the need for
the bot to continuously poll the backend for new requests.
- `nickname-chat KV`: Telegram operates with a `chat_id` when sending a message to a user, whereas the backend only knows
of the volunteers' nicknames. When a volunteer adds the bot to their contact list, the bot receives the `chat_id` and
the `nickname` (the same nickname that the backend knows about). This is saved in the KV store, such that in
the future, when the backend notifies the bot about a new request for assistance (including a list of nicknames of
volunteers to contact), we'll know which `chat_id` corresponds to each volunteer. TODO: ideally, the backend should
send us a list of `(chat_id, nickname)` tuples, so we don't need this KV store here at all.


## Endpoints

The following endpoints are used for interaction between the backend and the Telegram bot:

    - backend->bot: notify about a new request {requestId, beneficiary name, list of volunteer IDs to send alert to, street address}
    - bot->backend: notify about offers from volunteers about a specific requestID
    - backend->bot: notify the specific volunteer that {they are responsible | they've been cancelled}
    - bot->backend: volunteer is on their way
    - bot->backend: mission accomplished
    - bot->backend: send the receipt
    - bot->backend: exit survey
    
    
## Payloads

Payload sample `assistance_request` (TODO discuss):

    {
        "request_id": "fe91e4b6-e902-4d03-8500-d058673cb9bd",
        "beneficiary": "Martina Cojocaru",
        "address": "str. 31 August",
        "needs": "Medicamente, produse alimentare,
        "gotSymptoms": false,
        "isInfected": false,
        "safetyCode": "Izvor-45",
        "phoneNumber": "+373 777 77 777",
        "remarks": ["Nu lucreaza ascensorul", "Are caine rau"],
        "gotFunds": true
        "volunteers": ["theresa", "curcudush", "priquindel"]
      }




## How to run it

1. Talk to @BotFather to register your bot and get a token, as described here: https://core.telegram.org/bots#6-botfather
2. Install dependencies from `requirements.txt` using `virtualenv` or `pipenv`
3. Set the `TELEGRAM_TOKEN` environment variable to the token, e.g. `export TELEGRAM_TOKEN=1123test`
4. Run `python main.py`

Optionally, you can open http://localhost:5000 to send an example of a payload, simulating an actual request that came
from the backend.


# How to contribute

1. Run ``make autoformat`` to format all ``.py`` files
2. Run ``make verify`` and examine the output, looking for issues that need to be addressed
3. Open a pull request with your changes
