from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/currency/<currency_name>/review', methods=['GET', 'DELETE', 'POST', 'PUT'])
def review(currency_name):
    # дозволяє працювати з відкуками конкретної валюти
    if request.method == 'DELETE':
        return f'Delete {currency_name} currency review'
    elif request.method == 'POST':
        return f'Create a review for {currency_name} currency'
    elif request.method == 'PUT':
        return f'Update Currency Review {currency_name}'
    else:
        return f'all reviews about {currency_name} currency'


@app.route('/currency/<currency_name>')
def show_info_currency(currency_name):
    # показує інформацію стосовно однієї валюти
    return f'Currency: {currency_name}'


@app.get('/currency/trade/<currency_name1>/<currency_name2>')
def trade_get_ratio(currency_name1, currency_name2):
    # відображає співвідношення двох валют
    return f"Ratio of currency - {currency_name1}/{currency_name2}"


@app.post('/currency/trade/<currency_name1>/<currency_name2>')
def trade_exchange(currency_name1, currency_name2):
    # операція обміну однієї валюти на другу
    return f"Exchange currency - {currency_name1}/{currency_name2}"


@app.route('/currency')
def all_currency():
    # список всіх валют
    return "List of all currencies"


@app.route('/user')
def user_info():
    # інформація про користувача
    return "All information about the user"


@app.post('/user/transfer')
def transfer_currency_user():
    # переказ коштів
    return "User currency transaction"


@app.route('/user/history')
def user_transaction_history():
    # історія переказів користувача
    return "User transaction history"


@app.route('/user/deposit')
def deposit_user():
    # шнформфція про дипозит користувача
    return 'User Deposit info'


@app.post('/user/deposit/<deposit_id>')
def create_deposit(deposit_id):
    # створення дипозиту
    return f"user deposit in currency {deposit_id}"


@app.route('/deposit/<currency_name>')
def deposit_info_currency(currency_name):
    # шнформація про дипозит у вказаній валюті
    return f"Info about deposit in {currency_name}"


if __name__ == '__main__':
    app.run()

