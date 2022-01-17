from webingo.support import logger
import datetime, copy, functools,json
import uuid

def build_transaction( type, subtype, amount, description, data = {} ):
        return {"type": str(int(type)), "sub_type": str(subtype), "value": int(amount), "descr": description, "data": data}


class round():

    TYPE_BET = 1
    TYPE_PAYOUT = 2

    @staticmethod
    def get_game_rgs_int( game_id, session_registry ):
        if game_id in session_registry.game_configs:
            return int(session_registry.game_id_map[game_id])

        return -1

    def __init__(self, game_id_rgs_int, wallet, is_demo = True, extra_data={}):
        self.transactions = []
        self.unique_id = str(uuid.uuid4().hex)
        self.delta = 0
        self.game_id = game_id_rgs_int
        self.denomination_rgs = wallet.denom_data["rgs_id"]
        self.is_demo = is_demo
        self.extra_data = extra_data
        self.start_date = datetime.datetime.now().isoformat().replace('.','+')

        self.lobby_version = None
        self.game_version = None

        self.wallet = wallet
        wallet.set_round(self)
        self._needs_finalize = True

    def add_transaction( self, transaction ):
        self.transactions.append(transaction)
        self._calc_delta()
        if self.wallet:
            self.wallet.notify_round_tx(transaction)

    def to_json_object(self):
        self._calc_delta()
        bets = list(filter(lambda t: int(t["type"]) == round.TYPE_BET, self.transactions))
        bet_total = 0
        for bet in bets:
            bet_total += bet["value"]

        wins = list(filter(lambda t: int(t["type"]) == round.TYPE_PAYOUT, self.transactions))
        win_total = 0
        for win in wins:
            win_total += win["value"]

        # make a copy of the transaction data and remove private transaction data fields
        txs = copy.copy(self.transactions)
        for tx in txs:
            for key in tx.keys():
                if key.startswith("_"):
                    tx.pop(key)

        ret = {
            "round_unique_id": self.unique_id,
            "round_date": datetime.datetime.now().isoformat().replace('.','+'),
            "round_start_date": self.start_date,
            "game_id": self.game_id,
            "currency": self.denomination_rgs,
            "lang": "pt-BR",
            "total_bets": bet_total,
            "total_natural_wins": self.extra_data.pop('total_natural_wins'),
            "total_wins": win_total,
            "fl_is_demo": "true" if self.is_demo else "false",
            "data": json.dumps(self.extra_data),
            "transactions": txs,
            "lobby_version": self.lobby_version,
            "game_version": self.game_version
        }
        if hasattr(self, "player_data"):
            ret["player_data"] = json.dumps(self.player_data)

        return ret

    def _calc_delta(self):
        self.delta = 0
        for tx in self.transactions:
            mul = 1 if int(tx["type"]) == round.TYPE_PAYOUT else -1
            toadd = mul * int(tx["value"])
            self.delta += toadd

    def get_curr_delta(self):
        return self.delta

    def on_finalize(self):
        if not self.wallet.round() or self.wallet.round() != self:
            raise ValueError("[round] not registered with wallet in the first place. session_id = " + self.wallet.session_id)
        else:
            self.wallet.set_round( None, self.delta )
            self._needs_finalize = False

    def needs_finalize(self):
        return self._needs_finalize
