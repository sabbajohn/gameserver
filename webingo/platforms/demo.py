from .base import PlatformBase
from webingo.wallet.wallet_rgs import wallet_rgs
import tornado.web as web
import tornado.template as template
import webingo.repos.session_registry as registry
from webingo.user.profile import user_profile

class PlatformDemo( PlatformBase ):
    
    def __init__(self, auth_data, site):
        self.auth_data = auth_data
        self.wallet = None
        self.user = user_profile( auth_data["uid"], site.id, {'first_time': True} )

    def name(self):
        return "demo"


    async def get_registry(self, site, user_data, ip_addr):
        self.session_registry = registry.session_registry(site, user_data)
        await self.registry.request_id()

        self.wallet = wallet_rgs(self.session_registry.get_session_id())
        await self.wallet.init_async()

        return self.session_registry


    def get_user( self ):
        return self.user


# this handles access to the games list, or main portal
class PortalDemo( web.RequestHandler ):

    def initialize(self):
        pass

    def get(self, *args, **kwargs):
        self.render("demo_portal.html")

    @staticmethod
    def register( app: web.Application ):
        app.add_handlers( r'.*', [(r'/demo/portal', PortalDemo)] )


