
from flask import Flask, render_template
from flask_peewee.db import Database
from peewee import SqliteDatabase


DATABASE =  {
    'name': 'example.db',
    'engine': 'peewee.SqliteDatabase',
    'check_same_thread': False,
}
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

db = Database(app)


#
# import datetime
# import calendar
# import peewee
# from playhouse.shortcuts import *
# from decimal import Decimal
# from models import *

# db = SqliteDatabase()
#
# db.create_tables([Account, Transaction, Category, BudgetPeriod, BudgetEntry], safe=True)
#
#
# @app.route('/api/v1/accounts', methods=['GET', 'POST'])
# def account_endpoint():
#     if request.method == 'GET':
#         per_page = 10
#         data = [acct.serialize for acct in Account.select()]
#
#         if data:
#             res = jsonify({
#                 'accounts': data,
#             })
#             res.status_code = 200
#         else:
#             # if no results are found.
#             output = {
#                 "error": "No results found. Check url again",
#                 "url": request.url,
#             }
#             res = jsonify(output)
#             res.status_code = 404
#         return res
#
#     elif request.method == 'POST':  # post request
#         row = Account.create(**request.json)
#         query = Account.select().where(
#             Account.name == row.name
#         )
#         data = [i.serialize for i in query]
#         res = jsonify({
#             'city': data,
#             'meta': {'page_url': request.url}
#             })
#         res.status_code = 201
#         return res
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/hello')
# def hello():
#     return render_template('hello.html')
#
# @app.errorhandler(404)
# def not_found(exc):
#     return Response('<h3>Not found</h3>'), 404
