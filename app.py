
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

from flask_peewee.db import Database
from peewee import SqliteDatabase

DATABASE =  {
    'name': 'example.db',
    'engine': 'peewee.SqliteDatabase',
    'check_same_thread': False,
}
DEBUG = True

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.url_map.strict_slashes = False
app.config.from_object(__name__)

db = Database(app)

from models import *
@app.route('/api/v1/accounts', methods=['GET', 'POST'])
def accounts(on_budget=True):
    if request.method == 'GET':
        res = Account.select().where(Account.on_budget==on_budget)
        output = [row.serialize(include_balance=True) for row in res]
        return jsonify(output)

@app.route('/api/v1/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'GET':
        account_id = request.args.get('account_id',0)
        try:
            res = Account.get(Account.id == account_id)
            txns = res.transactions
            output = [row.serialize() for row in txns]
        except Exception as e:
            print('No transactions found')
            print(e)
            output = []
        return jsonify(output)
