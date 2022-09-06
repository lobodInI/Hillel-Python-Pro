from flask import Flask, request
import sqlite3
from datetime import datetime
from models import db, Account, Currency, Deposit, Review, Transactions, User
import os
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STR')
db.init_app(app)
migrate = Migrate(app, db)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_data(query: str):
    # with sqlite3.connect("databases_exchanger.db") as con:
    #     con.row_factory = dict_factory
    #     cursor = con.execute(query)
    #     result = cursor.fetchall()
    #     return result
    con = sqlite3.connect("databases_exchanger.db")
    con.row_factory = dict_factory
    cursor = con.execute(query)
    result = cursor.fetchall()
    con.commit()
    con.close()
    return result


@app.route('/')
def hello_world():
    return 'world is amazing'


@app.route('/currency')    # список всіх валют
def all_currency():
    list_all_currency = Currency.query.all()
    return [item.to_dict() for item in list_all_currency]


@app.route('/currency/<currency_name>')     # показує інформацію стосовно однієї валюти
def show_info_currency(currency_name):      # format currency name: XXX
    currency_information = Currency.query.filter_by(name_currency=currency_name.upper()).all()
    if not currency_information:
        return f'Дані про валюту {currency_name} не знайдено'
    else:
        return [item.to_dict() for item in currency_information]


@app.route('/currency/<currency_name>/review', methods=['GET', 'DELETE', 'POST', 'PUT'])     # дозволяє працювати з
def review_currency(currency_name):                                                    # відкуками конкретної валюти
    if request.method == 'DELETE':
        return f'DELETE a review for {currency_name} currency'

    elif request.method == 'POST':
        request_data = request.get_json()
        actual_date = datetime.now().strftime("%Y-%m-%d")
        currency_info = Currency.query.filter_by(name_currency=currency_name.upper(), pricing_date=actual_date).first()
        if not currency_info:
            return "Ви не можете залишити відгук, бо такої валюти в обміннику не існує"
        else:
            new_review = Review(id_currency=currency_info.id_currency,
                                user_rating=request_data["user_rating"],
                                review_client=request_data["review_client"],
                                date_review=actual_date)
            db.session.add(new_review)
            db.session.commit()
            return 'Data is recorded.'

    elif request.method == 'PUT':
        return f'Update a review for {currency_name} currency'

    else:
        currency_info = Currency.query.filter_by(name_currency=currency_name.upper()).first()
        if not currency_info:
            return 'Такої валюти немає в обміннику, або не існує'
        else:
            review_information = Review.query.filter_by(id_currency=currency_info.id_currency).all()
            if not review_information:
                return f'Відгуків по данній валюті {currency_name} не знайдено'
            else:
                return [item.to_dict() for item in review_information]


@app.route('/currency/trade_ratio/<currency_name1>/<currency_name2>')    # відображає співвідношення двох валют
def trade_get_ratio(currency_name1, currency_name2):
    actual_date = datetime.now().strftime("%Y-%m-%d")
    currency_name1_info = Currency.query.filter_by(name_currency=currency_name1.upper(),
                                                   pricing_date=actual_date).first()
    currency_name2_info = Currency.query.filter_by(name_currency=currency_name2.upper(),
                                                   pricing_date=actual_date).first()
    if not currency_name1_info or not currency_name2_info:
        return "Такої валютної пари не існує, валюта не оновлювалася тривалий час."
    else:
        dict_trade_ratio = {'exchenge_rate': currency_name1_info.cost_in_USD/currency_name2_info.cost_in_USD}
        return f"За одну грошову одиницю {currency_name1.upper()}, " \
               f"ви заплатите {round(dict_trade_ratio['exchenge_rate'], 2)} {currency_name2.upper()}"


