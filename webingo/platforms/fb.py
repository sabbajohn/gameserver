import copy

import tornado.template as template
import tornado.web as web
import webingo.repos.session_registry as registry
from webingo.repos.user import user_repo
from webingo.support import logger
from webingo.user.profile import user_profile

from .base import PlatformBase
from .facebook import social, wallet
from .facebook.user import fb_user


class PlatformFacebook( PlatformBase ):

    USER_INITIAL_DATA = { "first_time": True }

    def __init__(self, auth_data, site):
        self.auth_data = auth_data
        self.wallet = None

        uid = auth_data["uid"]
        auth_token = auth_data["token"]
        initial_info = auth_data["userinfo"]
        initial_data = PlatformFacebook.USER_INITIAL_DATA
        self.user = None

        if user_repo.has_user(site.id, uid):
            logger.info(f"[fb] found user {uid} at {site.id}")
            self.user = user_repo.get_user(site.id, uid)
            fb_user.prepare(self.user, auth_token)
        else:
            logger.info(f"[fb] creating user {uid} at {site.id}")
            self.user = user_profile(uid, site.id, copy.copy(initial_info), copy.copy(initial_data), True)
            fb_user.prepare(self.user, auth_token)

    def name(self):
        return "facebook"

    def get_components( self, controller ):
        soc = social.fb_social( controller, self.user, self.wallet )
        return { soc.name(): soc }

    def validate_session(self):
        return True

    def lock_session(self):
        return True

    def get_user(self):
        return self.user

    async def get_registry(self, site, user_data, browser, ip_addr,
                           mobile_app
                           ):
        self.session_registry = registry.session_registry(site, user_data,
                                                          browser, ip_addr,
                                                          mobile_app
                                                          )
        await self.session_registry.request_id()

        self.wallet = wallet.fb_wallet(self.session_registry.get_session_id())
        await self.wallet.init_async()

        return self.session_registry


# this handles access to the games list, or main portal
class PortalFacebook( web.RequestHandler ):

    def initialize(self):
        pass

    def post(self, *args, **kwargs):
        return self.get( *args, **kwargs )

    def get(self, *args, **kwargs):

        self.render("iframe.html")

    @staticmethod
    def register( app: web.Application ):
        app.add_handlers( r'.*', [(r'/facebook/portal', PortalFacebook)] )

