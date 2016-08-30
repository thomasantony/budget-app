from peewee import *
from playhouse.shortcuts import model_to_dict
from decimal import Decimal
import datetime
import heapq

DATABASE = ':memory:'
db = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = db


class Account(BaseModel):
    name = CharField(unique=True)
    type = CharField()
    on_budget = BooleanField()
    opening_balance = DecimalField()
    opening_date = DateField(default=datetime.datetime.now)

    def ledger(self):
        """Returns combination of all transactions and transfers"""
        txns = (Transaction.select()
                           .where(
                           (Transaction.acct_from == self)
                           | (Transaction.acct_to == self)
                           )
                           .order_by(Transaction.date))
        running_balance = Decimal(self.opening_balance)
        for t in txns:
            if t.acct_from == self:
                t.amount = -t.amount
            running_balance += Decimal(t.amount)
            t.running_balance = running_balance
            yield t

class Transaction(BaseModel):
    acct_from = ForeignKeyField(Account, related_name='outgoing')
    is_transfer = BooleanField(default=False)
    acct_to = ForeignKeyField(Account, related_name='incoming', null=True)
    payee = CharField(null=True) # Either this or ^^
    memo = CharField(null=True)
    is_cleared = BooleanField(default=False)
    amount = DecimalField()
    date = DateField(default=datetime.datetime.now)


class Category(BaseModel):
    """Model for a budget category"""
    category_name = CharField()
    parent = ForeignKeyField('self', null=True, related_name = 'children')


class BudgetPeriod(BaseModel):
    name = CharField()  # e.g. August 2016
    short_name = CharField() # e.g. 082016


class BudgetEntry(BaseModel):
    """One entry in the budget for a period"""
    period = ForeignKeyField(BudgetPeriod, related_name = 'entries')
    category = ForeignKeyField(Category)
    amt_budgeted = DecimalField()


db.connect()
db.create_tables([Account, Transaction, Category, BudgetPeriod, BudgetEntry])
print('Created tables '+str(db.get_tables()))

acct = Account.create(name='PEFCU Checking', type='checking', on_budget=True, opening_balance=0.0)
acct2 = Account.create(name='PEFCU Visa', type='cc', on_budget=True, opening_balance=0.0)

txns = []
txns.append(Transaction.create(acct_from=acct2, acct_to=acct, amount=10.0, is_transfer=True))
txns.append(Transaction.create(acct_from=acct2, acct_to=acct, amount=20.0, is_transfer=True))

for tx in acct2.ledger():
    print(tx)

db.close()


# if __name__ == '__main__':
#     app.run()
