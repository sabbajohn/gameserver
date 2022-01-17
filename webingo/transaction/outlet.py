from webingo.support import logger
import tornado.ioloop as ioloop
from webingo.repos.wallet_registry import wallet_registry
from webingo.wallet.wallet_rgs import wallet_rgs

# this is called by the event loop to actually send up the round
async def do_round_post(*args):

    wallet: wallet_rgs = args[0]
    rgs_session_id = args[1]
    round = args[2]

    data = await wallet_registry.post_round(rgs_session_id, round)
    wallet.on_rgs_change( data["balance"], True )

# we keep the implementation with the wallet registry, even if invoked globally
def commit_round( wallet, rgs_session_id, round ):
    if round.needs_finalize():
        round.on_finalize()
    ioloop.IOLoop.current().add_callback(do_round_post, wallet, rgs_session_id, round )

