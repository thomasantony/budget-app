import datetime
import calendar
from peewee import *
from playhouse.shortcuts import model_to_dict
from decimal import Decimal

from app import db

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


class Category(BaseModel):
    """Model for a budget category"""
    name = CharField()
    parent = ForeignKeyField('self', null=True, related_name = 'children')

    def get_master_categories(self):
        """Returns categories with no parent."""
        return Category.select().where(parent == None)


class Transaction(BaseModel):
    acct_from = ForeignKeyField(Account, related_name='outgoing')
    is_transfer = BooleanField(default=False)
    acct_to = ForeignKeyField(Account, related_name='incoming', null=True)
    category = ForeignKeyField(Category, related_name='transactions', null=True)
    payee = CharField(null=True) # Either this or ^^
    memo = CharField(null=True)
    is_cleared = BooleanField(default=False)
    amount = DecimalField()
    date = DateField(default=datetime.datetime.now)


class BudgetPeriod(BaseModel):
    name = CharField()          # e.g. August 2016
    start_date = DateField()    # Denotes teh starting date of period
    num_days = IntegerField()   # Number of days in the budget period
    def get_budget(self):
        """
        Retrieves budget entries for all categories for current period
        with outflows and balances
        """
        pass

class BudgetEntry(BaseModel):
    """One entry in the budget for a period"""
    period = ForeignKeyField(BudgetPeriod, related_name = 'entries')
    category = ForeignKeyField(Category)
    amount = DecimalField()

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
        return {'budgeted': self.amount, 'outflows': total.outflows,
                'balance': self.amount + total.outflows}




if __name__ == '__main__':
    db.connect()
    db.create_tables([Account, Transaction, Category, BudgetPeriod, BudgetEntry])
    print('Created tables '+str(db.get_tables()))

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
    budgetEntry1 = BudgetEntry.create(period=budgetPeriod, category=rent, amount=535.0)
    budgetEntry2 = BudgetEntry.create(period=budgetPeriod, category=groceries, amount=200.0)

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
    print([e.category.name+': $'+str(e.amount) for e in budgetPeriod.entries])
    print(budgetEntry1.get_full_entry())
    db.close()
