from webingo.server.config import serverconfig_get
from tornado.httputil import HTTPServerRequest
from webingo.support import logger

API_KEY_HEADER_NAME = "X-API-Key"
CONFIG_KEY_LIST_FIELD = "api_v1_keys"

class api_key_mixin( object ):

    def prepare( self ):
        if not self.check_api_key():
            logger.warning( "[api_key_mixin] Attempted unauthorized access to API: " + self.request.host )
            self.send_error(403)
        else:
            logger.warning( "[api_key_mixin] verified API access from: " + self.request.host )

    def check_api_key( self ):
        req : HTTPServerRequest = self.request
        if API_KEY_HEADER_NAME in req.headers and req.headers[API_KEY_HEADER_NAME] in serverconfig_get(CONFIG_KEY_LIST_FIELD):
            return True

        # busted!!!
        return False
