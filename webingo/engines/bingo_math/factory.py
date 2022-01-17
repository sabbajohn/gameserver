
from .base import bingo_math_base
from .bigbingo import bigbingo_math
from webingo.support import logger


def create_bingo_math( id, gamedefs, **kwargs ):
    if id == "base":
        return bingo_math_base( gamedefs, **kwargs )
    elif id == "bigbingo":
        return bigbingo_math( gamedefs, **kwargs )

    logger.warn("[bingo_math] factory: instantiating base bingo math because id '{}' didn't match")
    return bingo_math_base( gamedefs, **kwargs )
