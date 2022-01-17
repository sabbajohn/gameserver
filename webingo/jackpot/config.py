import json

JACKPOT_DEFAULTS = None

def get_jackpot_defaults():
    global JACKPOT_DEFAULTS
    if not JACKPOT_DEFAULTS:
        with open("./res/jackpot_defaults.json", "r") as cfgfile:
            JACKPOT_DEFAULTS = json.load(cfgfile)

    return JACKPOT_DEFAULTS
