"""Constants used throughout the code, mainly strings"""

from enum import Enum

VERSION = "0.4.2"  # follow SemVer conventions: https://semver.org/
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
MSG_PHONE_QUERY = "Te rog să ne transmiți numărul de telefon, pentru a finaliza înregistrarea."
MSG_ANOTHER_ASSIGNEE = "Altcineva merge acolo. Te anunțăm când apar noi cereri"
MSG_REQUEST_CANCELED = "Cererea de ajutor a fost anulată."
MSG_LET_ME_KNOW = "Anunță-mă când te-ai pornit"
MSG_LET_ME_KNOW_ARRIVE = "Anunță-mă când e gata"
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


SYMPTOMS = {
    "symptom_fever": "Febră",
    "symptom_cough": "Tuse",
    "symptom_heavybreathing": "Respirație cu dificultăți",
}
