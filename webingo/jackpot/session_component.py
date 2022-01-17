from webingo.server.session_component import session_component
from webingo.repos.jackpot import jackpot_repo
from webingo.repos.game import registry as game_registry
from webingo.support import logger, rgs_http_client
import webingo.jackpot.pot as pot
import webingo.jackpot.config as jpconfig
from webingo.wallet.wallet_rgs import wallet_listener_mixin
from webingo.transaction.round import round
import functools
import json
from ..repos.rgs_config import RGS_BASE as RGS_BASE
from ..repos.rgs_config import RGS_AUTH_HEADERS as RGS_AUTH_HEADERS
import tornado.httpclient as httpclient

# TODO this should be programmed to send jackpot updates,
#      check out what can be done using timers or whatever
#      on tornado.ioloop, or the underlying py3 asyncio loop
class jackpot_subscription():

    def __init__(self, jackpot_name, controller):
        self.pot_name = jackpot_name
        self.pot = jackpot_repo.get_pot(controller.site_id, jackpot_name)
        self.controller = controller

    def get_now(self):
        # logger.debug("WATCHED "+repr(self.pot))
        return self.pot.value()



class jackpot_component( session_component, wallet_listener_mixin ):

    def __init__(self, controller):
        super().__init__("jackpot", controller)
        self.controller = controller
        self.subscriptions = {}

        self.curr_game_jackpot_incrementer = None
        self.defaults = jpconfig.get_jackpot_defaults()

        self.inc_fraction = self.defaults["fraction"]

    def got_wallet(self, wallet):
        self.wallet = wallet
        # reimplement using new interface of round transaction adds
        # self.wallet.add_callback( lambda op, amount: self.on_wallet_op( op, amount ))

    def on_round_transaction(self, tx):
        logger.debug("JACKPOT RECV "+repr(tx))
        pot = self.curr_game_jackpot_incrementer
        if not pot:
            return
        if str(tx["type"]) == str(round.TYPE_BET):
            before = pot.value()
            delta = float(tx["value"]) * float(self.inc_fraction)
            logger.debug("INC "+repr(pot))
            pot.inc(delta)
            after = pot.value()
            logger.debug("JACKPOT BET {} -> {} ({})".format(before, after, delta))

    def game_loaded(self, game_obj, site):

        potname = ""
        potmultiplier = self.inc_fraction
        gamename = game_obj.name

        # try to fund jackpot to increment in server definition
        for gameconfig in self.controller.registry.game_configs:
            if "game" in gameconfig and gameconfig["game"] == gamename:
                if "jackpot" in gameconfig["configs"]:
                    potname = gameconfig["configs"]["jackpot"]
                if "jackpot_fraction" in gameconfig["configs"]:
                    potmultiplier = gameconfig["configs"]["jackpot_fraction"]

        # try to find a pot name in local game config
        if not potname:
            local_game_conf = game_registry.get_game(gamename)
            if local_game_conf:
                if "jackpot_links" in local_game_conf.extra:
                    jl = local_game_conf.extra["jackpot_links"]
                    if jl and isinstance(jl, list):
                        potname = jl[0]["name"]
                        potmultiplier = float(jl[0]["fraction"]) if "fraction" in jl[0] else potmultiplier

        if potname:
            if self.curr_game_jackpot_incrementer:
                self.game_unloaded()


            inc_target = jackpot_repo.get_pot(self.controller.site_id, potname)
            self.curr_game_jackpot_incrementer = inc_target
            self.inc_fraction = potmultiplier
            self.wallet.add_listener(self)
            logger.info("[jackpot_component] incrementing jackpot "+potname+" "+str(potmultiplier))

        else:
            logger.warning("[jackpot_component] no target jackpot in game configuration")

        # tell engine to work atop this jackpot right here
        if self.curr_game_jackpot_incrementer:
            self.controller.engine.target_pot = self.curr_game_jackpot_incrementer

    def game_unloaded(self):
        self.wallet.remove_listener(self)
        del self.curr_game_jackpot_incrementer
        self.curr_game_jackpot_incrementer = None

    def get_session_state_extra_info(self):
        jackpot_values = {}

        for subname, sub in self.subscriptions.items():
            jackpot_values[subname] = sub.get_now()

        logger.info("WATCHED JACKPOTS: " + str(jackpot_values))
        return jackpot_values

    async def handle(self, msg):
        if 'what' in msg:
            if msg['what'] == 'subscribe' and ('to' in msg) and msg['to']:
                target = msg['to']
                if target not in self.subscriptions:
                    sub = jackpot_subscription( target, self.controller )
                    self.subscriptions[target] = sub
                    logger.debug("JACKPOT SUBBED TO " + target)
                    return True
            elif msg['what'] == 'unsubscribe_all':
                del self.subscriptions
                self.subscriptions = {}
            else:
                logger.warning("JACKPOT MALFORMED MESSAGE: " + str(msg))
        else:
            logger.warning("JACKPOT NO MESSAGE TYPE: " + str(msg))


    async def get_paid_jackpots(self, session_id):
        '''
        Return a list of all (max 30?) recent paid jackpots.
            Parameters:
                session_id (String): Current session ID.
            Returns:
                response (dict): Dictionary containing the list of paid jackpots.
        '''
        url = RGS_BASE + "get-paid-jackpots" + "/" + str(session_id)
        request = httpclient.HTTPRequest(url, "GET", headers=dict(RGS_AUTH_HEADERS, **{"Content-Type": "application/json"}))
        response: httpclient.HTTPResponse = await rgs_http_client.fetch(request)
        return response.body
