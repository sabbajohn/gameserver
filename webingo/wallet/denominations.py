import math

data = {
    "CRE": {"prefix": "",    "suffix": "", "integer": True,  "money_multiplier": 1,    "rgs_id":"CRE"},
    "USD":    {"prefix": "$",   "suffix": "", "integer": False, "money_multiplier": 0.01, "rgs_id":"USD"},
    "BRL":    {"prefix": "R$",  "suffix": "", "integer": False, "money_multiplier": 0.01, "rgs_id":"BRL"},
    }

default_denomination = "CRE"

def get_denomination_list():
    return data.keys()

def get_denomination(name):
    return data[name]

def get_default_denomination():
    return data[default_denomination]


def money_to_credits(denomination, amount):
    return math.floor(amount / get_denomination(denomination)["money_multiplier"])
