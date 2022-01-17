from tornado.web import Application
import webingo.api.bo.v1.jackpot
import webingo.api.bo.v1.user_data

API_BASE = r"/api/bo/v1/"

def register_handlers(app : Application):
    app.add_handlers(r".*", [(API_BASE+r"jackpot", jackpot.handler)])
    app.add_handlers(r".*", [(API_BASE+r"jackpot/([^/]*)$", jackpot.handler)])
    app.add_handlers(r".*", [(API_BASE+r"user_data/([^/]*)$", user_data.handler)])
