from webingo.jackpot.pot import pot, POT_KEY_PREFIX
from webingo.support import get_db

class jackpot_repo:

    pot_dict = {}

    @staticmethod
    def list_pots(siteid):
        ret = []

        db = get_db()
        keybase = POT_KEY_PREFIX+siteid+"__"

        for key in db.scan_iter(keybase+"*"):
            unprefixed = key[len(keybase):]
            if "__" not in unprefixed:
                ret.append(unprefixed)

        return ret

    @staticmethod
    def get_pot(siteid, potid):
        ret = None

        dictid = siteid+"__"+potid

        if dictid in jackpot_repo.pot_dict:
            ret = jackpot_repo.pot_dict[dictid]
        else:
            ret = pot(siteid, potid)
            jackpot_repo.pot_dict[dictid] = ret
        return ret


    @staticmethod
    def delete_pot(siteid, potid):
        pass
