from flask_peewee.rest import RestAPI, RestResource

from app import app
from models import *


class AccountResource(RestResource):
    exclude = ('on_budget')

api = RestAPI(app)
api.register(Account, AccountResource)