@app.post('/currency/trade/<currency_name1>/<currency_name2>')    # операція обміну однієї валюти на другу
def trade_exchange(currency_name1, currency_name2):
    user_id = int(request.get_json()['user_id'])
    am_cur_exch = request.get_json()['amount']                   # am_cur_exch = Amount of currency to exchange
    actual_date = datetime.now().strftime("%Y-%m-%d")

    # загальна актуальна інформація по валюту яку продає юзер
    info_currency1 = Currency.query.filter_by(name_currency=currency_name1.upper(), pricing_date=actual_date).first()
    # загальна актуальна інформація по валюту яку купує юзер
    info_currency2 = Currency.query.filter_by(name_currency=currency_name2.upper(), pricing_date=actual_date).first()
    # звертаємось до данних в Account до логіну юзера
    account_user_info1 = Account.query.filter_by(user_id=user_id, id_currency=info_currency1.id_currency).first()
    account_user_info2 = Account.query.filter_by(user_id=user_id, id_currency=info_currency2.id_currency).first()
    # сума у валюті, яку хоче купити юзер
    required_amount = round((info_currency1.cost_in_USD/info_currency2.cost_in_USD) * am_cur_exch, 2)

    # перевірка наявності валюти у юзера та перевірка чи є необхідна сума у обміннику
    if account_user_info1.balance >= am_cur_exch and required_amount <= info_currency2.available_quantity:
        if not account_user_info2:
            new_account = Account(user_id=user_id, id_currency=info_currency2.id_currency, balance=0)
            db.session.add(new_account)
            db.session.commit()
            account_user_info2 = Account.query.filter_by(user_id=user_id,
                                                         id_currency=info_currency2.id_currency).first()
        # оновлення доступної кількості валюти у одміннику, яку продає юзер
        # не створюємо нову строку бо в теорії в нас кожен день оновлюєтться та сворюється строка валюти
        info_currency1.available_quantity = info_currency1.available_quantity + am_cur_exch
        # оновлення доступної кількості валюти у одміннику, яку купує юзер
        info_currency2.available_quantity = info_currency2.available_quantity - required_amount
        # оновлення кількості валюти у юзера яку продав
        account_user_info1.balance = account_user_info1.balance - am_cur_exch
        # оновлення кількості валюти у юзера яку купив
        account_user_info2.balance = account_user_info2.balance + required_amount

        # запис транзакції у таблицю
        new_transaction = Transactions( user_id = user_id,
                                        type_operation = (request.get_json()["type_operation"]),
                                        id_currency_output = info_currency1.id_currency,
                                        id_currency_input = info_currency2.id_currency,
                                        count_currency_spent = am_cur_exch,
                                        count_currency_received = required_amount,
                                        commission = 0,
                                        id_account_output = account_user_info1.id,
                                        id_account_input = account_user_info2.id,
                                        date_operation = actual_date)

        db.session.add(info_currency1)
        db.session.add(info_currency2)
        db.session.add(account_user_info1)
        db.session.add(account_user_info2)
        db.session.add(new_transaction)
        db.session.commit()
        return "Операція обміну пройшла успішно"
    else:
        return "Операція не можлива. Недостатньо коштів у юзера або в обмінику для проведення операції. " \
               "Або вказані невірні дані"


@app.route('/user/<user_id>')    # інформація про користувача
def user_info(user_id):          # робив через ID бо якщо витягувати дані через логін, то засвічується пароль
    account_info = Account.query.filter_by(user_id=user_id).all()
    if not account_info:
        return f'Дані про користувача з ID: {user_id} не знайдено'
    else:
        return [item.to_dict() for item in account_info]


@app.post('/user/transfer')    # переказ коштів
def transfer_currency_user():

    return "User currency transaction"


@app.route('/user/<user_id>/history')    # історія переказів користувача
def user_transaction_history(user_id):
    transac_user_history = Transactions.query.filter_by(user_id=user_id).all()
    if not transac_user_history:
        return f'Дані про користувача з ID: {user_id} не знайдено'
    else:
        return [item.to_dict() for item in transac_user_history]


@app.route('/user/<user_id>/deposit')    # шнформфція про дипозит користувача
def deposit_user(user_id):
    deposit_info = Deposit.query.filter_by(user_id=user_id).all()
    if not deposit_info:
        return f'Дані про дипозит користувача з ID: {user_id} не знайдено'
    else:
        return [item.to_dict() for item in deposit_info]


@app.post('/user/deposit/<deposit_id>')    # створення дипозиту
def create_deposit(deposit_id):
    return f"user deposit in currency {deposit_id}"


if __name__ == '__main__':
    app.run(host='0.0.0.0')

