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


# this handles access to the games list, or main portal
class FacebookWeb(web.RequestHandler):

    def initialize(self):
        pass

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, *args, **kwargs):

        base_name = "webingo-client"
        res_base = ("/static/webingo-client/")

        # template variables
        BASE_PATH = res_base+base_name
        JS_SOURCE = self.static_url("webingo-client/"+base_name+".js")
        EXECUTABLE_NAME = res_base+base_name
        MAIN_PACK = self.static_url("webingo-client/"+base_name+".pck")
        PCK_SERVER_LOCATION = "static/games-available/"
        self.render("fb_web.html",
                    BASE_PATH=BASE_PATH,
                    JS_SOURCE=JS_SOURCE,
                    EXECUTABLE_NAME=EXECUTABLE_NAME,
                    MAIN_PACK=MAIN_PACK,
                    PCK_SERVER_LOCATION=PCK_SERVER_LOCATION)

    @staticmethod
    def register(app: web.Application):
        app.add_handlers(r'.*', [
                                 (r'/facebook/web', FacebookWeb)
                                ]
                         )
