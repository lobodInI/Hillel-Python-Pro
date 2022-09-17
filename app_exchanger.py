import time
import uuid
import models
import database

from flask import Flask, request
from datetime import datetime
from celery_worker import task_trade


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'world is amazing'


@app.route('/currency')    # список всіх валют
def all_currency():
    database.init_db()
    list_all_currency = models.Currency.query.all()
    return [item.to_dict() for item in list_all_currency]


@app.route('/currency/<currency_name>')     # показує інформацію стосовно однієї валюти
def show_info_currency(currency_name):   # format currency name: XXX
    database.init_db()
    currency_information = models.Currency.query.filter_by(name_currency=currency_name.upper()).all()
    if not currency_information:
        return f'Дані про валюту {currency_name} не знайдено'
    else:
        return [item.to_dict() for item in currency_information]


@app.route('/currency/<currency_name>/review', methods=['GET', 'DELETE', 'POST', 'PUT'])     # дозволяє працювати з
def review_currency(currency_name):                                                    # відкуками конкретної валюти
    database.init_db()
    if request.method == 'DELETE':
        return f'DELETE a review for {currency_name} currency'

    elif request.method == 'POST':
        request_data = request.get_json()
        actual_date = datetime.now().strftime("%Y-%m-%d")
        currency_info = models.Currency.query.filter_by(name_currency=currency_name.upper(), pricing_date=actual_date).first()
        if not currency_info:
            return "Ви не можете залишити відгук, бо такої валюти в обміннику не існує"
        else:
            new_review = models.Review(id_currency=currency_info.id_currency,
                                user_rating=request_data["user_rating"],
                                review_client=request_data["review_client"],
                                date_review=actual_date)
            database.db_session.add(new_review)
            database.db_session.commit()
            return 'Data is recorded.'

    elif request.method == 'PUT':
        return f'Update a review for {currency_name} currency'

    else:
        currency_info = models.Currency.query.filter_by(name_currency=currency_name.upper()).first()
        if not currency_info:
            return 'Такої валюти немає в обміннику, або не існує'
        else:
            review_information = models.Review.query.filter_by(id_currency=currency_info.id_currency).all()
            if not review_information:
                return f'Відгуків по данній валюті {currency_name} не знайдено'
            else:
                return [item.to_dict() for item in review_information]


@app.route('/currency/trade_ratio/<currency_name1>/<currency_name2>')    # відображає співвідношення двох валют
def trade_get_ratio(currency_name1, currency_name2):
    database.init_db()
    actual_date = datetime.now().strftime("%Y-%m-%d")
    currency_name1_info = models.Currency.query.filter_by(name_currency=currency_name1.upper(),
                                                   pricing_date=actual_date).first()
    currency_name2_info = models.Currency.query.filter_by(name_currency=currency_name2.upper(),
                                                   pricing_date=actual_date).first()
    if not currency_name1_info or not currency_name2_info:
        return "Такої валютної пари не існує, валюта не оновлювалася тривалий час."
    else:
        dict_trade_ratio = {'exchenge_rate': currency_name1_info.cost_in_USD/currency_name2_info.cost_in_USD}
        return f"За одну грошову одиницю {currency_name1.upper()}, " \
               f"ви заплатите {round(dict_trade_ratio['exchenge_rate'], 2)} {currency_name2.upper()}"


# @app.route('/test1')
# def test():
#     task_obj = task1.apply_async(args=[1, 2, 30, 400])
#     return str(task_obj)


@app.post('/currency/trade/<currency_name1>/<currency_name2>')    # операція обміну однієї валюти на другу
def trade_exchange(currency_name1, currency_name2):
    database.init_db()
    user_id = int(request.get_json()['user_id'])
    am_cur_exch = request.get_json()['amount']                   # am_cur_exch = Amount of currency to exchange
    type_operation = request.get_json()['type_operation']

    uuid_transaction = uuid.uuid4()
    actual_date = datetime.now().strftime("%Y-%m-%d")
    new_transaction = models.Transactions(user_id=user_id,               # створення запису у таблиці транзакцій
                                          type_operation=type_operation,
                                          id_currency_output=0,
                                          id_currency_input=0,
                                          count_currency_spent=am_cur_exch,
                                          count_currency_received=0,
                                          commission=100,
                                          id_account_output=0,
                                          id_account_input=0,
                                          date_operation=actual_date,
                                          id_operation=uuid_transaction,
                                          status_operation='In processing')

    database.db_session.add(new_transaction)
    database.db_session.commit()
    time.sleep(15)
    task_obj = task_trade.apply_async(args=[user_id, currency_name1, currency_name2, am_cur_exch, uuid_transaction])

    return 'Request was sent'



@app.route('/user/<user_id>')
def user_info(user_id):
    database.init_db()
    account_info = models.Account.query.filter_by(user_id=user_id).all()
    if not account_info:
        return f'Дані про користувача з ID: {user_id} не знайдено'
    else:
        return [item.to_dict() for item in account_info]


@app.post('/user/transfer')    # переказ коштів
def transfer_currency_user():

    return "User currency transaction"


@app.route('/user/<user_id>/history')    # історія переказів користувача
def user_transaction_history(user_id):
    transac_user_history = models.Transactions.query.filter_by(user_id=user_id).all()
    if not transac_user_history:
        return f'Дані про користувача з ID: {user_id} не знайдено'
    else:
        return [item.to_dict() for item in transac_user_history]


@app.route('/user/<user_id>/deposit')    # шнформфція про дипозит користувача
def deposit_user(user_id):
    deposit_info = models.Deposit.query.filter_by(user_id=user_id).all()
    if not deposit_info:
        return f'Дані про дипозит користувача з ID: {user_id} не знайдено'
    else:
        return [item.to_dict() for item in deposit_info]


@app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()


if __name__ == '__main__':
    app.run(host='0.0.0.0')

