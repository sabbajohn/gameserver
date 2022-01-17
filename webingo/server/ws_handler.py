import json
import datetime

from tornado import websocket
from user_agents import parse
from webingo.support import logger

from .session_controller import get_session
import datetime

class ws_handler (websocket.WebSocketHandler):
    
    def open(self, *args, **kwargs):
        self.log("connection open from "+str(self.request.remote_ip))
        self.session = None
        self.ip = self.request.remote_ip
        self.last_datetime_pong_received: datetime = None
        self.browser = ""
        try:
            temp_variable = parse(self.request.headers.get("User-Agent"))
            self.browser = {
                "pretty_string_version": str(temp_variable).replace("/", "-"),
                "is_mobile": temp_variable.is_mobile,
                "is_tablet": temp_variable.is_tablet,
                "is_touch_capable": temp_variable.is_touch_capable,
                "is_pc": temp_variable.is_pc,
                "is_bot": temp_variable.is_bot  
            }
        except:
            self.browser = "No User-Agent Information"

    async def on_message(self, data):
        # all messages have to be valid json
        src = "(null)"
        try:
            src = data if isinstance( data, str ) else data.decode()
            self.log("RECV " + src)
            o = json.loads(src)
        
            if not self.session:
                # self.log(str(o))
                await self.try_open_session(o)
            else:
                state_changed = await self.session.process_ws_message(o)

                while self.session.get_queue_len():
                    outmsg = self.session.queue_pop()
                    await self.send_message(outmsg)

                if state_changed:
                    await self.send_session_state()
        
        except json.JSONDecodeError:
            self.log( "invalid message received at "+str(self) + ": " + src)
        
    async def try_open_session(self, data):
        try:
            s = get_session(data, self)
            self.session = s
            checking_token_user_data = self.session.checking_token_user_data(
                self.request)
            if checking_token_user_data:
                await self.session.finalize_init_async()
            else:
                # TODO: implement closing session with on_close method.
                self.log("Closing Websocket")
                self.session = None
                self.close()
        except:
            import traceback
            traceback.print_exc()
            self.log("could not create game session, closing")
            self.session = None
            self.close()

        await self.send_session_state()

    async def send_session_state(self):
        if self.session:
            msg = self.session.get_current_state_message()
            await self.write_message(json.dumps(msg))
            self.log("sent session state: " + json.dumps(msg) )

    async def send_message(self, outmsg):
            await self.write_message(json.dumps(outmsg))
            self.log("sent message: " + json.dumps(outmsg) )

    def on_close(self):
        if self.last_datetime_pong_received is None:
            self.log("WebSocket closed, no pong response received")
        else:
            self.log("WebSocket closed, last received pong " +
                     f"occurred on {self.last_datetime_pong_received} utc")

    def check_origin(self, origin):
        return True     # accept all origins (we are a server)

    def on_pong(self, data: bytes):
        self.last_datetime_pong_received = datetime.datetime.utcnow()
        # self.log("RECV pong")

    def log(self, str):
        remote = self.request.headers.get("X-Real-IP") or \
                self.request.headers.get("X-Forwarded-For") or \
                self.request.remote_ip
        logger.debug("[handler] " + remote + ": " + str )
