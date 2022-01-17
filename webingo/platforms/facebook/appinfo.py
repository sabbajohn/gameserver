from webingo.server.config import serverconfig_get


def get_app_id():
    ret = serverconfig_get("fb_app_id", "")
    if not ret:
        raise ValueError("No Facebook app id present in the configuration")
    return ret

def get_app_secret():
    ret = serverconfig_get("fb_app_secret", "")
    if not ret:
        raise ValueError("No Facebook app secret present in the configuration")


def get_app_token(use_cache=True):
    # outdated:
    # "TODO use the server<->server api to get the token, using the id and secret
    # MIND use_cache, IF THE TOKEN DOESN'T WORK IT NEEDS A REFRESH"
    # This method will return the unchangeble app_token
    ret = serverconfig_get("fb_app_token", "")
    if not ret:
        raise ValueError("No Facebook app token present in the configuration")
    return ret
