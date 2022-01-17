from .bingo import BingoEngine
from .slots import SlotsEngine

def game_engine_create( game, rgs_session, wallet ):
    
    type = game.engine
    version = 1

    if version == 1:
        if type == "bingo":
            return BingoEngine( game, rgs_session, wallet )
        elif type == "slots":
            return SlotsEngine( game, rgs_session, wallet )

    return None
