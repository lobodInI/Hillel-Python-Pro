from flask import Flask, request
import sqlite3


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'world is amazing'


def get_data(query: str):
    with sqlite3.connect("databases_exchanger.db") as con:
        cursor = con.execute(query)
        result = cursor.fetchall()
        return result


@app.route('/currency')    # список всіх валют
def all_currency():
    result = get_data("SELECT name_currency, cost_in_USD, available_quantity FROM Currency")
    return result


@app.route('/currency/<currency_name>/review', methods=['GET', 'DELETE', 'POST', 'PUT'])     # дозволяє працювати з
def review_currency(currency_name):                                                    # відкуками конкретної валюти
    if request.method == 'DELETE':
        return f'DELETE a review for {currency_name} currency'
    elif request.method == 'POST':
        return f'Create a review for {currency_name} currency'
    elif request.method == 'PUT':
        return f'Update a review for {currency_name} currency'
    else:
        result = get_data(f"""SELECT name_currency, rating, review_client, date_review 
        FROM Review JOIN Currency on Currency.id_currency=Review.id_currency 
        WHERE name_currency='{currency_name.upper()}'""")
        if not result:
            return f'Відгуків по данній валюті {currency_name} не знайдено'
        else:
            return result


@app.route('/currency/<currency_name>')     # показує інформацію стосовно однієї валюти
def show_info_currency(currency_name):      # format currency name: XXX
    result = get_data(f"SELECT * FROM Currency WHERE name_currency='{currency_name.upper()}'")
    if not result:
        return f'Дані про валюту {currency_name} не знайдено'
    else:
        return result


@app.route('/currency/trade_ratio/<currency_name1>/<currency_name2>')    # відображає співвідношення двох валют
def trade_get_ratio(currency_name1, currency_name2):
    name_check1 = get_data(f"SELECT cost_in_USD FROM Currency WHERE name_currency='{currency_name1.upper()}'")
    name_check2 = get_data(f"SELECT cost_in_USD FROM Currency WHERE name_currency='{currency_name2.upper()}'")
    if not name_check1 or not name_check2:
        return 'спробуйте корректно ввести назву валют, або валютної пари не існує'
    else:
        result = get_data(f"""SELECT round(
        (SELECT cost_in_USD FROM Currency WHERE name_currency='{currency_name1.upper()}' AND 
        pricing_date=(SELECT max(pricing_date) FROM Currency WHERE name_currency='{currency_name1.upper()}'))/
        (SELECT cost_in_USD FROM Currency WHERE name_currency='{currency_name2.upper()}' AND 
        pricing_date=(SELECT max(pricing_date) FROM Currency WHERE name_currency='{currency_name2.upper()}')), 2)""")
        return f"За одну грошову одиницю {currency_name1.upper()}, ви заплатите {result}{currency_name2.upper()}"



@app.post('/currency/trade/<currency_name1>/<currency_name2>')    # операція обміну однієї валюти на другу
def trade_exchange(currency_name1, currency_name2):

    return f"Exchange currency - {currency_name1}/{currency_name2}"


@app.route('/user/<login>')    # інформація про користувача
def user_info(login):
    result = get_data(f"""SELECT login, name_currency, balance FROM Currency JOIN Account, User 
    on Currency.id_currency=Account.id_currency AND User.id=Account.user_id WHERE login='{login}'""")
    if not result:
        return f'Дані про користувача {login} не знайдено'
    else:
        return result


@app.post('/user/transfer')    # переказ коштів
def transfer_currency_user():

    return "User currency transaction"


@app.route('/user/<login>/history')    # історія переказів користувача
def user_transaction_history(login):
    result = get_data(f"""SELECT type_operation, id_currency_output, count_currency_spent, id_currency_input, 
    count_currency_received, commission, date_operation From Transactions JOIN User on 
    User.id=Transactions.user_id WHERE login='{login}'""")
    if not result:
        return f'Дані про користувача {login} не знайдено'
    else:
        return result

@app.route('/user/<login>/deposit')    # шнформфція про дипозит користувача
def deposit_user(login):
    result = get_data(f"""SELECT login, name_currency, balance, opening_date, closing_date, interest_rate, 
    storage_conditions FROM Deposit JOIN User, Currency on Deposit.user_id=User.id AND 
    Deposit.id_currency=Currency.id_currency WHERE login='{login}'""")
    if not result:
        return f'Дані про дипозит користувача {login} не знайдено'
    else:
        return result


@app.post('/user/deposit/<deposit_id>')    # створення дипозиту
def create_deposit(deposit_id):

    return f"user deposit in currency {deposit_id}"


@app.route('/deposit/<currency_name>')    # вся шнформація про дипозит у вказаній валюті
def deposit_info_currency(currency_name):

    return f"Info about deposit in {currency_name}"


if __name__ == '__main__':
    app.run()

