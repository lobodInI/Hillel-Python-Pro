from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Account(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    user_id = db.Column(db.INTEGER, nullable=False)
    id_currency = db.Column(db.INTEGER, nullable=False)
    balance = db.Column(db.REAL, nullable=False)
    date_open = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return f'<Account {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'id_currency': self.id_currency,
            'balance': self.balance,
        }


class Currency(db.Model):
    id_currency = db.Column(db.INTEGER, primary_key=True, nullable=False)
    name_currency = db.Column(db.TEXT, nullable=False)
    cost_in_USD = db.Column(db.REAL, nullable=False)
    available_quantity = db.Column(db.REAL, nullable=False)
    pricing_date = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return f'<Currency {self.name_currency}>'

    def to_dict(self):
        return {
            'id_currency': self.id_currency,
            'name_currency': self.name_currency,
            'cost_in_USD': self.cost_in_USD,
            'available_quantity': self.available_quantity,
            'pricing_date': self.pricing_date,
        }


class Deposit(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    user_id = db.Column(db.INTEGER, nullable=False)
    opening_date = db.Column(db.TEXT, nullable=False)
    closing_date = db.Column(db.TEXT, nullable=False)
    id_currency = db.Column(db.INTEGER, nullable=False)
    balance = db.Column(db.REAL, nullable=False)
    interest_rate = db.Column(db.INTEGER, nullable=False)
    storage_conditions = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return f'<Deposit {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'opening_date': self.opening_date,
            'closing_date': self.closing_date,
            'id_currency': self.id_currency,
            'balance': self.balance,
            'interest_rate': self.interest_rate,
            'storage_conditions': self.storage_conditions,
        }


class Review(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    id_currency = db.Column(db.INTEGER, nullable=False)
    user_rating = db.Column(db.REAL, nullable=False)
    review_client = db.Column(db.TEXT, nullable=False)
    date_review = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return f'<Review {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'id_currency': self.id_currency,
            'user_rating': self.user_rating,
            'review_client': self.review_client,
            'date_review': self.date_review,
        }


class Transactions(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    user_id = db.Column(db.INTEGER, nullable=False)
    type_operation = db.Column(db.TEXT, nullable=False)
    id_currency_output = db.Column(db.INTEGER, nullable=False)
    id_currency_input = db.Column(db.INTEGER, nullable=False)
    count_currency_spent = db.Column(db.REAL, nullable=False)
    count_currency_received = db.Column(db.REAL, nullable=False)
    commission = db.Column(db.REAL, nullable=False)
    id_account_output = db.Column(db.INTEGER, nullable=False)
    id_account_input = db.Column(db.INTEGER, nullable=False)
    date_operation = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return f'<Transaction {self.id}, {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type_operation': self.type_operation,
            'id_currency_output': self.id_currency_output,
            'id_currency_input': self.id_currency_input,
            'count_currency_spent': self.count_currency_spent,
            'commission': self.commission,
            'id_account_output': self.id_account_output,
            'id_account_input': self.id_account_input,
            'date_operation': self.date_operation,
        }


class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    login = db.Column(db.TEXT, nullable=False)
    password = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return f'<User {self.login}>'

    def to_dict(self):
        return {
            'id': self.id,
            'login': self.login,
            'password': self.password
        }

