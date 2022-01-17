from webingo.support import logger
import os, json

# this resource denotes where a set of games might be installed,
# and also contains the set of configurations for every game
# stored on the backoffice


class site:
    def __init__(self, id, platform):
        self.id = id
        self.platform = platform


class site_source_local:
    def __init__(self):
        # we won't cache anything, installations are supposed to be dynamic
        self.path = os.path.abspath("./res/local_sites/")

    def find(self, id):

        filepath = self.path+"/"+str(id)+".json"

        if os.path.exists(filepath):
            with open(filepath, "r") as m:
                all = str(m.read())
                iobj = json.loads(all)

                expected_keys = ["id", "platform"]
                valid = False

                for key in expected_keys:
                    if key not in iobj:
                        logger.error("[installation_source_local] installation at "+filepath+" missing field: " + key)
                        return None

                return site( id, iobj["platform"] )

        return None



class site_source_backoffice:

    def __init__(self):
        pass
    
    # TODO: in the future... Catch site_id data throw here. Example: platform.
    def find(self, id):
        return None



source_local = site_source_local()
source_backoffice = site_source_backoffice()

def find_site(id):

    i = None

    try:
        i = source_backoffice.find(id)
    except:
        logger.error("[find_site] exception looking for remote site "+str(id))
        import traceback
        traceback.print_exc()

    if i: return i

    try:
        i = source_local.find(id)
    except:
        logger.error("[find_site] exception looking for local site "+str(id))
        import traceback
        traceback.print_exc()

    if i: return i

    logger.warn("[find_site] not found: " + id)
    return None

