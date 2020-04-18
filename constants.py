"""Constants used throughout the code, mainly strings"""

from enum import Enum

VERSION = "0.5.0"  # follow SemVer conventions: https://semver.org/
URL = "code4md.com"

# Though we operate with UTC internally, the times will be shown to the users
# in their local timezone.
TIMEZONE = "Europe/Chisinau"

# Messages used in various phases of interaction
MSG_HELP = "Încearcă comanda /vreausaajut"
MSG_ABOUT = f"Ajubot v{VERSION}, {URL}"
MSG_STANDBY = "Mulțumesc! Te vom alerta când apar cereri noi."
MSG_THANKS_NOTHANKS = "Bine, te vom alerta când apar cereri noi."
MSG_THANKS_FINAL = "Îți mulțumim mult pentru ajutor."
MSG_ACK_TIME = "Bine, ora %s, "
MSG_COORDINATING = "coordonez cu alți voluntari."
MSG_PHONE_QUERY = "Te rog să ne transmiți numărul de contact, pentru a începe înregistrarea."
MSG_ANOTHER_ASSIGNEE = "Altcineva merge acolo. Te anunțăm când apar noi cereri"
MSG_REQUEST_CANCELED = "Cererea de ajutor a fost anulată."
MSG_LET_ME_KNOW = "Anunță-mă când te-ai pornit"
MSG_LET_ME_KNOW_ARRIVE = "Anunță-mă când e gata"
MSG_DISABILITY = "♿ Atenție, %(beneficiary)s are careva dizabilități, posibil va deschide mai lent ușa sau va răspunde întârziat, să ai răbdare."
MSG_OTHER_REMARKS = "*Remarci* de la alți voluntari:\n"
MSG_NO_WORRIES_LATER = (
    "Bine, nu te îngrijora, vor apărea și alte cereri în viitor. Ai grijă de tine!"
)
MSG_EXPLICIT_ASSIGNMENT = "Un operator ți-a atribuit o cerere, în curând primești detalii..."

MSG_CAUTION = """Înainte de a porni la drum, gândește-te că poți să infectezi o persoană vulnerabilă, prin neatenție sau neglijență!

Ești sigur că nu ai niciun simptom din acestea?
- tuse
- febră
- respirație dificilă
"""

MSG_FULL_DETAILS = """*Confirmat* pentru ora *%(time)s*

*Adresa*: %(address)s
*Nume*: %(beneficiary)s
*Cod*: %(safetyCode)s
*Telefon*: %(phoneNumber)s
"""

MSG_SAFETY_INSTRUCTIONS = """Nu uita:
- Nu intra în contact direct
- Poartă *mănuși și mască*
- *Dezinfectează-ți* mâinile
- Păstrează distanța de *cel puțin 2m*
- Lasă produsele la ușă
- După bani - *spală mâinile 20s*"""

MSG_SAFETY_REMINDER = """Când ajungi, întreabă-i despre:
- Are cineva din familie tuse, febră, nas curgător, sau dureri de cap?
- Au contactat cu cineva care s-a întors din străinătate în ultimele 14 zile?
- Își măsoară regulat temperatura?"""

MSG_REQUEST_ANNOUNCEMENT = "O persoană din *%s* are nevoie de:\n%s\nPoți ajuta?"

MSG_THANKS_FEEDBACK = (
    "Îți mulțumesc pentru ajutor. Te rog să-mi spui câte ceva despre această experiență:"
)

MSG_FEEDBACK_EXPENSES = (
    "Ai suportat careva cheltuieli? Dacă da, introdu suma în lei (e.g., 45 sau 45.82)"
)
MSG_FEEDBACK_RECEIPT = "Te rog, expediază-mi *factura cumpărăturilor* efectuate"
MSG_FEEDBACK_RECEIPT_ABSENT = "Nu am factură"
MSG_FEEDBACK_BENEFICIARY_MOOD = "Cum apreciezi *dispoziția* persoanei *%s*?"
MSG_FEEDBACK_FURTHER_COMMENTS = "Ai careva remarci adiționale pentru noi sau pentru alți voluntari care vor ajuta *%s*? Dacă da, scrie-le în următorul mesaj"

