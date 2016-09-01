import pytest
from peewee import *
from playhouse.test_utils import test_database
from playhouse.shortcuts import model_to_dict

from models import Account, Transaction, Category, BudgetPeriod, BudgetEntry

@pytest.fixture(scope="module")
def test_db():
    test_db = SqliteDatabase(':memory:')
    test_db.connect()
    yield test_db
    test_db.close()

def test_accounts(test_db):
    with test_database(test_db, (Account, Transaction, Category, BudgetEntry, BudgetPeriod)):
        Account.create(name='My Checking', type='checking', on_budget=True, opening_balance=0.0)
        Account.create(name='My Credit card', type='cc', on_budget=True, opening_balance=0.0)

        checking = Account.select().where(Account.name == 'My Checking').get()
        cc = Account.select().where(Account.name == 'My Credit card').get()
        Transaction.create(acct_from=cc, acct_to=checking, amount=10.0, is_transfer=True)
        Transaction.create(acct_from=cc, acct_to=checking, amount=20.0, is_transfer=True)

        ledger = list(model_to_dict(c) for c  in cc.ledger())

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
