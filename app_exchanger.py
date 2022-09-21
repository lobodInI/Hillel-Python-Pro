import os
import time
import json
import uuid
import random
import models
import database


from datetime import datetime
from celery_worker import task_trade
from flask import Flask, request, session


app = Flask(__name__)


session_secret = os.environ.get('SESSION_SECRET')
if not session_secret:
    if not os.path.exists('session.secret'):
        secret_file = open('session.secret', 'w')
        secret_file.write(str(random.randint(10000000, 999999999)))
        secret_file.close()
    secret_file = open('session.secret')
    session_secret = secret_file.read()
    secret_file.close()

app.secret_key = session_secret


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


@app.route('/currency/trade/<currency_name1>/<currency_name2>', methods=['GET', 'POST'])    # операція обміну однієї валюти на другу
def trade_exchange(currency_name1, currency_name2):
    database.init_db()
    if request.method == 'GET':
        if session.get('user_login') is not None:
            return '''
                <html>
                <form method="post"
          <div class="container">
            <label for="uname"><b>amount_currency</b></label>
            <input type="text" placeholder="Enter how many" name="amount_currency" required>
            <button type="submit">Submit</button>
          </div>
        </form>
                </html>
                '''
        else:
            return 'Login first!!!'

    else:
        user_login = session.get('user_login')
        user_id = models.User.query.filter_by(login=user_login).first().id   # отримуємо ІД юзера через логін
        am_cur_exch = float(request.form.get('amount_currency'))             # am_cur_exch = Amount of currency to exchange

        uuid_transaction = uuid.uuid4()
        actual_date = datetime.now().strftime("%Y-%m-%d")
        new_transaction = models.Transactions(user_id=user_id,               # створення запису у таблиці транзакцій
                                              type_operation="currency exchange",
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
        # time.sleep(10)
        task_obj = task_trade.apply_async(args=[user_id, currency_name1, currency_name2, am_cur_exch, uuid_transaction])

        return 'Request was sent'


@app.route('/user', methods=['GET', 'POST'])
def user_info():
    database.init_db()
    if request.method == 'GET':
        user_login = session.get('user_login')
        if user_login is None:
            return '''
            <html>
            <form method="post">
  <div class="container">
    <label for="uname"><b>Username</b></label>
    <input type="text" placeholder="Enter Username" name="uname" required>

    <label for="psw"><b>Password</b></label>
    <input type="password" placeholder="Enter Password" name="psw" required>

    <button type="submit">Login</button>
  </div>
</form>
            </html>
            '''
        else:
            # account_info = models.Account.query.filter_by(user_id=user_login).all()
            user_id = models.User.query.filter_by(login=user_login).first().id
            account_info = models.Account.query.filter_by(user_id=user_id).all()
            if not account_info:
                return f'Дані про рахунки користувача з Логіном: {user_login} не знайдено'
            else:
                return [item.to_dict() for item in account_info]
    else:
        user_login = request.form.get('uname')
        user_pasw = request.form.get('psw')
        check_user_info = models.User.query.filter_by(login=user_login, password=user_pasw).first()
        if check_user_info:
            session['user_login'] = user_login
            return 'Successful authorization'
        else:
            return 'Authorization error'


@app.route('/user/history', methods=['GET', 'POST'])   # історія переказів користувача
def history_info():
    database.init_db()
    if request.method == 'GET':
        user_login = session.get('user_login')
        if user_login is None:
            return '''
            <html>
            <form method="post">
  <div class="container">
    <label for="uname"><b>Username</b></label>
    <input type="text" placeholder="Enter Username" name="uname" required>

    <label for="psw"><b>Password</b></label>
    <input type="password" placeholder="Enter Password" name="psw" required>

    <button type="submit">Login</button>
  </div>
</form>
            </html>
            '''
        else:
            user_id = models.User.query.filter_by(login=user_login).first().id
            transaction_info = models.Transactions.query.filter_by(user_id=user_id).all()
            if not transaction_info:
                return f'Дані про транзакціі користувача з Логіном: {user_login} не знайдено'
            else:
                return [item.to_dict() for item in transaction_info]
    else:
        user_login = request.form.get('uname')
        user_pasw = request.form.get('psw')
        check_user_info = models.User.query.filter_by(login=user_login, password=user_pasw).first()
        if check_user_info:
            session['user_login'] = user_login
            return 'Successful authorization'
        else:
            return 'Authorization error'


@app.route('/user/deposit', methods=['GET', 'POST'])   # iнформфція про дипозит користувача
def deposit_user():
    database.init_db()
    if request.method == 'GET':
        user_login = session.get('user_login')
        if user_login is None:
            return '''
            <html>
            <form method="post">
  <div class="container">
    <label for="uname"><b>Username</b></label>
    <input type="text" placeholder="Enter Username" name="uname" required>

    <label for="psw"><b>Password</b></label>
    <input type="password" placeholder="Enter Password" name="psw" required>

    <button type="submit">Login</button>
  </div>
</form>
            </html>
            '''
        else:
            user_id = models.User.query.filter_by(login=user_login).first().id
            deposit_info = models.Deposit.query.filter_by(user_id=user_id).all()
            if not deposit_info:
                return f'Дані про депозит користувача з Логіном: {user_login} не знайдено'
            else:
                return [item.to_dict() for item in deposit_info]
    else:
        user_login = request.form.get('uname')
        user_pasw = request.form.get('psw')
        check_user_info = models.User.query.filter_by(login=user_login, password=user_pasw).first()
        if check_user_info:
            session['user_login'] = user_login
            return 'Successful authorization'
        else:
            return 'Authorization error'


# @app.route('/user/<user_id>/history')    # історія переказів користувача
# def user_transaction_history(user_id):
#     transac_user_history = models.Transactions.query.filter_by(user_id=user_id).all()
#     if not transac_user_history:
#         return f'Дані про користувача з ID: {user_id} не знайдено'
#     else:
#         return [item.to_dict() for item in transac_user_history]


# @app.route('/user/<user_id>/deposit')    # шнформфція про дипозит користувача
# def deposit_user(user_id):
#     deposit_info = models.Deposit.query.filter_by(user_id=user_id).all()
#     if not deposit_info:
#         return f'Дані про дипозит користувача з ID: {user_id} не знайдено'
#     else:
#         return [item.to_dict() for item in deposit_info]


@app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()


if __name__ == '__main__':
    app.run(host='0.0.0.0')

