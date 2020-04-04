VERSION = "0.0.1"  # follow SemVer conventions: https://semver.org/
URL = "code4md.com"

STATE_EXPECTING_FEEDBACK = 0
STATE_GOT_FEEDBACK = 1
STATE_EXPECTING_REPLY = 2
STATE_GOT_REPLY = 3

# Messages used in various phases of interaction
MSG_HELP = "Încearcă comanda /vreausaajut"
MSG_ABOUT = f"Ajubot v{VERSION}, {URL}"
MSG_STANDBY = "Mulțumesc! Te vom alerta când apar cereri noi."
MSG_PHONE_QUERY = "Te rog să ne transmiți numărul de telefon, pentru a finaliza înregistrarea."

# Button labels
BTN_GET_PHONE = "Trimite numărul de telefon"
