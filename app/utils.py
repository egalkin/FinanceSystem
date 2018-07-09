from app.models import BankAccount


def search_function(is_operations, type, category, account_name):
    account = BankAccount.query.filter_by(account_name=account_name).first()
    search_list = account.operations.all() if is_operations else account.transactions.all()
    if type == 'Incomes':
        return list(filter(
            lambda el: el.category == category if category != 'Default' else lambda
                el: el,
            list(
                filter(lambda el: el.is_income if is_operations else not el.is_income, search_list))))
    elif type == 'Costs':
        return list(filter(
            lambda el: el.category == category if category != 'Default' else lambda
                el: el,
            list(
                filter(lambda el: not el.is_income if is_operations else el.is_income, search_list))))
    else:
        return list(filter(
            lambda el: el.category == category if category != 'Default' else lambda
                el: el,
            search_list))


def check_account_existence(account_name):
    account = BankAccount.query.filter_by(account_name=account_name).first()
    if account is None:
        return False
