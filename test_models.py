import pytest
import datetime
import calendar
from peewee import *
from playhouse.test_utils import test_database
from playhouse.shortcuts import model_to_dict

from models import *

@pytest.fixture(scope="module")
def test_db():
    test_db = SqliteDatabase(':memory:')
    test_db.connect()
    yield test_db
    test_db.close()

def test_accounts(test_db):
    with test_database(test_db, (Account, Transaction, Transfer, Category, BudgetEntry, BudgetPeriod)):
        acct = Account.create(name='My Checking', type='checking', on_budget=True, opening_balance=0.0)
        acct2 = Account.create(name='My Credit card', type='cc', on_budget=True, opening_balance=0.0)

        checking = Account.select().where(Account.name == 'My Checking').get()
        cc = Account.select().where(Account.name == 'My Credit card').get()

        assert cc.balance == -0.0
        assert checking.balance == +0.0

        t1_a = Transaction.create(
                            acct=cc,
                            amount=-10.0,
                            is_transfer=True,
                            prev_balance=cc.opening_balance,
                            current_balance=-10.0)
        t1_b = Transaction.create(acct=checking,
                            amount=+10.0,
                            is_transfer=True,
                            prev_balance=checking.opening_balance,
                            current_balance=+10.0)

        Transfer.create(from_txn=t1_a, to_txn=t1_b)

        assert cc.balance == -10.0
        assert checking.balance == +10.0


        t2_a = Transaction.create(acct=cc,
                                  amount=-20.0,
                                  is_transfer=True,
                                  prev_balance=cc.balance,
                                  current_balance=-30.0)
        t2_b = Transaction.create(acct=checking,
                                  amount=+20.0,
                                  is_transfer=True,
                                  prev_balance=checking.balance,
                                  current_balance=+30.0)
        Transfer.create(from_txn=t2_a, to_txn=t2_b)
        assert cc.balance == -30.0
        assert checking.balance == +30.0

        ledger = list(model_to_dict(c) for c  in cc.ledger())
        print(ledger)
        #
        # cat0 = Category.create(name='Everyday Expenses', parent=None)
        # rent = Category.create(name='Rent', parent=cat0)
        # groceries = Category.create(name='Groceries', parent=cat0)
        #
        # today = datetime.date.today()
        # budgetPeriod = BudgetPeriod.create(
        #                 name='August 2016',
        #                 start_date = today.replace(day=1),
        #                 num_days = calendar.monthrange(today.year, today.month)[1]
        #                )
        # budgetEntry1 = BudgetEntry.create(period=budgetPeriod, category=rent, budgeted=535.0)
        # budgetEntry2 = BudgetEntry.create(period=budgetPeriod, category=groceries, budgeted=200.0)
        #
        # Transaction.create(acct_from=acct,
        #                     category=rent,
        #                     amount=-525.0,
        #                     is_transfer=False,
        #                     payee = 'Landlord')
        # Transaction.create(acct_from=acct2,
        #                     category=groceries,
        #                     amount=-25.0,
        #                     is_transfer=False,
        #                     payee = 'Supermarket')
        #
        # assert budgetEntry1.get_full_entry() == {'budgeted': 535.0, 'outflows': -525.0,
        #         'balance': 10.0, 'category': 'Rent'}
        # assert budgetPeriod.get_budget() == [{'category': 'Rent', 'outflows': -525, 'budgeted': 535, 'balance': 10}, {'category': 'Groceries', 'outflows': -25, 'budgeted': 200, 'balance': 175}]
