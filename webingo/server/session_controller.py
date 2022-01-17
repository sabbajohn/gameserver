import datetime
import json

import webingo.repos.game as games
import webingo.repos.session_data_repo as sdata_repo
import webingo.repos.site as sites
from webingo.engines import factory as engine_factory
from webingo.jackpot.session_component import jackpot_component
from webingo.platforms import factory as platform_factory
from webingo.support import logger


class session_controller:

    def __init__(self, initdata, handler):

        logger.debug("[session_controller] initdata is:  " + json.dumps(initdata))

        self.queue = []
        self.jpcomp = jackpot_component(self)
        self.components = {self.jpcomp.name(): self.jpcomp}
        self.lobby_version = None

        self.initdata = initdata
        self.handler = handler
        # TODO: In the future, we will have several platform, it will be
        # necessary to put the platform name in the query
        # This try/catch has been used in case we do not pass the q parameter
        # in the query.
        # example: facebook/portal?q=amazoniabingo to check
        # example 2: /facebook/portal -> without query.
        # This try/catch especially because of the android and iOS app.
        try:
            if initdata["auth"]["site_id"] is not None:
                self.site_id = initdata["auth"]["site_id"]
                self.platform_name = self.initdata['platform']
            else:
                self.site_id = self.initdata['site']
                self.platform_name = self.initdata['platform']
        except Exception:
            self.site_id = self.initdata['site']
            self.platform_name = self.initdata['platform']
        self.site = sites.find_site(self.site_id)
        self.auth = initdata["auth"]
        # TODO: Make the server get the platform name throw parameters not by
        # the file in this method
        self.platform = platform_factory.create_platform_broker(self.platform_name, self.auth, self.site)
        self.needs_init = True
        # self.device_info: Dict = None

    async def finalize_init_async(self):
        if self.needs_init:
            self.needs_init = False

            logger.debug("SESSION CONTROLLER AUTH:::"+str(repr(self.auth)))
            auth = dict(self.auth, **{"id": self.auth["uid"]})
            browser = self.handler.browser
            self.registry = await self.platform.get_registry(self.site, auth, browser, self.handler.ip, self.initdata)
            if not self.registry.is_valid():
                raise Exception("[session_controller] failed to validate rgs session registry")

            self.registry.controller = self

            self.components.update(self.platform.get_components(self))
            self.user = self.platform.get_user()

            self.wallet = self.platform.wallet
            self.jpcomp.got_wallet(self.wallet)

            self.sdata = sdata_repo.get_or_create(self.site_id, self.user.get_id(), self.registry.game_configs)
            self.sdata.curr_game_name = None
            self.sdata.curr_game = None
            self.engine = None

            if "game" in self.initdata:
                self.start_game(self.initdata["game"])

    async def process_ws_message(self, data):
        # return True if overall state changed
        ret = False
        if (not self.registry) or not self.registry.is_valid():
            raise Exception("[session_controller] attempet to process message on invalid session")

        try:
            type = data['t']

            # if there is a game running
            prev_sid = ""
            if self.engine:
                prev_sid = self.engine.get_state()['id']
                if type == "action":
                    # do action
                    action_state_id = data['sid']
                    if(self.engine.get_state()['id'] == action_state_id):
                        self.engine.do_action(data['action'], data['params'], action_state_id)
                    else:
                        # state out of sync
                        # tell state changed so that it is resent
                        # TODO: maybe have more possible returns: changed/unchanged/resend
                        logger.warning("[sessioncontroller] state out of sync, resending")
                        ret = True
                elif type == "gamedefs":
                    self._queue_gamedefs()
                elif type == "gamefinish":
                    finished = False
                    if self.can_finish_game():
                        finished = self.finish_game()
                        if finished:
                            self._queue_message({"t": "gamefinish"})
                        else:
                            logger.error("[session_controller] failed to finish game")
                    else:
                        logger.info("[session_controller] can't finish game yet")
                    ret = ret or finished

                # check if state in game engine has changed
                # test if engine exists again because we could have
                # just terminated it on "gamefinish"
                if self.engine:
                    sid = self.engine.get_state()['id']
                    if sid != prev_sid:
                        ret = True
                        self.sdata.gamestate = self.get_game_state()
                        self.store_game_state()

            # handle messages that don't care if there is a game on the session
            if type == "query_state":
                # resend state
                ret = True
            elif type == "gameload" and "gameid" in data:
                started = self.start_game(data['gameid'])
                ret = ret or started
                if started:
                    self._queue_gamedefs()
            elif type == "component":
                if 'which' in data and 'message' in data:
                    which = data['which']
                    if which in self.components:
                        try:
                            req_send = await self.components[which].handle(data['message'])
                            ret = ret or req_send
                            await self.send_queued_component_messages()
                        except Exception as e:
                            logger.error(f"[session_controller] exception {e} in component handler: "+which)
                            raise
                    else:
                        logger.error("[session_controller] no controller found: "+which)
                else:
                    logger.error("[session_controller] 'component' message is incomplete: "+data)
            elif type == "userdata_update":
                if 'data' in data:
                    logger.info("[session_controller] userdata_update: "+repr(data['data']))
                    self.user.data.update(data['data'])
                    self.user.save_data()
                ret = True   # updated or not, resend session state with most recent user data
            elif type == "paid_jackpots":
                response = await self.jpcomp.get_paid_jackpots(self.registry.get_session_id())
                message = json.loads(response)
                message['t'] = "paid_jackpots"
                self._queue_message(message)
            elif type == "version":
                if data['name'] == "Amazonia Lobby":
                    self.lobby_version = {
                        "lobby": data['name'],
                        "version": data['date']
                    }
                else:
                    self.engine.game_version = {
                        "game": data['name'],
                        "version": data['date']
                    }
            elif type == "device_info":
                await self.registry.send_device_info(data)
            else:
                logger.error(f"[session_controller] Unknow message type=[{type}]")

        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[session_controller] could not process client message: {e}")
            self.die()

        return ret

    def store_game_state(self):
        self.sdata.save()

    def get_game_state(self):
        if self.engine:
            return self.engine.get_state()
        else:
            return None

    async def send_queued_component_messages(self):
        for name, comp in self.components.items():
            while comp.has_queued_messages():
                self._queue_message({'t': 'component', 'which': name, 'message': comp.pop_msg()})

    def get_current_state_message(self):
        ret = {"t": "state",
               "tstp": datetime.datetime.utcnow().timestamp()}

        gamestate = self.get_game_state()
        if gamestate:
            ret["curr_game"] = self.sdata.curr_game_name
            ret["gamestate"] = gamestate

        ret["wallet"] = self.wallet.get_state()
        ret["userdata"] = self.user.get_data_ref()

        for compname, comp in self.components.items():
            extrainfo = comp.get_session_state_extra_info()
            if extrainfo:
                ret['_'+compname] = extrainfo

        return ret

    def start_game(self, game_name):
        if self.engine:
            return False

        if not game_name:
            logger.warn("[session_controller] game_name is empty!")
            logger.warn("[session_controller] check if client specifies game name in session object")
            return False

        gameobj = games.registry.get_game(game_name)
        if gameobj:
            self.engine = engine_factory.game_engine_create(gameobj, self.registry, self.platform.wallet)
            self.sdata.gamestate = self.engine.get_state()
            self.sdata.curr_game = gameobj
            self.sdata.curr_game_name = self.sdata.curr_game.name
            self.store_game_state()
            self.engine.lobby_version = self.lobby_version

            for comp in self.components.values():
                comp.game_loaded(gameobj, self.site)

            # HACK to send user_data with every round, because the API is ????
            def add_user_data_to_round(round):
                round.player_data = self.user.get_data_ref()

            self.engine.round_process_callback = add_user_data_to_round

            return True
        else:
            logger.error("[sessioncontroller] could not find game data for: " + game_name)
            return False

    def can_finish_game(self):
        if not self.engine:
            return False
        return self.engine.can_finish_game()

    def finish_game(self):
        finished = self.engine.finish_game()
        if(finished):
            self.engine = None
            self.sdata.gamestate = None
            self.sdata.curr_game = None

            for comp in self.components.values():
                comp.game_unloaded()

        return finished

    def __del__(self):
        if self.registry:
            del self.registry
            self.registry = None

    def die(self):
        logger.error("[session_controller] terminating session")
        if self.engine:
            if self.can_finish_game():
                self.finish_game()

        self.handler.close(1001, "user session killed")

        if self.registry:
            del self.registry
            self.registry = None

    def _queue_message(self, msg):
        self.queue.append(msg)

    def get_queue_len(self):
        return len(self.queue)

    def queue_pop(self):
        if len(self.queue):
            ret = self.queue[0]
            self.queue.pop(0)
            return ret
        else:
            return None

    def _queue_gamedefs(self):
        if not self.sdata.curr_game:
            return

        msg = {"t": "gamedefs", "gamedefs": self.sdata.curr_game.gamedefs}
        for c in self.components:
            xtra = self.components[c].get_gamedefs_extra_info()
            if xtra:
                msg["_"+c] = xtra
        self._queue_message(msg)

    def checking_token_user_data(self, request_info):
        """
        This method checks if any of the openning session json

        """
        remote = request_info.headers.get("X-Real-IP") or \
            request_info.headers.get("X-Forwarded-For") or \
            request_info.remote_ip
        if self.initdata['auth']['uid'] is None or \
                self.initdata['auth']['token'] is None or \
                self.initdata['auth']['uid'] == "null" or \
                self.initdata['auth']['token'] == "null":
            logger.error(
                         f"[Session_controller] {remote} uid or token " +
                         "came empty"
                        )
            return False
        else:
            return True
    # We will implement this in the future
    #     elif self.platform_name == "facebook":
    #         logger.debug(
    #                      f"[Session_controller] {remote} checking if the"
    #                      "user's token belongs to our facebook app"
    #                     )
    #         response_validate: bool = await fb_user.validate(
    #             self.initdata['auth']['token'],
    #             self.initdata['auth']['uid'],
    #             remote
    #            )
    #         return response_validate
    #     else:
    #         return True


def get_session(data, handler):
    return session_controller(data, handler)
