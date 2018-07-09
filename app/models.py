from datetime import datetime
from app import db
from time import sleep

from app.errors import NotEnoughMoneyException


class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(64), index=True, unique=True)
    cash_amount = db.Column(db.Float, index=True)
    transactions = db.relationship('Transaction', backref='parent_account', lazy='dynamic')
    saving_accounts = db.relationship('SavingAccount', backref='parent_account', lazy='dynamic')
    operations = db.relationship('Operation', backref='parent_account', lazy='dynamic')

    def __init__(self, account_name, cash_amount=1000):
        self.account_name = account_name
        self.cash_amount = cash_amount
        do_operation(self, is_income=True, amount=0, category='Initial operation')

    def __repr__(self):
        return 'Account: {}'.format(self.account_name)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_amount = db.Column(db.Float, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    is_income = db.Column(db.Boolean, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'))
    sender_name = db.Column(db.String(64), index=True)
    recipient_name = db.Column(db.String(64), index=True)
    category = db.Column(db.String(128), index=True)

    def __repr__(self):
        if self.is_income:
            return 'Transaction to account {} : {}'.format(self.recipient_name, self.transaction_amount)
        else:
            return 'Received from account {} : +{}'.format(self.sender_name, self.transaction_amount)


class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_amount = db.Column(db.Float, index=True)
    account_amount_before_operation = db.Column(db.Float, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    is_income = db.Column(db.Boolean, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'))
    category = db.Column(db.String, index=True)

    def __repr__(self):
        if self.is_income:
            return '{} : +{}'.format(self.category, self.operation_amount)
        else:
            return '{} : {}'.format(self.category, self.operation_amount)


class SavingAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_amount = db.Column(db.Float, index=True)
    account_name = db.Column(db.String(128), index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'))
    raise_percent = db.Column(db.Integer, index=True)

    def raise_amount(self):
        self.account_amount *= 1.0 + (1 / self.raise_percent)

    def __init__(self, account_amount, account_name, parent_account, raise_percent=10):
        self.account_amount = account_amount
        self.account_name = account_name
        self.parent_account = parent_account
        self.raise_percent = raise_percent

    def __repr__(self):
        return '{} : {:.3f}'.format(self.account_name, self.account_amount)


def do_transaction(sender: BankAccount, recipient: BankAccount, amount: float, category: str = 'Default') -> None:
    if sender.cash_amount < amount:
        raise NotEnoughMoneyException()
    sender.cash_amount -= amount
    recipient.cash_amount += amount
    transaction = Transaction(transaction_amount=-amount, is_income=True, parent_account=sender,
                              sender_name=sender.account_name,
                              recipient_name=recipient.account_name, category=category)
    received = Transaction(transaction_amount=amount, is_income=False, parent_account=recipient,
                           sender_name=sender.account_name,
                           recipient_name=recipient.account_name, category=category)
    db.session.add(transaction)
    db.session.add(received)
    db.session.commit()


def do_operation(account: BankAccount, is_income: bool, amount: float, category: str = 'Default') -> None:
    if not is_income and account.cash_amount < amount:
        raise NotEnoughMoneyException()
    account.cash_amount = account.cash_amount + amount if is_income else account.cash_amount - amount
    operation = Operation(operation_amount=amount if is_income else -amount, category=category, is_income=is_income,
                          account_amount_before_operation=account.cash_amount,
                          parent_account=account)
    db.session.add(operation)
    db.session.commit()


def raise_saving_account(account_id):
    while True:
        cur_account = SavingAccount.query.filter_by(id=account_id).first()
        if cur_account is None:
            break
        cur_account.raise_amount()
        db.session.commit()
        print(cur_account)
        sleep(10)


def raise_saving_accounts(client_id):
    while True:
        cur_user = BankAccount.query.filter_by(id=client_id).first()
        if cur_user is None:
            break
        accounts = BankAccount.query.filter_by(id=client_id).first().saving_accounts.all()
        for account in accounts:
            account.raise_amount()
            db.session.commit()
            print(account)
        sleep(10)
