from peewee import *

DATABASE = ':memory:'
db = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = db


class Account(BaseModel):
    acct_name = CharField(unique=True)
    acct_type = CharField()
    on_budget = BooleanField()
    opening_balance = CharField()
    opening_date = DateField()


class Transaction(BaseModel):
    is_transfer = BooleanField()
    acct_from = ForeignKeyField(Account, related_name='transactions')
    acct_to = ForeignKeyField(Account, related_name='incoming', null=True)
    payee = CharField() # Either this or ^^
    amount = DecimalField()
    date = DateField()
    indexes = (
            # create a unique on from/to/date
            (('acct_from', 'acct_to', 'date'), True),
            # create a non-unique on from/to
            (('acct_from', 'acct_to'), False),
        )

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


db.close()


# if __name__ == '__main__':
#     app.run()
