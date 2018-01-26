import calendar
import datetime
from peewee import SqliteDatabase

from models import Account, Transaction, Category, BudgetPeriod, BudgetEntry

DATABASE =  {
    'name': 'example.db',
    # 'engine': 'peewee.SqliteDatabase',
    'check_same_thread': False,
}

db = SqliteDatabase(DATABASE['name'])

db.connect()
db.create_tables([Account, Transaction, Category, BudgetPeriod, BudgetEntry], safe=True)

acct = Account.create(name='My Checking', type='checking', on_budget=True, opening_balance=0.0)
acct2 = Account.create(name='My Credit card', type='cc', on_budget=True, opening_balance=0.0)

checking = Account.select().where(Account.name == 'My Checking').get()
cc = Account.select().where(Account.name == 'My Credit card').get()

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
