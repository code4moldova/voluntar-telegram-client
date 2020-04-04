from enum import Enum

VERSION = "0.0.1"  # follow SemVer conventions: https://semver.org/
URL = "code4md.com"

# Messages used in various phases of interaction
MSG_HELP = "Încearcă comanda /vreausaajut"
MSG_ABOUT = f"Ajubot v{VERSION}, {URL}"
MSG_STANDBY = "Mulțumesc! Te vom alerta când apar cereri noi."
MSG_THANKS_NOTHANKS = "Bine, te vom alerta când apar cereri noi."
MSG_ACK_TIME = "Bine, ora %s, "
MSG_COORDINATING = "coordonez cu alți voluntari."
MSG_PHONE_QUERY = "Te rog să ne transmiți numărul de telefon, pentru a finaliza înregistrarea."
MSG_ANOTHER_ASSIGNEE = "Altcineva merge acolo. Te anunțăm când apar noi cereri"
MSG_LET_ME_KNOW = "Anunță-mă când te-ai pornit"
MSG_OTHER_REMARKS = "*Remarci* de la alți voluntari:\n"
MSG_NO_WORRIES_LATER = "Bine, nu te îngrijora, vor apărea și alte cereri în viitor"

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

MSG_REQUEST_ANNOUNCEMENT = "O persoană din *%s* are nevoie de:\n%s\nPoți ajuta?"

# Button labels
BTN_GET_PHONE = "Trimite numărul de telefon"


class State(Enum):
    EXPECTING_PHONE_NUMBER = 0
    AVAILABLE = 1
    REQUEST_SENT = 2
    REQUEST_TIME_NEGOTIATION = 3
    REQUEST_ASSIGNED = 4
    REQUEST_IN_PROGRESS = 5
    REQUEST_COMPLETED = 6
