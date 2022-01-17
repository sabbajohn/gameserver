
from tornado.web import RequestHandler as Handler
import tornado.escape as escape
from .auth import api_key_mixin
from .util import error_message_mixin

from webingo.repos.user import user_repo
import copy


class handler(Handler, api_key_mixin, error_message_mixin):

    # TODO implement this endpoint
    async def post(self, *args, **kwargs):

        FIELDS = ["wallet_id", "currency", "balance"]

        site_id = self.get_argument("site_id")

        if not site_id:
            self.fail(400, "No site_id specified in query")
            return

        data = escape.json_decode(self.request.body)

        if (not data) or not isinstance(data, object):
            self.fail(400, "No data or wrong data in request. Send JSON object.")
            return

        for key in data:
            if key not in FIELDS:
                self.fail(400, "Wrong key:" + key)
                return

        for f in FIELDS:
            if f not in data:
                self.fail(400, "Missing notification field:" + f)
                return

        #TODO DO SOMETHING HERE

        self.finish()
        return

