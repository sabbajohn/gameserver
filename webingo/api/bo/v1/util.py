from webingo.server.config import serverconfig_get
from tornado.httputil import HTTPServerRequest
from webingo.support import logger

class error_message_mixin( object ):

    def fail( self, errno, reason="Unknown Error" ):
        self.set_status(errno)
        self.finish({"reason": reason})
