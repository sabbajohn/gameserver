import tornado.httpclient as httpclient
from webingo.support import rgs_http_client, logger
import json
import string

from .rgs_config import RGS_BASE as RGS_BASE
from .rgs_config import RGS_AUTH_HEADERS as RGS_AUTH_HEADERS

class wallet_registry():

    GET_BALANCE_ENDPOINT = "get-player-balance"

    # transaction types
    TX_BONUS = 1    # won a bonus, usually via social cassino mechanics
    TX_CREDIT = 2   # bought some credits, to be used by the facebook purchase api impl

    # transaction endpoints by type
    TX_BONUS_ENDPOINT = "create-bonus-movement"
    TX_CREDIT_ENDPOINT = "create-purchase-credit-movement"
    TX_FB_PAYMENT_ENDPOINT = "confirm-payment-request"

    # subtypes for bonus transactions
    # this values comes from wallet_movement_type on the backoffice
    TX_BONUS_WELCOME = 4
    TX_BONUS_DAILY = 5
    TX_BONUS_LEVEL_UP = 11
    TX_BONUS_AD_COINS = 14   # admob rewarded video

    @staticmethod
    async def get(session_id, denom_rgs_id):

        req_url = "{}{}/{}/{}".format(RGS_BASE, wallet_registry.GET_BALANCE_ENDPOINT, session_id, denom_rgs_id)
        req = httpclient.HTTPRequest(req_url, "GET", headers=dict(RGS_AUTH_HEADERS))

        try:
            repl: httpclient.HTTPResponse = await rgs_http_client.fetch(req)
            data = json.loads(repl.body.decode())
            return data

        except httpclient.HTTPError as err:
            logger.error("[wallet_registry] get: request to rgs failed with: " + str(err))
            logger.info(err.response.body)
            return {
                "wallet_id": -1,
                "balance": 0,
                "currency": "CRE"
            }


    @staticmethod
    async def post_round(session_id, round):
        req_url = RGS_BASE + "create-round" + "/" + str(session_id)

        # post_body_obj = round.to_json_object()
        post_body_obj = round

        req = httpclient.HTTPRequest(req_url, "POST",
                                            headers=dict(RGS_AUTH_HEADERS, **{"Content-Type":"application/json"}),
                                            body=json.dumps(post_body_obj))

        repl: httpclient.HTTPResponse = await rgs_http_client.fetch(req)
        #logger.info( repl )
        # return json.loads(repl.body.decode())
        return repl

    @staticmethod
    async def post_transaction(session_id, tx_type, tx_subtype, value, denom_rgs_id, descr):

        session_id = str(session_id)

        req_url = RGS_BASE
        post_body_obj = {
                "currency": denom_rgs_id,
                "value": int(value),
                "description": descr if descr else "(no description)"
            }

        if tx_type == wallet_registry.TX_BONUS:
            req_url += wallet_registry.TX_BONUS_ENDPOINT + "/" + session_id
            post_body_obj["bonus_type"] = tx_subtype
        elif tx_type == wallet_registry.TX_CREDIT:
            req_url += wallet_registry.TX_CREDIT_ENDPOINT + "/" + session_id


        req = httpclient.HTTPRequest(req_url, "POST",
                                          headers=dict(RGS_AUTH_HEADERS, **{"Content-Type":"application/json"}),
                                          body=json.dumps(post_body_obj))

        try:
            repl: httpclient.HTTPResponse = await rgs_http_client.fetch(req)
            data = json.loads(repl.body.decode())
            return data

        except httpclient.HTTPError as err:
            logger.error("[wallet_registry] post_transaction: request to rgs failed with: " + str(err))
            logger.info(err.response.body)

    @staticmethod
    async def post_fb_purchase( session_id, purchase_data ):
        session_id = str(session_id)

        req_url = RGS_BASE + wallet_registry.TX_FB_PAYMENT_ENDPOINT + "/" + session_id
        post_body_obj = purchase_data
        post_body_obj['quantity_credits'] = str(int(purchase_data['product_id'].strip(string.ascii_letters)))

        req = httpclient.HTTPRequest(req_url, "POST",
                                          headers=dict(RGS_AUTH_HEADERS, **{"Content-Type":"application/json"}),
                                          body=json.dumps(post_body_obj))

        try:
            repl: httpclient.HTTPResponse = await rgs_http_client.fetch(req)
            data = json.loads(repl.body.decode())
            return data

        except httpclient.HTTPError as err:
            logger.error("[wallet_registry] post_transaction: request to rgs failed with: " + str(err))
            logger.info(err.response.body)
