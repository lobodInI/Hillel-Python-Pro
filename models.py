from sqlalchemy import Column, INTEGER, REAL, TEXT
from database import Base


class Account(Base):
    __tablename__ = 'Account'

    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    id_currency = Column(INTEGER, nullable=False)
    balance = Column(REAL, nullable=False)
    date_open = Column(TEXT, nullable=False)

    def __repr__(self):
        return f'<Account {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'id_currency': self.id_currency,
            'balance': self.balance,
        }


class Currency(Base):
    __tablename__ = 'Currency'

    id_currency = Column(INTEGER, primary_key=True, nullable=False)
    name_currency = Column(TEXT, nullable=False)
    cost_in_USD = Column(REAL, nullable=False)
    available_quantity = Column(REAL, nullable=False)
    pricing_date = Column(TEXT, nullable=False)

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


class Deposit(Base):
    __tablename__ = 'Deposit'

    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    opening_date = Column(TEXT, nullable=False)
    closing_date = Column(TEXT, nullable=False)
    id_currency = Column(INTEGER, nullable=False)
    balance = Column(REAL, nullable=False)
    interest_rate = Column(INTEGER, nullable=False)
    storage_conditions = Column(TEXT, nullable=False)

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


class Review(Base):
    __tablename__ = 'Review'

    id = Column(INTEGER, primary_key=True, nullable=False)
    id_currency = Column(INTEGER, nullable=False)
    user_rating = Column(REAL, nullable=False)
    review_client = Column(TEXT, nullable=False)
    date_review = Column(TEXT, nullable=False)

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


class Transactions(Base):
    __tablename__ = 'Transaction'

    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    type_operation = Column(TEXT, nullable=False)
    id_currency_output = Column(INTEGER, nullable=False)
    id_currency_input = Column(INTEGER, nullable=False)
    count_currency_spent = Column(REAL, nullable=False)
    count_currency_received = Column(REAL, nullable=False)
    commission = Column(REAL, nullable=False)
    id_account_output = Column(INTEGER, nullable=False)
    id_account_input = Column(INTEGER, nullable=False)
    date_operation = Column(TEXT, nullable=False)
    id_operation = Column(TEXT, nullable=False)
    status_operation = Column(TEXT, nullable=False)

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
            'count_currency_received': self.count_currency_received,
            'commission': self.commission,
            'id_account_output': self.id_account_output,
            'id_account_input': self.id_account_input,
            'date_operation': self.date_operation,
            'id_operation': self.id_operation,
            'status_operation': self.status_operation
        }


class User(Base):
    __tablename__ = 'User'

    id = Column(INTEGER, primary_key=True, nullable=False)
    login = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)

    def __repr__(self):
        return f'<User {self.login}>'

    def to_dict(self):
        return {
            'id': self.id,
            'login': self.login,
            'password': self.password
        }

