def import_transactions(filename, db):
    """Import Transactions from YNAB Register CSV file"""
    # Keep track of account names found so far
    accounts = {}
    with open(filename, newline='') as csvfile:
        txnreader = csv.reader(csvfile, delimiter=',',quotechar='"')
        next(txnreader, None)  # skip the headers
        for row in txnreader:
            acct_name = row[0]
            if acct_name not in accounts:
                acct = Account.get_or_create(name=acct_name)
                accounts[acct_name] = acct
            payee = row[4]
            is_transfer = payee.startswith('Transfer : ')
            if is_transfer:
                acct_to_name = re.search(r'^Transfer : (.*)$', payee).group(0)
                acct_to = Account.get_or_create(name=acct_to_name)
                accounts[acct_to_name] = acct_to
                payee = None
            else:
                acct_to = None

            outflow = row[9]
            inflow = row[10]
            Transaction.create(acct_from=acct_name,
                               acct_to=acct_to,
                               payee=payee,
                               amount
                               is_transfer = is_transfer
                               )
import_transactions('../mybudget-Register.CSV', db)
