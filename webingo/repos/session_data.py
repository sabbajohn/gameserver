
from webingo.support import get_db
import json

class session_data():

    @staticmethod
    def get_key(site_id, user_id):
        return "SS__"+site_id+"__"+user_id

    def __init__(self, site_id, user_id, rgs_config=None):
        self.db_key = session_data.get_key(site_id, user_id)

        # this identifies this session data as unique for a session
        self.site_id = site_id
        self.user_id = user_id

        # this is constant for a session but not part of identification of course
        self.rgs_config = rgs_config

        # these are dynamic during the sesion
        self.curr_game_name = None
        self.curr_game = None
        self.gamestate = None


    def load(self):
        db = get_db()
        o = json.loads(str(db.get(self.db_key)))
        self.from_obj(o)

    def save(self):
        db = get_db()
        o = self.to_obj()
        db.set(self.db_key, json.dumps(o))

    def to_obj( self ):
        return {
                "curr_game_name": self.curr_game_name,
                "gamestate": self.gamestate,
                "rgs_config": self.rgs_config
            }

    def from_obj( self, obj ):
        self.curr_game_name = obj["curr_game_name"]
        self.gamestate = obj["gamestate"]
        self.rgs_config = obj["rgs_config"]

    def valid( self ):
        return True # TODO heuristics?
