from tornado.web import RequestHandler as Handler
import tornado.escape as escape
from .auth import api_key_mixin
from .util import error_message_mixin
# from webingo.support import logger

from webingo.repos.jackpot import jackpot_repo
from webingo.wallet.denominations import get_denomination_list


class handler(Handler, api_key_mixin, error_message_mixin):

    JP_ALLOWED_FIELDS = ["id", "site_id", "denomination", "value", "min_value", "max_value"]

    async def get(self, *args, **kwargs):
        site_id = self.get_argument("site_id")

        if not site_id:
            self.fail(400, "No site_id specified in query")
            return

        if len(args) == 1:
            data = self.get_pot_data(site_id, args[0])
            if data:
                self.finish(data)
            else:
                self.fail(404, "No jackpot called "+args[0]+" found on site "+site_id)
        elif not args:
            ret = []
            pots = jackpot_repo.list_pots(site_id)

            if pots:
                for pot in pots:
                    data = self.get_pot_data(site_id, pot)
                    if data:
                        ret.append(data)

            self.finish({"jackpots":ret})
        else:
            self.fail(400, "Too many arguments")

    def get_pot_data(self, site_id, pot):
        p = jackpot_repo.get_pot(site_id, pot)
        if p:
            return {
                "id": pot,
                "site_id": site_id,
                "denomination": p.denom,
                "value": p.value(),
                "min_value": p.value_min / p.storage_int_multiplier,
                "max_value": p.value_max / p.storage_int_multiplier
            }
        else:
            return None


    async def post(self, *args, **kwargs):

        if len(args):
            self.fail(400, "No url path arguments needed for this method")
            return

        data = escape.json_decode(self.request.body)

        if (not data) or not isinstance(data, object):
            self.fail(400, "No data or wrong data in request. Send JSON object.")
            return

        for key in data:
            if key not in handler.JP_ALLOWED_FIELDS:
                self.fail(400, "Wrong key:" + key)
                return

        if "site_id" not in data or "id" not in data:
                self.fail(400, "No site_id or no id")

        site_id = data["site_id"]
        id = data["id"]

        all_in_site = jackpot_repo.list_pots(site_id)
        if(id in all_in_site):
            self.fail(400, "This pot already exists on this site")
            return

        p = jackpot_repo.get_pot(site_id, id)

        if self.update_pot(p, data):
            self.finish("Jackpot created successfully")
        else:
            self.fail(400, "Data inconsistency found")


    def update_pot(self, pot, data):

        # check for "denomination", "value", "min_value", "max_value"

        if "min_value" in data and "max_value" in data:
            if data["min_value"] > data["max_value"]:
                # logger.debug("1")
                return False

        if "min_value" in data and "max_value" not in data:
            if data["min_value"] > pot.value_max/pot.storage_int_multiplier:
                # logger.debug("2")
                return False

        if "min_value" not in data and "max_value" in data:
            if data["max_value"] < pot.value_min/pot.storage_int_multiplier:
                # logger.debug("3")
                return False

        if "denomination" in data:
            if data["denomination"] not in get_denomination_list():
                # logger.debug("4"+str(get_denomination_list()))
                return False

        # checks ended, apply changes

        if "denomination" in data:
            pot.denom = data["denomination"]

        if "min_value" in data:
            pot.value_min = (data["min_value"] * pot.storage_int_multiplier)

        if "max_value" in data:
            pot.value_max = (data["max_value"] * pot.storage_int_multiplier)

        if "value" in data:
            pot.set_value(data["value"])

        pot.save_configs()
        return True


    async def put(self, *args, **kwargs):
        self.fail(405, "UNIMPLEMENTED method")

    async def delete(self, *args, **kwargs):
        self.fail(405, "UNIMPLEMENTED method")
