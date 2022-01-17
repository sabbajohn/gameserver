import logging
import os
import random
import socket

import redis
import tornado.httpclient as hc

__all__ = ["logger", "init_db", "connect_db", "db", "rgs_http_client", "notify"]


def find_config_path():
    return os.path.exists("/etc/webingo.json")


def initLog():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    if find_config_path():
        # log to file
        if not os.path.isdir('./log'):
            os.mkdir('./log')
        ch = logging.FileHandler("./log/webingo.log")
    else:
        # log to console
        ch = logging.StreamHandler()

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    log.addHandler(ch)
    return log


logger = initLog()

random.seed(os.urandom(128))

db: redis.StrictRedis = None


def connect_db():
    d = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    cname = "webingo_{}_{}".format(socket.gethostname(), os.getpid())
    d.client_setname(cname)
    logger.info('[kvdb] connected to persistency db as {}'.format(cname))
    return d


def init_db():
    global db
    db = connect_db()


def get_db():
    global db
    return db


hc.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
rgs_http_client = hc.AsyncHTTPClient()
