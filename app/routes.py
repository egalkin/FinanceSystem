from threading import Thread
import pygal
from flask import render_template, redirect, url_for
from forex_python.converter import CurrencyRates

from app.errors import NotEnoughMoneyException
from app.forms import TransferForm, SavingAccountForm, \
    SearchForm, BankAccountForm, OperationForm, GlobalOperationForm
from app.models import BankAccount, do_transaction, SavingAccount, \
    do_operation, raise_saving_accounts

from app import app, db
from app.utils import search_function, check_account_existence


@app.route('/')
@app.route('/index')
def index():
    c = CurrencyRates()
    return render_template('index.html', usd=c.get_rate('USD', 'RUB'), eur=c.get_rate('EUR', 'RUB'))


@app.route('/profile')
def profile():
    accounts = BankAccount.query.all()
    return render_template('profile.html', accounts=accounts)


@app.route('/new_account', methods=['GET', 'POST'])
def new_account():
    form = BankAccountForm()
    if form.validate_on_submit():
        account = BankAccount(account_name=form.account_name.data, account_currency=form.account_currency.data,
                              cash_amount=float(form.start_amount.data))
        db.session.add(account)
        db.session.commit()
        t = Thread(target=raise_saving_accounts, args=(account.id,))
        t.start()
        return redirect(url_for('profile'))
    return render_template('new_bank_account.html', form=form)


@app.route('/profile/<account_name>', methods=['GET', 'POST'])
def bank_account(account_name):
    if check_account_existence(account_name) is False:
        return render_template('account_not_found.html', account_name=account_name)
    account = BankAccount.query.filter_by(account_name=account_name).first()
    operation_form = OperationForm()
    if operation_form.validate_on_submit():
        try:
            do_operation(account, is_income=True if operation_form.operation_type.data == 'Income' else False,
                         amount=float(operation_form.operation_amount.data),
                         category='Default' if operation_form.category.data == '' else operation_form.category.data)
            redirect(url_for('profile'))
        except NotEnoughMoneyException:
            return render_template('not_enough_money.html', err_info='to do operation', account=account)

    return render_template('account_view.html', account=account, form=operation_form)


@app.route('/profile/<account_name>/transfer', methods=['GET', 'POST'])
def transfer(account_name):
    if check_account_existence(account_name) is False:
        return render_template('account_not_found.html', account_name=account_name)
    account = BankAccount.query.filter_by(account_name=account_name).first()
    transfer_form = TransferForm()
    if transfer_form.validate_on_submit():
        try:
            recipient_account = BankAccount.query.filter_by(account_name=transfer_form.recipient.data).first()
            do_transaction(sender=account, recipient=recipient_account, amount=int(transfer_form.transfer_amount.data),
                           category='Default' if transfer_form.category.data == '' else transfer_form.category.data)
            redirect(url_for('profile'))
        except NotEnoughMoneyException:
            return render_template('not_enough_money.html', err_info='to do transaction', account=account)
    return render_template('transfer_page.html', account=account, form=transfer_form)


@app.route('/profile/<account_name>/transactions', methods=['GET', 'POST'])
def transactions(account_name):
    if check_account_existence(account_name) is False:
        return render_template('account_not_found.html', account_name=account_name)
    account = BankAccount.query.filter_by(account_name=account_name).first()
    form = SearchForm()
    if form.validate_on_submit():
        type = form.type.data
        category = 'Default' if form.category.data == '' else form.category.data
        return render_template('search_result_list.html', type=type, category=category,
                               list=search_function(is_operations=False, account_name=account_name, type=type,
                                                    category=category), account=account)
    return render_template('search_page.html', form=form, account=account)


@app.route('/profile/<account_name>/operations', methods=['GET', 'POST'])
def operations(account_name):
    if check_account_existence(account_name) is False:
        return render_template('account_not_found.html', account_name=account_name)
    account = BankAccount.query.filter_by(account_name=account_name).first()
    form = SearchForm()
    if form.validate_on_submit():
        type = form.type.data
        category = 'Default' if form.category.data == '' else form.category.data
        return render_template('search_result_list.html', type=type, category=category,
                               list=search_function(is_operations=True, account_name=account_name, type=type,
                                                    category=category), account=account)
    return render_template('search_page.html', form=form, account=account)


@app.route('/profile/<account_name>/delete')
def delete(account_name):
    if check_account_existence(account_name) is False:
        return render_template('account_not_found.html', account_name=account_name)
    account = BankAccount.query.filter_by(account_name=account_name).first()
    for transaction in account.transactions.all():
        db.session.delete(transaction)
    for saving_account in account.saving_accounts.all():
        db.session.delete(saving_account)
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/profile/<account_name>/saving_accounts')
def saving_accounts(account_name):
    if check_account_existence(account_name) is False:
        return render_template('account_not_found.html', account_name=account_name)
    account = BankAccount.query.filter_by(account_name=account_name).first()
    saving_accounts = account.saving_accounts.all()
    return render_template('saving_accounts.html', account=account, saving_accounts=saving_accounts)


@app.route('/profile/operations', methods=['GET', 'POST'])
def global_operations():
    form = GlobalOperationForm()
    if form.validate_on_submit():
        type = form.type.data
        category = 'Default' if form.category.data == '' else form.category.data
        if form.account_name.data != '':
            return render_template('search_result_list.html', type=type, category=category,
                                   list=search_function(is_operations=True, type=type,
                                                        category=category,
                                                        account_name=form.account_name.data),
                                   account=BankAccount.query.filter_by(account_name=form.account_name.data).first())
        accounts_dict = {}
        accounts = BankAccount.query.all()
        for account in accounts:
            if account.account_name in accounts_dict:
                accounts_dict[account.account_name].append(search_function(is_operations=True, type=type,
                                                                           category=category,
                                                                           account_name=account.account_name))
            else:
                accounts_dict[account.account_name] = search_function(is_operations=True, type=type,
                                                                      category=category,
                                                                      account_name=account.account_name)
        return render_template('global_search_result_list.html', dict=accounts_dict, type=type, category=category)
    return render_template('global_search_page.html', form=form)


@app.route('/profile/<account_name>/saving_accounts/new', methods=['GET', 'POST'])
def new_saving_account(account_name):
    if check_account_existence(account_name) is False:
        return render_template('account_not_found.html', account_name=account_name)
    account = BankAccount.query.filter_by(account_name=account_name).first()
    form = SavingAccountForm()
    if form.validate_on_submit():
        if account.cash_amount < float(form.account_amount.data):
            return render_template('not_enough_money.html', err_info='to create saving account', account=account)
        account.cash_amount -= float(form.account_amount.data)
        saving_account = SavingAccount(account_name=form.name.data, account_amount=int(form.account_amount.data),
                                       parent_account=account)
        db.session.add(saving_account)
        db.session.commit()
        return redirect(url_for('saving_accounts', account_name=account.account_name))
    return render_template('new_saving_account.html', form=form, account=account)


@app.route('/profile/<account_name>/plot')
def plot(account_name):
    if check_account_existence(account_name) is False:
        return render_template('account_not_found.html', account_name=account_name)
    plot_list = BankAccount.query.filter_by(account_name=account_name).first().operations.all()
    line_chart = pygal.Line()
    line_chart.title = 'Incomes/Costs plot'
    line_chart.x_label = map(str, range(1, len(plot_list) + 1))
    line_chart.add('Trend line', list(map(lambda op: op.account_amount_before_operation, plot_list)))
    return line_chart.render_response()


if __name__ == '__main__':
    app.run()
