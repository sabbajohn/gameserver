from webingo.repos.wallet_registry import wallet_registry
from webingo.transaction.round import round
from .denominations import get_denomination, get_default_denomination
from webingo.support import logger
import functools

from abc import ABC


class wallet_listener_mixin(ABC):
    def on_wallet_change(self, wallet, deltas):
        pass

    def on_round_transaction(self, tx):
        pass


def _notifies(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        value = func(*args, **kwargs)
        curr = self._capture_state()
        delta = wallet_rgs._states_delta(prev, curr)
        if delta:
            self._notify_listeners(delta)
        return value
    return wrapper


# TODO instead of a specific new_pending_round_delta, we should have a generic interface to register
#      and unregister pending credit deltas for operations that are in progress
#      FOR NOW, this only makes sense for ROUNDS, but who knows what sort of async crap the backoffice
#      may force us to deal with? :)

class wallet_rgs():

    # note to self: wallet.data uses different nomenclature than before, to use rgs info directly
    # value is "balance"
    # denomination is "currency"

    def __init__(self, session_id, denom=get_default_denomination()):
        self.session_id = session_id

        self.data = None
        self._round: round = None
        self._pending_round_delta = 0
        self.denom = denom
        self.listeners = []

        self.print_enabled = True
        self._validate_conf()

    async def init_async(self):
        await self._get_info()

    def round(self):
        return self._round

    def set_round(self, r, new_pending_round_delta=None):
        self._do_print("set_round_before")
        if (not self.round) and (not r):
            self._round = None
            return

        if self._round and r:
            raise ValueError("[wallet_rgs] a round is already attached to this wallet, unset it first")

        prev = self._capture_state()

        self._round = r
        if new_pending_round_delta is not None:
            self._pending_round_delta = new_pending_round_delta

        # curr_total = self.combined_credits()

        self._do_print("set_round_after")

        curr = self._capture_state()
        delta = wallet_rgs._states_delta(prev, curr)
        if delta:
            self._notify_listeners(delta)

    def base_credits(self):
        return int(self.data["balance"])

    def round_delta(self):
        if not self._round:
            return 0
        else:
            return self._round.get_curr_delta()

    def pending_round_delta(self):
        return self._pending_round_delta

    def combined_credits(self):
        return self.round_delta() + self.base_credits() + self.pending_round_delta()

    # wallet state to be sent together with session state
    def get_state(self):
        return {
            "credits": self.combined_credits(),
            "denom": self.denom,
            "denom_info": self.denom_data,
            "rgs": self.base_credits()
        }

    def add_listener(self, listener, immediate_notify=False):
        if not hasattr(listener, "on_wallet_change") or not callable(listener.on_wallet_change):
            raise ValueError("[wallet_rgs] this is not a wallet listener")

        if listener not in self.listeners:
            self.listeners.append(listener)

        if immediate_notify:
            listener.on_wallet_change(self)

    def remove_listener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)

    @_notifies
    def set_pending_round_delta(self, new_delta):
        prev = self._capture_state()

        self._do_print("set_round_delta_before")
        self._pending_round_delta = new_delta
        self._do_print("set_round_delta_after")

        curr = self._capture_state()
        delta = wallet_rgs._states_delta(prev, curr)
        if delta:
            self._notify_listeners(delta)

    def on_rgs_change(self, curr_rgs_data, clear_pending_round_value=False):
        prev = self._capture_state()

        if self.data:
            self._do_print("rgs_change_before")

        if self.data:
            if self.data["currency"] != curr_rgs_data["currency"]:
                raise AssertionError("[wallet_rgs] attempted to change currency of wallet, this is unsupported")

        self.data = curr_rgs_data
        if clear_pending_round_value:
            self._pending_round_delta = 0
        self._do_print("rgs_change_after")

        curr = self._capture_state()
        delta = wallet_rgs._states_delta(prev, curr)
        if delta:
            self._notify_listeners(delta)

    def _validate_conf(self):
        if not self.session_id:
            raise ValueError("[wallet_rgs] no session_id")
        if not self.denom:
            raise ValueError("[wallet_rgs] no denomination")
        else:
            self.denom_data = get_denomination(self.denom)

    async def _get_info(self):
        recv_data = await wallet_registry.get(self.session_id, self.denom)

        if recv_data:
            self.on_rgs_change(recv_data)
        else:
            logger.error("[wallet_rgs] could not get info from rgs")

    def _notify_listeners(self, deltas):
        self._do_print("notify")
        for listener in self.listeners:
            listener.on_wallet_change(self, deltas)

    def _do_print(self, func=""):
        if not self.print_enabled:
            return
        logger.debug(f"[wallet_rgs] WALLET INFO at {func}: {self._capture_state()}")

    def _capture_state(self):
        # logger.debug("[wallet_rgs] " + str(self.data))
        if not hasattr(self, "data") or not self.data:
            return None
        return {
            "combined": self.combined_credits(),
            "base":     self.base_credits(),
            "round":    self._round,
            "round_delta": self.round_delta(),
            "pending_round": self.pending_round_delta()
            }

    @staticmethod
    def _states_delta(previous: dict, current: dict):
        if not previous or not current:
            return None

        allkeys = set(list(previous.keys()) + list(current.keys()))

        ret = {}

        for key in allkeys:
            inprev = key in previous
            incurr = key in current

            if(inprev != incurr):
                prevval = previous[key] if inprev else None
                currval = current[key] if incurr else None

                ret[key] = (prevval, currval)
            else:
                if previous[key] != current[key]:
                    ret[key] = (previous[key], current[key])

        return ret if ret else None

    def notify_round_tx(self, tx):
        logger.debug("WALLET NOTIFYING ROUND TX "+repr(tx))
        for listener in self.listeners:
            listener.on_round_transaction(tx)
