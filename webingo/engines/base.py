import uuid

class GameEngine:

    def type(self):
        raise NotImplementedError("Engine does not define own type")
    
    def get_state(self):
        raise NotImplementedError("Unimplemented get_state")
    
    def do_action(self, action, args, stateid):
        raise NotImplementedError("Unimplemented do_action")

    def gen_state_id(self):
        return str(uuid.uuid4())

    def can_finish_game(self):
        return False
