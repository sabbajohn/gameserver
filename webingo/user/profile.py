from webingo.support import logger, get_db
import json
import copy

DEBUG_PRINT=True

class user_profile():

    def __init__(self, id, site_id, initial_info = None, initial_data = None, force_update_info = False):
        self.id = id
        self.site_id = site_id

        self.db_key = user_profile.mk_db_key(id, site_id)
        self.db_key_data = user_profile.mk_db_key_data(id, site_id)
        db = get_db()
        self.db = db

        if (not db.exists(self.db_key)):
            logger.info(f"[user_profile] key {self.db_key} NOT FOUND in db, new user")
            if initial_info:
                logger.info(f"[user_profile] initial info is {initial_info}")
                self.info = copy.copy(initial_info)
                self.save_info()
            else:
                self.info = {}

            if initial_data:
                logger.info(f"[user_profile] initial data is {initial_data}")
                self.data = copy.copy(initial_data)
                self.save_data()
            else:
                self.data = {}
        else:
            logger.info(f"[user_profile] key {self.db_key} found in db, retrieving")
            if not force_update_info:
                self.info = json.loads(str(db.get(self.db_key)))
            else:
                self.info = copy.copy(initial_info)
                self.save_info()

            if (not db.exists(self.db_key_data)):
                if initial_data:
                    self.data = copy.copy(initial_data)
                    self.save_data()
                else:
                    self.data = {}
            else:
                self.data = json.loads(str(db.get(self.db_key_data)))

    def get_id(self):
        return self.id

    def get_info_ref(self):
        return self.info

    def save_info(self):
        logger.info(f"[user_profile] saving {self.db_key}")
        self.db.set(self.db_key, json.dumps(self.info))

    def get_data_ref(self):
        return self.data

    def save_data(self):
        logger.info(f"[user_profile] saving {self.db_key_data}: "+repr(self.data))
        #import traceback
        #traceback.print_stack()
        #logger.info(f"[user_profile] BEFORE: {repr(self.db.get(self.db_key_data))}")
        self.db.set(self.db_key_data, json.dumps(self.data))
        #logger.info(f"[user_profile] SAVING {self.db_key_data}: "+repr(self.data))
        #logger.info(f"[user_profile] AFTER: {repr(self.db.get(self.db_key_data))}")


    @staticmethod
    def mk_db_key(user_id, site_id):
        return "USER_" + str(site_id + "__" + str(user_id))

    @staticmethod
    def mk_db_key_data(user_id, site_id):
        return user_profile.mk_db_key(user_id, site_id) + "_DATA"

    @staticmethod
    def exists(user_id, site_id):
        key = user_profile.mk_db_key(user_id, site_id)
        logger.debug("KEY IS "+key)
        db = get_db()
        return db.exists(key)

    @staticmethod
    def delete_user_data(user_id, site_id):
        key = user_profile.mk_db_key(user_id, site_id)
        keyd = user_profile.mk_db_key_data(user_id, site_id)
        logger.info(f"[profile] deleting user, key '{key}', data key '{keyd}'")
        db = get_db()
        if not db.delete(key):
            logger.warn("Failed to delete user main key")
        if not db.delete(keyd):
            logger.warn("Failed to delete user data key")

