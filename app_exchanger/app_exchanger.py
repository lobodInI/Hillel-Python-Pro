from flask import Flask, request
import sqlite3
import datetime

app = Flask(__name__)


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
    result = get_data("SELECT name_currency, cost_in_USD, available_quantity, pricing_date FROM Currency")
    return result


@app.route('/currency/<currency_name>/review', methods=['GET', 'DELETE', 'POST', 'PUT'])     # дозволяє працювати з
def review_currency(currency_name):                                                    # відкуками конкретної валюти
    if request.method == 'DELETE':
        return f'DELETE a review for {currency_name} currency'

    elif request.method == 'POST':
        request_data = request.get_json()
        get_data(f"""INSERT INTO Review (id_currency, rating, review_client, date_review) 
        VALUES ((SELECT id_currency FROM Currency 
                 WHERE name_currency='{currency_name.upper()}' ORDER by pricing_date DESC LIMIT 1), 
        '{request_data['rating']}', '{request_data['review_client']}', '{request_data['date_review']}')""")
        return 'Data is recorded.'

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
        (SELECT cost_in_USD FROM Currency 
            WHERE name_currency='{currency_name1.upper()}' ORDER by pricing_date DESC LIMIT 1)/
        (SELECT cost_in_USD FROM Currency 
            WHERE name_currency='{currency_name2.upper()}' ORDER by pricing_date DESC LIMIT 1), 2) as exchange_rate""")
        return f"За одну грошову одиницю {currency_name1.upper()}, " \
               f"ви заплатите {result[0]['exchange_rate']} {currency_name2.upper()}"


@app.post('/currency/trade/<currency_name1>/<currency_name2>')    # операція обміну однієї валюти на другу
def trade_exchange(currency_name1, currency_name2):
    user_login = request.get_json()['user_login']                 # вказуємо логін юзера у json
    user_id = (get_data(f"""SELECT id FROM User WHERE login='{user_login}'"""))[0]['id']
    am_cur_exch = request.get_json()['amount']                   # am_cur_exch = Amount of currency to exchange

    # звертаємось до данних в Account до логіну юзера, та назви валюти
    check_balance_user = get_data(f"""SELECT balance FROM Account JOIN Currency, User 
                        on Currency.id_currency=Account.id_currency AND User.id=Account.user_id 
                        WHERE user_id='{user_id}' AND name_currency='{currency_name1.upper()}'""")[0]['balance']

    # загальна актуальна інформація по валюту яку продає юзер
    info_currency1 = get_data(f"""SELECT * FROM Currency WHERE name_currency='{currency_name1.upper()}'
                                              ORDER by pricing_date DESC LIMIT 1""")
    # загальна актуальна інформація по валюту яку купує юзер
    info_currency2 = get_data(f"""SELECT * FROM Currency WHERE name_currency='{currency_name2.upper()}'
                                                  ORDER by pricing_date DESC LIMIT 1""")

    # сума у валюті, яку хоче купити юзер
    required_amount = round((info_currency1[0]['cost_in_USD'] / info_currency2[0]['cost_in_USD']) * am_cur_exch, 2)

    # перевірка наявності валюти у юзера та перевірка чи є необхідна сума у обміннику
    if check_balance_user >= am_cur_exch and required_amount <= info_currency2[0]['available_quantity']:

        # оновлення id валюти в Account у юзера,  яку юзер хоче продати
        old_id_currency_user_cell = get_data(f"""SELECT Account.id_currency FROM Account JOIN Currency
                                on Currency.id_currency=Account.id_currency WHERE name_currency='{currency_name1.upper()}'
                                AND user_id='{user_id}'""")

        get_data(f"""UPDATE Account SET id_currency={info_currency1[0]['id_currency']}
                             WHERE id_currency={old_id_currency_user_cell[0]['id_currency']} AND user_id='{user_id}'""")

        # оновлення id валюти в Account у юзера,  яку юзер хоче купити
        old_id_currency_user_buy = get_data(f"""SELECT Account.id_currency FROM Account JOIN Currency
                                on Currency.id_currency=Account.id_currency WHERE name_currency='{currency_name2.upper()}'
                                AND user_id='{user_id}'""")

        # перевірка чи є рахунок у валюті яку хоче купити юзер в Account
        if not old_id_currency_user_buy:
            get_data(f"""INSERT INTO Account (user_id, id_currency, balance) 
                                 VALUES ('{user_id}', '{info_currency2[0]['id_currency']}', 0)""")
        else:
            get_data(f"""UPDATE Account SET id_currency={info_currency2[0]['id_currency']}
                                         WHERE id_currency={old_id_currency_user_buy[0]['id_currency']} 
                                         AND user_id='{user_id}'""")

        # оновлення доступної кількості валюти у одміннику, яку продає юзер
        # не створюємо нову строку бо в теорії в нас кожен день оновлюєтться та сворюється строка валюти
        get_data(f"""UPDATE Currency
                     SET available_quantity={(info_currency1[0]['available_quantity']+am_cur_exch)},
                        pricing_date='{datetime.datetime.now().strftime("%Y-%m-%d")}'
                     WHERE id_currency='{info_currency1[0]['id_currency']}'""")

        # оновлення доступної кількості валюти у одміннику, яку купує юзер
        get_data(f"""UPDATE Currency
                     SET available_quantity={(info_currency2[0]['available_quantity']-required_amount)},
                        pricing_date='{datetime.datetime.now().strftime("%Y-%m-%d")}'
                     WHERE id_currency={info_currency2[0]['id_currency']}""")

        # оновлення кількості валюти у юзера яку продав
        get_data(f"""UPDATE Account SET balance={check_balance_user-am_cur_exch} 
                     WHERE user_id='{user_id}' AND id_currency='{info_currency1[0]['id_currency']}'""")

        # баланс валюти яку хоче купити юзер, в Account у юзера
        balance_user_currency2 = get_data(f"""SELECT balance FROM Account WHERE user_id='{user_id}' 
                                              AND id_currency='{info_currency2[0]['id_currency']}'""")

        # оновлення кількості валюти у юзера яку купив
        get_data(f"""UPDATE Account SET balance='{balance_user_currency2[0]['balance']+required_amount}'
                     WHERE user_id='{user_id}' AND id_currency='{info_currency2[0]['id_currency']}'""")

        # запис транзакції у таблицю
        get_data(f"""INSERT INTO Transactions (user_id, type_operation, id_currency_output, id_currency_input,
                                  count_currency_spent, count_currency_received, commission, id_account_output, 
                                  id_account_input, date_operation)
                    VALUES ('{user_id}', '{request.get_json()['type_operation']}', 
                    '{info_currency1[0]['id_currency']}', '{info_currency2[0]['id_currency']}', 
                    '{am_cur_exch}', '{required_amount}', 0, 
                    (SELECT id FROM Account WHERE id_currency='{info_currency1[0]['id_currency']}' 
                                            AND user_id='{user_id}'), 
                    (SELECT id FROM Account WHERE id_currency='{info_currency2[0]['id_currency']}' 
                                            AND user_id='{user_id}'), 
                    '{datetime.datetime.now().strftime("%Y-%m-%d")}')""")

        return "Операція обміну пройшла успішно"
    else:
        return "Операція не можлива. Недостатньо коштів у юзера або в обмінику для проведення операції. " \
               "Або вказані невірні дані"


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

