import json
import os
from webingo.support import logger


class game:

    def __init__(self, path):

        self.path = path

        manifest = path + "/manifest.json"

        if not os.path.exists(manifest):
            raise FileNotFoundError(f'File manifest.json not found at {path}')

        with open(manifest, "r") as m:
            all = str(m.read())
            mobj = json.loads(all)

            self.__dict__.update(mobj)

        if "name" not in self.__dict__ or not self.name:
            raise AttributeError("invalid name for game at " + path)

        if "version" not in self.__dict__ or not self.version:
            raise AttributeError("invalid version for game at " + path)

        if "engine" not in self.__dict__ or not self.engine:
            raise AttributeError("no engine for game at " + path)

        if "profiles" not in self.__dict__ or not self.profiles:
            raise AttributeError("no profiles for game at " + path)

        if "tech" not in self.__dict__ or not self.tech:
            raise AttributeError("no tech specified for game at " + path)

        if "extra" not in self.__dict__ or not isinstance(self.extra, object):
            self.extra = {}

        if "gamedefs" not in self.__dict__ or not isinstance(self.gamedefs, object):
            self.gamedefs = {}

        if "betcontrol" not in self.gamedefs:
            try:
                with open("res/{}_betcontrol_default.json".format(self.engine), "r") as bc:
                    self.gamedefs["betcontrol"] = json.load(bc)
            except Exception as e:
                logger.log("[game] resource: no betcontrol information on gamedefs nor on a default config file")
                logger.debug(f'[game] {str(e)}')


class registry_t:

    def __init__(self, gamespath):
        self.games_path = gamespath
        self.games = {}

        gamedirs = os.listdir(gamespath)

        if not gamedirs:
            logger.warn("[gameregistry] no games found!")
            return

        for gamedir in gamedirs:
            absdir = os.path.abspath(gamespath+"/"+gamedir)
            if not os.path.isdir(absdir):
                logger.debug(f'[gameregistry] {gamedir} is not a directory')
                continue
            try:
                gobj = game(absdir)
                self.games[gobj.name] = gobj
            except FileNotFoundError as e1:
                logger.error(f'[gameregistry] {gamedir} is not a valid game dir')
                logger.error(f'[gameregistry] {str(e1)}')
            except AttributeError as e2:
                logger.error(f'[gameregistry] {gamedir} has invalid game config')
                logger.error(f'[gameregistry] {str(e2)}')
            except Exception as e3:
                logger.error("[gameregistry] could not load game at " + absdir)
                logger.error(f'[gameregistry] {str(e3)}')
                import traceback
                traceback.print_exc()

        if not self.games:
            logger.warn("[gameregistry] no games loaded!")
        else:
            logger.info("[gameregistry] games available: " + ", ".join(self.games.keys()))

    def get_games_path(self):
        return self.games_path

    def get_game(self, id):
        if id not in self.games:
            return None
        return self.games[id]

    def get_game_ids(self):
        return self.games.keys()


registry = registry_t(os.path.abspath("./res/games"))
