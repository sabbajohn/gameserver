import webingo.wallet.denominations as denominations
import webingo.wallet.wallet_rgs as wallet_rgs

class fb_wallet(wallet_rgs.wallet_rgs):

    def __init__(self, session_id):
        super().__init__(session_id, "CRE")