MSG_WOULD_YOU_DO_THIS_AGAIN = "Vrei să ai grijă de *%s* în continuare?"
MSG_SYMPTOMS = "*%s* manifestă careva din simptomele COVID-19? (poți alege câteva)"


# Button labels
BTN_GET_PHONE = "Trimite numărul de telefon"


class State(Enum):
    """These enums represent states in which a volunteer can be, from the bot's perspective"""

    EXPECTING_PHONE_NUMBER = 0
    AVAILABLE = 1
    REQUEST_SENT = 2
    REQUEST_TIME_NEGOTIATION = 3
    REQUEST_ASSIGNED = 4
    REQUEST_IN_PROGRESS = 5
    REQUEST_COMPLETED = 6
    EXPECTING_AMOUNT = 7
    EXPECTING_RECEIPT = 8
    EXPECTING_EXIT_SURVEY = 9
    EXPECTING_FURTHER_COMMENTS = 10
    EXPECTING_PROFILE_DETAILS = 11


SYMPTOMS = {
    "symptom_fever": "Febră",
    "symptom_cough": "Tuse",
    "symptom_heavybreathing": "Respirație cu dificultăți",
}


MSG_ONBOARD_NEXT_STEPS = (
    "Îți mulțumim pentru răspunsuri. În curs de *2 zile* vei fi contactat telefonic de"
    " operatorii noștri.\n\nUrmătorii pași vor fi:\n"
    "- Pregătește *buletinul de identitate*\n"
    "- Vino la **str. București 35** pentru a *semna contractul*\n"
    "- Acolo vei primi *legitimația*\n\n"
    "Toate astea *după ce te sunăm _noi_*. Acum doar așteaptă."
)

MSG_ACTIVITIES_EXPLAINED = (
    "\- _Transport_: oferirea serviciilor de transportare\n"
    "\- _Apeluri_: preluarea cererilor persoanelor care necesită ajutor, la telefon\n"
    "\- _Livrare_: procurarea produselor alimentare și a medicamentelor, atât și livrarea acestora persoanelor ce sunt autoizolați în casă din diverse motive"
)


MSG_ONBOARD_FIRST_NAME = "Cum *te cheamă*?"
MSG_ONBOARD_LAST_NAME = "Care e numele tău de *familie*?"
MSG_ONBOARD_EMAIL = "Care e adresa ta de *email*?"
MSG_ONBOARD_AVAILABILITY = (
    "Aproximativ *câte ore* pe zi ești disponibil? \(introdu un număr, ex: 2\)"
)
MSG_ONBOARD_ACTIVITIES = "*Cum* poți contribui?\n\n" + MSG_ACTIVITIES_EXPLAINED
MSG_ONBOARD_ACTIVITIES_NUDGE = "Alege cel puțin o opțiune"


# These are used as keys in the user-profile dictionary that we assemble during onboarding
PROFILE_FIRST_NAME = "first_name"
PROFILE_LAST_NAME = "last_name"
PROFILE_NICKNAME = "nickname"
PROFILE_PHONE = "phone"
PROFILE_EMAIL = "email"
PROFILE_ACTIVITIES = "activities"
PROFILE_LANGUAGE = "language"
PROFILE_AVAILABILITY = "availability"
PROFILE_CHAT_ID = "chat_id"

PROFILE_QUESTIONS = {
    PROFILE_FIRST_NAME: MSG_ONBOARD_FIRST_NAME,
    PROFILE_LAST_NAME: MSG_ONBOARD_LAST_NAME,
    PROFILE_EMAIL: MSG_ONBOARD_EMAIL,
    PROFILE_AVAILABILITY: MSG_ONBOARD_AVAILABILITY,
    PROFILE_ACTIVITIES: MSG_ONBOARD_ACTIVITIES,
}
