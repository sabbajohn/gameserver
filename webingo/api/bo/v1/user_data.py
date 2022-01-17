
from tornado.web import RequestHandler as Handler
import tornado.escape as escape
from .auth import api_key_mixin
from .util import error_message_mixin

from webingo.repos.user import user_repo
import copy


class handler(Handler, api_key_mixin, error_message_mixin):

    async def get(self, *args, **kwargs):
        site_id = self.get_argument("site_id")

        if not site_id:
            self.fail(400, "No site_id specified in query")
            return

        if len(args) == 1:
            user_id = args[0]
            data = self.get_user_data(site_id, user_id)
            if data:
                self.finish(data)
            else:
                self.fail(404, "No user called "+user_id+" found on site "+site_id)
        elif not args:
            self.fail(400, "Missing arguments (user_id?)")

    def get_user_data(self, site_id, user_id):
        u = user_repo.get_user(site_id, user_id)
        if u:
            return {
                "site_id": user_id,
                "user_id": site_id,
                "user_data": copy.copy(u.get_data_ref())
            }
        else:
            return None

    async def delete(self, *args, **kwargs):
        site_id = self.get_argument("site_id")

        if not site_id:
            self.fail(400, "No site_id specified in query")
            return

        if len(args) == 1:
            user_id = args[0]
            if user_repo.has_user(site_id, user_id):
                try:
                    user_repo.delete_user(site_id, user_id)
                    self.finish()
                except:
                    self.fail(500, "Error deleting user "+args[0]+" from site "+site_id)
            else:
                self.fail(404, "No user called "+args[0]+" found on site "+site_id)
        elif not args:
            self.fail(400, "Missing arguments (user_id?)")
