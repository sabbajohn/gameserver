import webingo.user.profile as profile
from webingo.server.config import serverconfig_get
from tornado.httpclient import AsyncHTTPClient, HTTPResponse
import webingo.platforms.facebook.appinfo as appinfo
import json
from webingo.support import logger

class fb_user(profile.user_profile):

    @staticmethod
    def prepare(user, token):
        user.token = token
    # TODO: We will implement this in the future
    @staticmethod
    async def validate(user_token: str, user_uid: str, ip: str):
        """
        This static method checks if the user's facebook token is valid.
        In this way, we can check if the token is a fake one coming from
        the client side.
        """

        appTokenRequest: AsyncHTTPClient = AsyncHTTPClient()
        appTokenResponse: HTTPResponse = await appTokenRequest.\
            fetch("https://graph.facebook.com/debug_token?input_token=" +
                  f"{user_token}&access_token={appinfo.get_app_token()}")
        # TODO validate app token somewhere else
        # TODO validate user token, maybe generate longer-term token as seen here:
        # https://developers.facebook.com/docs/facebook-login/access-tokens/#apptokens

        # check out this API call right here:
        # GET graph.facebook.com/debug_token?
        #               input_token={token-to-inspect}
        #               &access_token={app-token-or-admin-token}
        # 05/19/2021 - Documentation followed for this implementation:
        # https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow#checktoken
        appTokenResponse_json = json.loads(appTokenResponse.body)
        try:
            if appTokenResponse_json['data']['user_id'] == user_uid:
                logger.debug(f"[User/fb_user] {ip} User_id belongs to our " +
                             "facebook app"
                             f"{json.dumps(appTokenResponse_json, indent=4)}")
                return True
            else:
                logger.debug(f"[User/fb_user] {ip} User_id does not belongs " +
                             "to our facebook app "
                             f"{json.dumps(appTokenResponse_json, indent=4)}")
                return False
        except Exception:
            import traceback
            traceback.print_exc()
            logger.error(f"[User/fb_user] {ip} Something went wrong, " +
                         "check the 'message' key for more details " +
                         f"{json.dumps(appTokenResponse_json, indent=4)}")
            return False
