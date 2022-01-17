from webingo.support import get_db
from webingo.repos.session_data import session_data


def data_exists( site_id, user_id ) -> bool:
    return get_db().exists( session_data.get_key(site_id, user_id) )


def data_valid( site_id, user_id ) -> bool:
    d = session_data(site_id, user_id)
    d.load()
    return d.valid()


def get_or_create( site_id, user_id, rgs_config, can_create=True ) -> session_data:
    if data_exists( site_id, user_id ):
        d = session_data(site_id, user_id, rgs_config)
        d.load()
        if d.valid():
            return d

    if can_create:
        d = session_data( site_id, user_id, rgs_config )
        return d
    else:
        return None
