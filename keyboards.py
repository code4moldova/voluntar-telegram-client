# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from telegram import KeyboardButton, InlineKeyboardButton

import constants as c

default_board = [
    [KeyboardButton("/vreausaajut")],
    [KeyboardButton("/help"), KeyboardButton("/about")],
]

# This one is used during onboarding, to ask for the phone number
contact_keyboard = KeyboardButton(text=c.BTN_GET_PHONE, request_contact=True)

# this keyboard is sent to the volunteer along with each request for assistance
initial_responses = [
    [KeyboardButton("/Da")],
    [KeyboardButton("/Nu")],
]

# this one is not used at the moment
eta_first_responses = [
    [
        InlineKeyboardButton("În 30min", callback_data="eta_30min"),
        InlineKeyboardButton("Într-o oră", callback_data="eta_1h"),
        InlineKeyboardButton("În 2 ore", callback_data="eta_2h"),
    ],
    [InlineKeyboardButton("Altă oră", callback_data="eta_later")],
    [InlineKeyboardButton("Anulează", callback_data="eta_never")],
]


# this keyboard is sent to them before dispatching the volunteer to a beneficiary, to make sure they are
# healthy themselves
caution_choices = [
    [InlineKeyboardButton("Sunt sănătos și fără simptome", callback_data="caution_ok")],
    [InlineKeyboardButton("Hmm... Mai bine anulez", callback_data="caution_cancel")],
]

# this keyboard is sent to them before dispatching the volunteer to a beneficiary, to keep track of their progress
handling_choices = [
    [InlineKeyboardButton("M-am pornit", callback_data="handle_onmyway")],
    [InlineKeyboardButton("Anulează", callback_data="handle_cancel")],
]

# shown after the volunteer pressed "I'm on my way"
inprogress_choices = [
    [InlineKeyboardButton("Misiune îndeplinită", callback_data="handle_done")],
    [InlineKeyboardButton("Anulează", callback_data="handle_cancel")],
]

# shown when they pressed "mission accomplished"
endgame_choices = [
    [
        InlineKeyboardButton(
            "Nu am avut cheltuieli sau mi s-au întors banii", callback_data="handle_no_expenses"
        )
    ],
]

# shown when the user is inquired about the beneficiary's wellbeing
wellbeing_choices = [
    [
        InlineKeyboardButton(
            "🥵 Foarte rea", callback_data="state_0"
        ),  # there's an invisible emoji in the beginning
        InlineKeyboardButton("😟 Rea", callback_data="state_1"),
    ],
    [InlineKeyboardButton("😐 Neutră", callback_data="state_2")],
    [
        InlineKeyboardButton("😃 Bună", callback_data="state_3"),
        InlineKeyboardButton("😁 Foarte bună", callback_data="state_4"),
    ],
]


# shown when asking whether the beneficiary has any symptoms
symptom_choices = [
    [
        InlineKeyboardButton("☐ Febră", callback_data="symptom_fever"),
        InlineKeyboardButton("☐ Tuse", callback_data="symptom_cough"),
        InlineKeyboardButton("☐ Respiră greu", callback_data="symptom_heavybreathing"),
    ],
    [InlineKeyboardButton("👍 Nu are simptome", callback_data="symptom_none")],
    [InlineKeyboardButton("Nu știu", callback_data="symptom_noidea")],
    [InlineKeyboardButton("Mai departe", callback_data="symptom_next")],
]


def toggle_checkmark(text):
    """Toggle a checkmark in a beginning of a string, e.g. '☐ Febră'->'☑ Febră' and vice versa"""
    if "☑" in text:
        return text.replace("☑", "☐")

    return text.replace("☐", "☑")


def update_dynamic_keyboard_symptom(keyboard, symptom):
    """Generate a new keyboard to provide a smooth user experience when ticking and unticking checkboxes, it
    is used for collecting a list of symptoms"""
    # UGLY and hardcoded but it is not essential at the moment
    if symptom == "symptom_fever":
        keyboard[0][0].text = toggle_checkmark(keyboard[0][0].text)
    elif symptom == "symptom_cough":
        keyboard[0][1].text = toggle_checkmark(keyboard[0][1].text)
    elif symptom == "symptom_heavybreathing":
        keyboard[0][2].text = toggle_checkmark(keyboard[0][2].text)

    return keyboard


# shown when asking whether the beneficiary has any symptoms
would_you_do_it_again_choices = [
    [InlineKeyboardButton("Da", callback_data="wouldyou_yes")],
    [InlineKeyboardButton("Nu", callback_data="wouldyou_no")],
]

# shown when asking whether the volunteer has further comments about the beneficiary
further_comments_choices = [
    [InlineKeyboardButton("Nu am comentarii", callback_data="furthercomments_no")],
]


def build_dynamic_keyboard_first_responses():
    """Build a dynamic keyboard that looks like `eta_first_responses`, but where the callback data contains
    timestamps that are N minutes in the future from now"""
    now = datetime.utcnow()
    timedelta(minutes=30)

    return [
        [
            InlineKeyboardButton(
                "În 30min", callback_data="eta_" + (now + timedelta(minutes=30)).strftime("%H:%M")
            ),
            InlineKeyboardButton(
                "Într-o oră", callback_data="eta_" + (now + timedelta(hours=1)).strftime("%H:%M")
            ),
            InlineKeyboardButton(
                "În 2 ore", callback_data="eta_" + (now + timedelta(hours=2)).strftime("%H:%M")
            ),
        ],
        [InlineKeyboardButton("Altă oră", callback_data="eta_later")],
        [InlineKeyboardButton("Anulează", callback_data="eta_never")],
    ]


def get_etas_today(time_from=None):
    """Construct a list of time options to choose from, starting with NOW, until the end of TODAY
    :param time_from: optional datetime, by default it is now"""
    time_from = time_from or datetime.utcnow()
    today = datetime.today().date()

    times = []
    step = timedelta(minutes=30)
    i = 1
    while True:
        new_entry = time_from + i * step
        times.append(new_entry)
        i += 1
        if new_entry.date() > today:
            break
    return times


def chunkify(lst, n=4):
    """Yield successive n-sized chunks from lst. Taken from https://stackoverflow.com/a/312464/27342"""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def build_dynamic_keyboard(time_from=None):
    """Construct a keyboard with various time options to choose from
    :param time_from: optional datetime, by default it is now
    :returns: Telegram keyboard that has 4 time options per row, it looks like this:
    keyboard = [
        [InlineKeyboardButton("15:32", callback_data="eta_15:32"),
        InlineKeyboardButton("16:02", callback_data="eta_16:02"),
        InlineKeyboardButton("16:32", callback_data="eta_16:32")],
        ...
    ]
    """
    times = [item.strftime("%H:%M") for item in get_etas_today(time_from)]
    chunkified_times = chunkify(times)

    keyboard = []
    for entry in chunkified_times:
        row = []
        for sub_entry in entry:
            row.append(InlineKeyboardButton(sub_entry, callback_data="eta_" + sub_entry))
        keyboard.append(row)
    return keyboard


if __name__ == "__main__":
    # print(build_dynamic_keyboard())
    # print(build_dynamic_keyboard_first_responses())

    print(update_dynamic_keyboard_symptom(symptom_choices, "symptom_fever"))
