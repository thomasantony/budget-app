import datetime
import calendar
from peewee import *
from playhouse.shortcuts import *
from decimal import Decimal
from flask_peewee.utils import get_dictionary_from_model

from app import db

# class db.Model(db.Model):
#     """Base class for all models"""
#     class Meta:
#         database = db


class Account(db.Model):
    name = CharField(unique=True)
    type = CharField()
    on_budget = BooleanField()
    opening_balance = DecimalField()
    opening_date = DateField(default=datetime.datetime.now, formats=['%Y-%m-%d'])

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

    @property
    def serialize(self):
        print('serialize yo ass')
        data = {
            'id': self.id,
            'name': str(self.name).strip(),
            'type': str(self.type).strip(),
            'on_budget': str(self.on_budget).strip(),
            'opening_balance': str(self.opening_balance).strip(),
            'opening_date': str(self.opening_date)
        }

        return data

    import json
    def to_json(self):
        print('foobaaaar')
        data = {
            'id': self.id,
            'name': str(self.name).strip(),
            'type': str(self.type).strip(),
            'on_budget': str(self.on_budget).strip(),
            'opening_balance': str(self.opening_balance).strip(),
            'opening_date': str(self.opening_date)
        }

        print(json.dumps(data))
        return json.dumps(data)


    def __str__(self):
        print('repr yo ass')
        return "{}, {}, {}, {}, {}".format(
            self.id,
            self.name,
            self.type,
            str(self.opening_balance),
            self.opening_date
        )


class Category(db.Model):
    """Model for a budget category"""
    name = CharField()
    parent = ForeignKeyField('self', null=True, related_name = 'children')

    def get_master_categories(self):
        """Returns categories with no parent."""
        return Category.select().where(parent == None)

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'name': str(self.name).strip(),
            'parent': str(self.parent_id).strip(),
        }

        return data

    def __repr__(self):
        return "{}, {}, {}".format(
            self.id,
            self.name,
            self.parent_id,
        )

class Transaction(db.Model):
    acct_from = ForeignKeyField(Account, related_name='outgoing')
    is_transfer = BooleanField(default=False)
    acct_to = ForeignKeyField(Account, related_name='incoming', null=True)
    category = ForeignKeyField(Category, related_name='transactions', null=True)
    payee = CharField(null=True) # Either this or ^^
    memo = CharField(null=True)
    is_cleared = BooleanField(default=False)
    amount = DecimalField()
    date = DateField(default=datetime.datetime.now)

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'acct_from': self.acct_from_id,
            'is_transfer': self.is_transfer,
            'acct_to': self.acct_to_id,
            'category': self.category_id,
            'payee': str(self.payee).strip(),
            'memo': str(self.memo).strip(),
            'is_cleared': self.is_cleared,
            'amount': str(self.amount),
            'date': str(self.date)
        }

        return data


class BudgetPeriod(db.Model):
    name = CharField()          # e.g. August 2016
    start_date = DateField()    # Denotes teh starting date of period
    num_days = IntegerField()   # Number of days in the budget period

    def get_budget(self):
        """
        Retrieves budget entries for all categories for current period
        with outflows and balances
        """
        txns = (BudgetEntry.select(BudgetEntry, fn.SUM(Transaction.amount).alias('outflows'), Category)
                          .join(Category)
                          .where(Transaction.date.between(
                                      self.start_date,
                                      self.start_date
                                      + datetime.timedelta(days = self.num_days)))
                          .group_by(Category)
                          .join(Transaction)
                          )

        return [{'category': t.category.name, 'outflows': t.outflows,
                'budgeted': t.budgeted, 'balance': t.budgeted + t.outflows}
                for t in txns]

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'name': self.name,
            'start_date': (self.start_date),
            'num_days': self.num_days,
        }

        return data


class BudgetEntry(db.Model):
    """One entry in the budget for a period"""
    period = ForeignKeyField(BudgetPeriod, related_name = 'entries')
    category = ForeignKeyField(Category)
    budgeted = DecimalField()

    def get_full_entry(self):
        """Computes outflows and balance for entry based on transactions."""
        total = self.category.transactions \
                    .select(fn.SUM(Transaction.amount).alias('outflows')) \
                    .where(
                     Transaction.date.between(
                      self.period.start_date,
                      self.period.start_date
                      + datetime.timedelta(days = self.period.num_days)
                     )).get()
        return {'category': self.category.name, 'budgeted': self.budgeted,
                'outflows': total.outflows,
                'balance': self.budgeted + total.outflows}

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'period': self.period_id,
            'category': self.category_id,
            'budgeted': str(self.budgeted)
        }

        return data

def create_test_data():
    acct = Account.create(name='PEFCU Checking', type='checking', on_budget=True, opening_balance=0.0)
    acct2 = Account.create(name='PEFCU Visa', type='cc', on_budget=True, opening_balance=0.0)

    txns = []
    txns.append(Transaction.create(acct_from=acct2, acct_to=acct, amount=10.0, is_transfer=True))
    txns.append(Transaction.create(acct_from=acct2, acct_to=acct, amount=20.0, is_transfer=True))

    cat0 = Category.create(name='Everyday Expenses', parent=None)
    rent = Category.create(name='Rent', parent=cat0)
    groceries = Category.create(name='Groceries', parent=cat0)

    today = datetime.date.today()
    budgetPeriod = BudgetPeriod.create(
                    name='August 2016',
                    start_date = today.replace(day=1),
                    num_days = calendar.monthrange(today.year, today.month)[1]
                   )
    budgetEntry1 = BudgetEntry.create(period=budgetPeriod, category=rent, budgeted=535.0)
    budgetEntry2 = BudgetEntry.create(period=budgetPeriod, category=groceries, budgeted=200.0)

    txns.append(Transaction.create(acct_from=acct,
                                    category=rent,
                                    amount=-525.0,
                                    is_transfer=False,
                                    payee = 'Landlord')
                )
    txns.append(Transaction.create(acct_from=acct2,
                                    category=groceries,
                                    amount=-25.0,
                                    is_transfer=False,
                                    payee = 'Supermarket')
                )
# if __name__ == '__main__':
#     db.connect()
#     db.create_tables([Account, Transaction, Category, BudgetPeriod, BudgetEntry])
#     print('Created tables '+str(db.get_tables()))
#     create_test_data()
#
#     print(budgetPeriod.get_budget())
#     db.close()
