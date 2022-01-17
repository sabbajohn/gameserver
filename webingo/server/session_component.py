from webingo.support import logger

class session_component:

    def __init__( self, component_name, controller ):
        self.component_name = component_name
        self.controller = controller
        self.msg_queue = []
        pass

    def name( self ):
        return self.component_name

    async def handle( self, msg ):
        logger.warning("[session_component] " + self.component_name + ": UNIMPLEMENTED MESSAGE HANDLER")
        pass

    def game_loaded( self, game_obj, site ):
        pass

    def game_unloaded( self ):
        pass

    def get_session_state_extra_info(self):
        return None

    def get_gamedefs_extra_info(self):
        return None

    def queue_message( self, msg ):
        self.msg_queue.append( msg )
        pass

    def has_queued_messages( self ):
        return len(self.msg_queue) > 0

    def pop_msg( self ):
        if not self.has_queued_messages():
            return None

        ret = self.msg_queue[0]
        self.msg_queue = self.msg_queue[1:]
        return ret
