from telegram import KeyboardButton

import constants as c

default_board = [
    [KeyboardButton("/vreausaajut")],
    [KeyboardButton("/help"), KeyboardButton("/about")],
]

# This one is used during onboarding, to ask for the phone number
contact_keyboard = KeyboardButton(text=c.BTN_GET_PHONE, request_contact=True)

# this is the inline keyboard that is sent to the volunteer along with each request for assistance
initial_responses = [
    [KeyboardButton("Nu")],
    [KeyboardButton("În 30min"), KeyboardButton("Într-o oră"), KeyboardButton("În 2 ore")],
    [KeyboardButton("Altă oră")],
]
