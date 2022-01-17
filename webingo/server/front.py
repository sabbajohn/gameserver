from webingo.support import logger, init_db
from webingo.platforms.factory import register_platform_http_handlers
from webingo.api.bo.v1 import register_handlers as register_bo_v1
from ..platforms.default_handler import DefaultHandler
from tornado import websocket, web, ioloop, httpserver
import ssl

from .config import serverconfig_get
from .ws_handler import ws_handler
import multiprocessing as mp

from webingo.transaction.outlet_new import OutletNew
from multiprocessing import Process

class PostableStaticFileHandler(web.StaticFileHandler):

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

class Frontend():

    def __init__( self, setup_cb ):
        
        self.setup_cb = setup_cb
        
        self.port = serverconfig_get("http_port", 8080)
        self.num_procs = serverconfig_get("num_procs", -1)
        self.debug = serverconfig_get("debug", False)
        
        if self.num_procs <= 0:
            self.num_procs = mp.cpu_count()
        
        #if self.debug: MULTIPROC HAS BECOME NOT VIABLE FOR NOW
        self.num_procs = 1
        

        self.routes = [("/session/ws", ws_handler),
                       (r"/game/(.*)", web.StaticFileHandler, {"path": "./res/games/"})]
        
        self.app = web.Application(
            self.routes,
            static_path="./static",
            static_url_prefix="/static/",
            static_handler_class=PostableStaticFileHandler,
            serve_traceback=self.debug,
            template_path="./res/templates",
            debug=self.debug,
            websocket_ping_interval=60,
            websocket_ping_timeout=180,
            default_handler_class=DefaultHandler
            )
               
        register_platform_http_handlers( self.app )
        register_bo_v1( self.app )

        ssl_ctx = None
        if(serverconfig_get("cert", "") and serverconfig_get("certkey", "")):
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(serverconfig_get("cert", ""),
                serverconfig_get("certkey", ""))

        self.server = httpserver.HTTPServer(self.app, ssl_options=ssl_ctx)
                
    def run( self ):
        self.server.bind(self.port)
        self.is_main = self.server.start(self.num_procs)
        self.setup()
        job = Process(target=OutletNew.repost_pending_rounds, name="REPOST")
        job.start()
        ioloop.IOLoop.instance().start()

    def setup(self):
        logger.debug("[frontend] process setup")
        init_db()
        if self.setup_cb:
            self.setup_cb(self.is_main)
