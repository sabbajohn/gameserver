from webingo.user.profile import user_profile
from webingo.support import get_db, logger
from webingo.repos.session_registry import session_registry

class user_repo:

    @staticmethod
    def get_user(siteid, userid):
        logger.info(f"[user_repo] get_user: site {siteid} uid {userid}")
        if user_profile.exists( userid, siteid ):
            p = user_profile( userid, siteid )
            logger.info(f"[user_repo] get_user: FOUND user for site {siteid} uid {userid}: {str(p)}")
            return p
        else:
            logger.info(f"[user_repo] get_user: NOT FOUND user for site {siteid} uid {userid}")
            return None

    @staticmethod
    def has_user(siteid, userid):
        ret = user_profile.exists( userid, siteid )
        logger.info(f"[user_repo] has_user: site {siteid} uid {userid}: {ret}")
        return ret

    @staticmethod
    def delete_user(siteid, userid):
        # TODO if we introduce a global registry of users in memory, take care of checking if any are in use now, and fail
        logger.info(f"[user_repo] delete_user: site {siteid} uid {userid}")
        session = session_registry.find_by_uid(siteid, userid)
        if session:
            logger.info(f"[user_repo] found user session, killing")
            try:
                session_registry.kill(session)
            except:
                logger.info(f"[user_repo] exception killing user session")
                import traceback
                traceback.print_exc()
        else:
            logger.info(f"[user_repo] no user session found for {(siteid, userid)}")

        try:
            user_profile.delete_user_data( userid, siteid )
        except:
            logger.info(f"[user_repo] exception deleting user db data")
            import traceback
            traceback.print_exc()
