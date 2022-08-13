from flask import Flask, request
import sqlite3


app = Flask(__name__)


def get_data(query: str):
    with sqlite3.connect('databases_exchanger.db') as db:
        cursor = db.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result



@app.route('/currency/<currency_rev>/review', methods=['GET', 'DELETE', 'POST', 'PUT'])     # дозволяє працювати з відкуками конкретної валюти
def review_currency(currency_rev):
    if request.method == 'GET':
        res = get_data(f"SELECT balance FROM Account WHERE user_id='{currency_rev}'")
        return res
    elif request.method == 'DELETE':
        return f'DELETE a review for {currency_rev} currency'
    elif request.method == 'POST':
        return f'Create a review for {currency_rev} currency'
    else:
        return f'Update Currency Review {currency_rev}'


@app.get('/currency/<currency_name>')     # показує інформацію стосовно однієї валюти
def show_info_currency(currency_name):
    conn = sqlite3.connect('Databases_exchanger.db')
    cursor = conn.execute(f"SELECT * FROM Currency")
    result = cursor.fetchall()
    conn.close()
    return result


@app.get('/currency/trade_ratio/<currency_name1>/<currency_name2>')    # відображає співвідношення двох валют
def trade_get_ratio(currency_name1, currency_name2):

    return f"Ratio of currency - {currency_name1}/{currency_name2}"


@app.post('/currency/trade/<currency_name1>/<currency_name2>')    # операція обміну однієї валюти на другу
def trade_exchange(currency_name1, currency_name2):

    return f"Exchange currency - {currency_name1}/{currency_name2}"


@app.get('/currency')    # список всіх валют
def all_currency():
    conn = sqlite3.connect('databases_exchanger.db')
    cursor = conn.execute("SELECT * FROM Currency")
    result = cursor.fetchall()
    conn.close()
    return result


@app.route('/user')    # інформація про користувача
def user_info():

    return "All information about the user"


@app.post('/user/transfer')    # переказ коштів
def transfer_currency_user():

    return "User currency transaction"


@app.route('/user/history')    # історія переказів користувача
def user_transaction_history():

    return "User transaction history"


@app.route('/user/deposit')    # шнформфція про дипозит користувача
def deposit_user():

    return 'User Deposit info'


@app.post('/user/deposit/<deposit_id>')    # створення дипозиту
def create_deposit(deposit_id):

    return f"user deposit in currency {deposit_id}"


@app.route('/deposit/<currency_name>')    # шнформація про дипозит у вказаній валюті
def deposit_info_currency(currency_name):

    return f"Info about deposit in {currency_name}"


if __name__ == '__main__':
    app.run()

