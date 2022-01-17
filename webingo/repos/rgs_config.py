from webingo.server.config import serverconfig_get

DEFAULT_RGS_BASE = "http://rgsapi.amazoniagaming.com/rgs-api/"
DEFAULT_RGS_AUTH_HEADERS = {'Authorization': 'Basic Z2FtZWFwaTpnYW1lYXBp'}

RGS_BASE: str = serverconfig_get("rgs_base", DEFAULT_RGS_BASE)
RGS_AUTH_HEADERS: object = serverconfig_get("rgs_auth", DEFAULT_RGS_AUTH_HEADERS)
