from webingo.support import logger
from webingo.server import front


def setup_callback(is_main):
    pass


def webingo_server_main():
    logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CUT HERE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    logger.info("[server] initializing")

    # initialize game registry
    import webingo.repos.game
    
    frontend = front.Frontend(setup_callback)
    frontend.run()
    
    
if __name__ == "__main__":
    webingo_server_main()
