import tornado.web
from ..support import logger


class DefaultHandler (tornado.web.RequestHandler):
    def prepare(self):
        remote = self.request.headers.get("X-Real-IP") or \
                 self.request.headers.get("X-Forwarded-For") or \
                 self.request.remote_ip
        try:
            self.redirect("https://www.amazoniabingo.com/")
            logger.warning(f"[handler] {remote}: User tried to access " +
                           f"the relative path '{self.request.uri}' " +
                           "and has been redirected to our official website " +
                           "'https://www.amazoniabingo.com/'")
        except Exception as e:
            logger.warning(f"[handler] {remote}: Error on redirecting User." +
                           "User tried to access the relative path" +
                           f"'{self.request.uri}' " +
                           "and has been redirected to our official website " +
                           "'https://www.amazoniabingo.com/' but an error" +
                           f"occurred. Error {e}")
