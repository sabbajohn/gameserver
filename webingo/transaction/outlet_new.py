import os
from webingo.support import logger
import tornado.ioloop as ioloop
from webingo.repos.wallet_registry import wallet_registry
from webingo.wallet.wallet_rgs import wallet_rgs
from webingo.support import get_db
from datetime import datetime
from time import sleep
from webingo.support.notify import Notify
import json
import requests
from webingo.repos.rgs_config import RGS_BASE as RGS_BASE
from webingo.repos.rgs_config import RGS_AUTH_HEADERS as RGS_AUTH_HEADERS


class OutletNew():
    
    @staticmethod
    def get_key():
        return "PENDING_ROUNDS"

    async def do_round_post(*args):
        wallet: wallet_rgs = args[0]
        rgs_session_id = args[1]
        round = args[2].to_json_object()

        data = await wallet_registry.post_round(rgs_session_id, round)
        if(data.code == 200):
            body = json.loads(data.body.decode())
            wallet.on_rgs_change( body["balance"], True )
        else:
            # TODO: Create a routine to notify the Dev team when an erro occurs and Log it
            logger.warning("[ROUND] Fail to POST round {}. Code {}".format(round["round_unique_id"], data.code))
            OutletNew.pending_round(rgs_session_id, round)
            OutletNew.AlertDevTeam(data.code, round)

    def loadKeys():
        db = get_db()
        key_p =OutletNew.get_key()
        Keys = db.keys("{}_*".format(key_p))
        return Keys
    
    def DelKey(key):
        db = get_db()
        D = db.delete(key)
        # return D

    def load(key):
        db = get_db()
        o = db.get(key)
        if (o):
            data = json.loads(str(o))
            
            return data
        else:
            return None

    def save(data):
        db = get_db()
        key = OutletNew.get_key()+"_" + data['round_unique_id']
        db.set(key, json.dumps(data))

    def pending_round(session_id, round):
        round["session_id"]= session_id
        round["last_try"]= str(datetime.now())
        round["number_of_tries"]= 1
        OutletNew.save(round)

    # we keep the implementation with the wallet registry, even if invoked globally
    def commit_round(wallet, rgs_session_id, round ):
        if round.needs_finalize():
            round.on_finalize()
        ioloop.IOLoop.current().add_callback(OutletNew.do_round_post, wallet, rgs_session_id, round )

    def repost_pending_rounds():
        while True:
            keys = OutletNew.loadKeys()
            for key in keys:
                round = OutletNew.load(key)
                if round:
                    response = OutletNew.OldSchoolPost(round)
                    if response.status_code == 200:
                        OutletNew.DelKey(key)
                    else:
                        round["last_try"] = str(datetime.now())
                        round['number_of_tries'] += 1
                        logger.warning("[ROUND] Fail on try to  POST round {} again. Code {}. Try n° {}".format(round["round_unique_id"], response.status_code, round["number_of_tries"]))
                        OutletNew.save(round)
                        # TODO log the unsuccessful tries
            sleep(60)

    def OldSchoolPost(request):
        req_url = RGS_BASE + "create-round" + "/" + str(request['session_id'])
        post_body_obj = request
        response =  requests.post(req_url,  headers=dict(RGS_AUTH_HEADERS, **{"Content-Type":"application/json"}), data=json.dumps(post_body_obj))
        return response

    def AlertDevTeam(code, round):
        path = os.path.abspath("./webingo/transaction")
        email_cfg = path +"/"+ "email_on_fail_cfg.json"
        

        if not os.path.exists(email_cfg):
            raise FileNotFoundError(f'File email_on_fail_cfg.json not found at {path}')
        else:
            with open(email_cfg, "r") as c:
                data = str(c.read())
        try:
            config = json.loads(data)
        except:
            raise AttributeError("Probably not a valid json file!")
        config['subject'] = config['subject'].replace("@", str(round["round_unique_id"]))
        config['contents'] = config['contents'].replace("@code", str(code))
        config['contents'] = config['contents'].replace("@round", json.dumps(round))
        try:
            Email = Notify(Subject=config['subject'], To=config['dev_team'], body_html=config['contents'])
            Email.sendEmail()
            logger.info("[NOTIFY] The Dev team was notified. ")
        except Exception as e:
            logger.warning("[NOTIFY] Unable to notify the Dev team. {}".format(e))
