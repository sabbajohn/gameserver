from webingo.server.session_component import session_component
from .wallet import fb_wallet
from webingo.repos.wallet_registry import wallet_registry
from webingo.wallet.wallet_rgs import wallet_listener_mixin
from webingo.transaction.round import round
from webingo.support import logger

import json
import warnings


class fb_social(session_component, wallet_listener_mixin):

    LEVEL_SPEND_TABLE = None
    LEVEL_SPEND_POLY = None

    def __init__(self, controller, user, wallet: fb_wallet):
        super().__init__("fb_social", controller)

        self.user = user
        self.wallet = wallet
        self.wallet.add_listener(self)

        self.user_level = user.data["soc_level"] if "soc_level" in user.data else 1
        self.user_level_progress = user.data["soc_level_prog"] if "soc_level_prog" in user.data else 0.0
        self.user_spend_total = user.data["spend_total"] if "spend_total" in user.data else 0

        # We do not use any files to get level parameters nowdays
        # if not fb_social.LEVEL_SPEND_TABLE:
        #     self.get_level_params()

        # TODO reimplement using level info from server configuration
        self.level_spend_table = [
                0,
                35000,
                100000,
                300000,
                800000,
                1700000,
                2800000,
                4100000,
                5600000,
                7200000,
                8900000,
                10900000,
                13100000,
                15500000,
                18100000,
                20900000,
                23900000,
                27100000,
                30500000,
                34100000,
                38100000,
                43035000,
                49035000,
                56035000,
                66035000,
                76035000,
                86035000,
                96035000,
                111035000,
                126035000,
                141035000,
                156035000,
                176035000,
                196035000,
                216035000,
                236035000,
                256035000,
                281035000,
                306035000,
                331035000,
                356035000,
                381035000,
                411035000,
                441035000,
                471035000,
                501035000,
                531035000,
                561035000,
                591035000,
                631035000
            ]
        self.update_user_level_info()
        self.save_user_level_info()

    def get_level_params(self):

        # first, figure out where to get info for this component
        # in our case, we get global info

        self.config = None

        with open("./res/fb_social_config.json", "r") as cfgfile:
            self.config = json.load(cfgfile)

    def on_round_transaction(self, tx):
        if str(tx["type"]) == str(round.TYPE_BET):
            amount = int(tx["value"])

            self.user_spend_total += amount
            logger.debug("USER SPEND TOTAL:" + str(self.user_spend_total))

            self.update_user_level_info()
            self.save_user_level_info()

    async def handle(self, msg):
        logger.debug("FB_SOCIAL RECEIVED MESSAGE: " + str(msg))
        if 'what' in msg:

            if msg['what'] == 'manual_buy' and ('amount' in msg) and int(msg['amount']):
                amount = int(msg['amount'])
                wallet_purchase_tx_result = await wallet_registry.post_transaction(self.controller.registry.get_session_id(),
                                                                                    wallet_registry().TX_CREDIT,
                                                                                    0,
                                                                                    amount,
                                                                                    self.wallet.denom_data["rgs_id"],
                                                                                    "Manual credit purchase")
                self.wallet.on_rgs_change(wallet_purchase_tx_result)
                warnings.warn("[fb_social] manual_buy works, for now, but purchases will be handled in-server in the future for security")
                return True
            elif msg['what'] == 'purchase' and ('data' in msg) and msg['data']:
                logger.debug("[fb_social] RECV PURCHASE: " + str(msg['data']))
                warnings.warn("[fb_social] purchasing without verification, this will not be the case in the future")
                try:
                    sid = self.controller.registry.get_session_id()
                    res = await wallet_registry.post_fb_purchase(sid, msg['data'])
                    self.wallet.on_rgs_change(res)
                    return True
                except Exception as e:
                    logger.error("[fb_social] Error: " + str(e))
                else:
                    logger.info("[fb_social] Error: " + str(res.body))
                return False
            elif msg['what'] == 'set_credits' and ('amount' in msg) and int(msg['amount']):
                # NOT TO BE USED ANYMORE
                amount = int(msg['amount'])
                # self.wallet.set_credits(amount)
                warnings.warn("[fb_social] set_credits disabled, please use other methods to influence wallet")
                return True
            elif msg['what'] == 'give_bonus' and ('amount' in msg) and int(msg['amount']) and 'type' in msg:
                # we are gonna hand out good stuff
                btype = str(msg['type'])
                amount = int(msg['amount'])

                tx_subtypes = {
                        'welcome': (wallet_registry.TX_BONUS_WELCOME, "Welcome bonus"),
                        'daily': (wallet_registry.TX_BONUS_DAILY, "Daily bonus"),
                        'level_up': (wallet_registry.TX_BONUS_LEVEL_UP, "Level up bonus"),
                        'coins': (wallet_registry.TX_BONUS_AD_COINS, "Ad Reward Coins"),
                    }
                tx_subtype = tx_subtypes[btype] if btype in tx_subtypes else tx_subtypes['daily']

                logger.debug("[fb_social] paying bonus {}, value={}".format(btype, amount))

                sid = self.controller.registry.get_session_id()
                denom = self.wallet.denom_data["rgs_id"]
                try:
                    res = await wallet_registry.post_transaction(sid, wallet_registry().TX_BONUS, tx_subtype[0], amount, denom, tx_subtype[1])
                    self.wallet.on_rgs_change(res)
                    return True
                except Exception as e:
                    logger.error("[fb_social] Error: " + str(e))
                return False
            else:
                logger.error("[fb_social] malformed message: " + str(msg))
        else:
            logger.error("[fb_social] no message type: " + str(msg))
        return False

    def update_user_level_info(self):
        spent = self.user_spend_total

        # It adds another level if the current table last index is lower than
        # the player's spent
        while True:
            level_spend_table_len = len(self.level_spend_table)

            if level_spend_table_len < 100 and \
               spent >= self.level_spend_table[-1]:
                self.level_spend_table.append(self.level_spend_table[-1] +
                                              50000000)

            elif 100 <= level_spend_table_len < 200 and \
                    spent >= self.level_spend_table[-1]:
                self.level_spend_table.append(self.level_spend_table[-1] +
                                              60000000)

            elif 200 <= level_spend_table_len < 300 and \
                    spent >= self.level_spend_table[-1]:
                self.level_spend_table.append(self.level_spend_table[-1] +
                                              80000000)

            elif 300 <= level_spend_table_len < 400 and \
                    spent >= self.level_spend_table[-1]:
                self.level_spend_table.append(self.level_spend_table[-1] +
                                              100000000)

            elif 400 <= level_spend_table_len < 500 and \
                    spent >= self.level_spend_table[-1]:
                self.level_spend_table.append(self.level_spend_table[-1] +
                                              120000000)

            elif level_spend_table_len >= 500 and \
                    spent >= self.level_spend_table[-1]:
                self.level_spend_table.append(self.level_spend_table[-1] +
                                              150000000)

            else:
                break

            # we have to scan the table and find out the current level and progress
        for i in range(len(self.level_spend_table)-1):
            idx_spend = self.level_spend_table[i]
            idx_spend_next = self.level_spend_table[i+1]

            if spent >= idx_spend and spent < idx_spend_next:
                residual = spent - idx_spend
                delta = idx_spend_next - idx_spend
                self.user_level = i + 1
                self.user_level_progress = residual / float(delta)
                break

    def save_user_level_info(self):
        self.user.data["soc_level"] = self.user_level
        self.user.data["soc_level_prog"] = self.user_level_progress
        self.user.data["spend_total"] = self.user_spend_total
        self.user.save_data()
