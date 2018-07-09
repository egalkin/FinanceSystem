from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError

from app.models import BankAccount, Transaction, Operation


class TransferForm(FlaskForm):
    recipient = StringField('Recipient', validators=[DataRequired()])
    transfer_amount = StringField('Transfer amount', validators=[DataRequired()])
    category = StringField('Category')
    submit = SubmitField('Transfer')

    def validate_recipient(self, recipient):
        user = BankAccount.query.filter_by(account_name=recipient.data).first()
        if user is None:
            raise ValidationError('Given recipient doesn\'t exist')


class SavingAccountForm(FlaskForm):
    name = StringField('Account name', validators=[DataRequired()])
    account_amount = StringField('Start amount', validators=[DataRequired()])
    submit = SubmitField('Create')


class SearchForm(FlaskForm):
    type = SelectField('Transaction type',
                       choices=[('Incomes', 'Incomes'), ('Costs', 'Costs'), ('All', 'All')])
    category = StringField('Category')
    submit = SubmitField('Get')

    def validate_category(self, category):
        transactions = Transaction.query.filter_by(category=category.data).all()
        if self.category.data != '' and transactions is None:
            raise ValidationError('No such category')


class OperationForm(FlaskForm):
    operation_type = SelectField('Operation type', choices=[('Income', 'Income'), ('Cost', 'Cost')])
    operation_amount = StringField('Operation amount', validators=[DataRequired()])
    category = StringField('Category')
    submit = SubmitField('Submit')

    def validate_category(self, category):
        operations = Operation.query.filter_by(category=category.data).all()
        if self.category.data != '' and operations is None:
            raise ValidationError('No such category')


class GlobalOperationForm(SearchForm):
    account_name = StringField('Account')

    def validate_account_name(self, account_name):
        account = BankAccount.query.filter_by(account_name=account_name.data).first()
        if self.account_name.data != '' and account is None:
            raise ValidationError('No such account')


class BankAccountForm(FlaskForm):
    account_name = StringField('Account name', validators=[DataRequired()])
    start_amount = StringField('Start amount', validators=[DataRequired()])
    submit = SubmitField('Create')

    def validate_account_name(self, account_name):
        account = BankAccount.query.filter_by(account_name=account_name.data).first()
        if account is not None:
            raise ValidationError('Account with same name already exists.')
