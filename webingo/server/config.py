import json, os
from webingo.support import logger

CONFIG_DEFAULTS = {
    "session-expiry": 172800    # 2 DAYS
    }


serverconfig = None
SYSTEM_CONFIG_PATH = "/etc/webingo.json"

def find_config_path():
    if os.path.exists(SYSTEM_CONFIG_PATH):
        return SYSTEM_CONFIG_PATH
    else:
        return "./config.json"

def load():
    global serverconfig
    logger.info("[config] load")
    try:
        with open(find_config_path(), "r") as f:
            serverconfig = json.load(f)
    except:
        logger.warning("[config] could not load config, using empty default")
        serverconfig = {}
                

def save():
    global serverconfig
    logger.info("[config] save")
    try:
        with open(find_config_path(), "r") as f:
            serverconfig = json.load(f)
    except:
        logger.error("[config] failed to save server configuration")


def serverconfig_get(key, default=None):
    global serverconfig
    
    if not serverconfig:
        load()
        
    if key not in serverconfig:
        if (not default) and key in CONFIG_DEFAULTS:
            serverconfig[key] = CONFIG_DEFAULTS[key]
        else:
            serverconfig[key] = default
        
    return serverconfig[key]


def serverconfig_set( key, value ):
    global serverconfig
    if not serverconfig:
        load()
    serverconfig[key] = value
