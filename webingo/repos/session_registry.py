import json

import tornado.httpclient as httpclient
from webingo.support import logger, rgs_http_client

from .rgs_config import RGS_AUTH_HEADERS, RGS_BASE

SESSIONS = {}


class session_registry:

    def __init__(self, site, user_data, browser, ip_addr=None, mobile_app=None):

        self.site_id = str(site.id)
        self.user_data = user_data
        self.mobile_app = mobile_app

        req_url = RGS_BASE + "start-session" + "/" + str(self.site_id)

        post_body_obj = {
            "player": {
                "id": user_data['uid'],
                "name": user_data['userinfo']['name'],
                "email": "",
                "data": {
                        "picture": ""
                    }
            }
        }

        try:
            post_body_obj['player']['data']['picture'] = user_data['userinfo']['picture']['data']['url']
        except KeyError:
            logger.info("USER HAS NO PICTURE")
            pass

        try:
            post_body_obj['player']['email'] = user_data['userinfo']['email']
        except KeyError:
            logger.info("USER HAS NO EMAIL")
            pass

        if ip_addr:
            post_body_obj["remote_ip_address"] = ip_addr

        if browser:
            post_body_obj["user_agent"] = browser

        try:
            if self.mobile_app["mobile_app"]:
                if self.mobile_app["mobile_app"] == "android":
                    post_body_obj["client_id"] = "app_android"
                else:
                    post_body_obj["client_id"] = "app_ios"
            else:
                try:
                    if self.user_data["facebook_games"]:
                        post_body_obj["client_id"] = "web_facebook"
                    else:
                        post_body_obj["client_id"] = "web_amz"
                except Exception:
                    post_body_obj["client_id"] = "web_amz"
        except Exception:
            try:
                if self.user_data["facebook_games"]:
                    post_body_obj["client_id"] = "web_facebook"
                else:
                    post_body_obj["client_id"] = "web_amz"
            except Exception:
                post_body_obj["client_id"] = "web_amz"

        self.req = httpclient.HTTPRequest(req_url, "POST",
                                          headers=dict(RGS_AUTH_HEADERS, **{"Content-Type": "application/json"}),
                                          body=json.dumps(post_body_obj))
        self.valid = False
        self.controller = None
        self.game_names = []    # lists all games made available to the session
        self.game_id_map = {}   # maps game names to rgs integer ids
        self.game_configs = {}  # "params" object from rgs, game configuration goes here

    async def request_id(self):
        try:
            repl: httpclient.HTTPResponse = await rgs_http_client.fetch(self.req)
            self.data = json.loads(repl.body)['session']
            logger.info(json.dumps(self.data, indent=True))

            self._parse_game_configurations()
            self.valid = True

            sid = self.get_session_id()
            logger.info(f"[session_registry] adding registry entry for session {sid}, site '{self.site_id}'")
            SESSIONS[self.local_key()] = self

        except httpclient.HTTPError as err:
            logger.error("[session_registry] request to rgs failed with: " + str(err))
            logger.info(err.response.body)

    def __del__(self):
        sid = self.get_session_id()
        logger.info(f"[session_registry] deleting registry entry for session {sid}, site '{self.site_id}'")
        SESSIONS.pop(self.local_key(), None)

    def is_valid(self):
        return self.valid

    def get_platform(self):
        if not self.valid:
            return ""

        return self.data["site"]["platform"]

    def get_session_id(self):
        if not self.valid:
            return ""

        return self.data["id"]

    def _parse_game_configurations(self):
        gamelist = self.data["site"]["games"]

        for game in gamelist:
            id_num = game["id"]
            name: str = game["name"]

            str_id_from_name = name.lower().replace(" ", "_")

            logger.info("GAME in site configuration, id={}, name={}, strid={}".format(id_num, name, str_id_from_name))

            self.game_names.append(str_id_from_name)
            self.game_id_map[str_id_from_name] = game["id"]
            self.game_configs[str_id_from_name] = game["params"]

    def local_key(self):
        return session_registry.mkkey(self.site_id, self.get_session_id())

    async def send_device_info(self, info):
        req_url: str = RGS_BASE + "update-session-info/" + str(self.get_session_id())
        header = dict(RGS_AUTH_HEADERS, **{"Content-Type": "application/json"})
        post_body_obj = info
        if 'data' in info:  # old way, used by outdated clients, kept for compatibility reasons
            info['user_agent'] = info['data']
            del info['data']
        if 't' in post_body_obj:
            del post_body_obj['t']  # remove type key from dictionary
        logger.debug(f"Sending device_info to backoffice. Device_info = {post_body_obj}")
        try:
            req = httpclient.HTTPRequest(req_url, "POST", headers=header, body=json.dumps(post_body_obj))
            await rgs_http_client.fetch(req)
        except Exception as e:
            logger.error(f"It was not possible to send this device_info to the backoffice, error {e}")

    @staticmethod
    def mkkey(site, sid):
        return f"{site}__{sid}"

    @staticmethod
    def kill(key):  # or session obj

        session = None

        if isinstance(key, session_registry):
            session = key
        elif key in SESSIONS:
            session = SESSIONS[key]

        if session:
            logger.info(f"[session_registry] killing session with key {session.local_key()}")
            if session.controller:
                session.controller.die()
                # session object should be deleted by the session controller on a kill or end of a session
                # del session
            else:
                logger.warn(f"[session_registry] kill: session {key} has no controller")
        else:
            logger.warn(f"[session_registry] kill: could not find session {key}")

    @staticmethod
    def find_by_uid(site, uid):
        for skey in SESSIONS:
            s = SESSIONS[skey]
            if s.user_data['uid'] == uid and s.site_id == site:
                return s
        keys = list(SESSIONS.keys())
        logger.warn(f"[session_registry] find_by_uid: not found {(site, uid)}, keys are {keys}")
        return None

    # TODO move round posting here in the future?
