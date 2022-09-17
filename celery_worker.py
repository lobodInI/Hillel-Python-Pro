import database
import models

from celery import Celery
from datetime import datetime


app = Celery('celery_worker', broker='pyamqp://guest@localhost//')


@app.task
def task_trade(user_id, currency_name1, currency_name2, am_cur_exch, uuid_transaction):

    database.init_db()
    actual_date = datetime.now().strftime("%Y-%m-%d")

    # загальна актуальна інформація по валюту яку продає юзер
    info_currency1 = models.Currency.query.filter_by(name_currency=currency_name1.upper(),
                                                     pricing_date=actual_date).first()
    print(info_currency1)
    # загальна актуальна інформація по валюту яку купує юзер
    info_currency2 = models.Currency.query.filter_by(name_currency=currency_name2.upper(),
                                                     pricing_date=actual_date).first()
    # звертаємось до данних в Account до логіну юзера
    account_user_info1 = models.Account.query.filter_by(user_id=user_id,
                                                        id_currency=info_currency1.id_currency).first()
    account_user_info2 = models.Account.query.filter_by(user_id=user_id,
                                                        id_currency=info_currency2.id_currency).first()
    # сума у валюті, яку хоче купити юзер
    required_amount = round((info_currency1.cost_in_USD / info_currency2.cost_in_USD) * am_cur_exch, 2)

    # перевірка наявності валюти у юзера та перевірка чи є необхідна сума у обміннику
    if account_user_info1.balance >= am_cur_exch and required_amount <= info_currency2.available_quantity:
        if not account_user_info2:
            new_account = models.Account(user_id=user_id, id_currency=info_currency2.id_currency,
                                         balance=0, date_open=actual_date)
            database.db_session.add(new_account)
            database.db_session.commit()
            account_user_info2 = models.Account.query.filter_by(user_id=user_id,
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

        # оновлення запису транзакції у таблиці

        update_info_transaction = models.Transactions.query.filter_by(id_operation=uuid_transaction).first()

        update_info_transaction.id_currency_output = info_currency1.id_currency
        update_info_transaction.id_currency_input = info_currency2.id_currency
        update_info_transaction.count_currency_received = required_amount
        update_info_transaction.commission = 0
        update_info_transaction.id_account_output = account_user_info1.id
        update_info_transaction.id_account_input = account_user_info2.id
        update_info_transaction.status_operation = 'Successfully'


        database.db_session.add(info_currency1)
        database.db_session.add(info_currency2)
        database.db_session.add(account_user_info1)
        database.db_session.add(account_user_info2)
        database.db_session.add(update_info_transaction)
        database.db_session.commit()
        return "Операція обміну пройшла успішно"
    else:
        update_info_transaction = models.Transactions.query.filter_by(id_operation=uuid_transaction).first()
        update_info_transaction.status_operation = 'ERROR'
        database.db_session.add(update_info_transaction)
        database.db_session.commit()

        return "Операція не можлива. Недостатньо коштів у юзера або в обмінику для проведення операції. " \
               "Або вказані невірні дані"