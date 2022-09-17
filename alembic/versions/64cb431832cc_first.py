"""first

Revision ID: 64cb431832cc
Revises: 
Create Date: 2022-09-16 23:18:34.992243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64cb431832cc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Account',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('id_currency', sa.INTEGER(), nullable=False),
    sa.Column('balance', sa.REAL(), nullable=False),
    sa.Column('date_open', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Currency',
    sa.Column('id_currency', sa.INTEGER(), nullable=False),
    sa.Column('name_currency', sa.TEXT(), nullable=False),
    sa.Column('cost_in_USD', sa.REAL(), nullable=False),
    sa.Column('available_quantity', sa.REAL(), nullable=False),
    sa.Column('pricing_date', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id_currency')
    )
    op.create_table('Deposit',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('opening_date', sa.TEXT(), nullable=False),
    sa.Column('closing_date', sa.TEXT(), nullable=False),
    sa.Column('id_currency', sa.INTEGER(), nullable=False),
    sa.Column('balance', sa.REAL(), nullable=False),
    sa.Column('interest_rate', sa.INTEGER(), nullable=False),
    sa.Column('storage_conditions', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Review',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('id_currency', sa.INTEGER(), nullable=False),
    sa.Column('user_rating', sa.REAL(), nullable=False),
    sa.Column('review_client', sa.TEXT(), nullable=False),
    sa.Column('date_review', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Transaction',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('type_operation', sa.TEXT(), nullable=False),
    sa.Column('id_currency_output', sa.INTEGER(), nullable=False),
    sa.Column('id_currency_input', sa.INTEGER(), nullable=False),
    sa.Column('count_currency_spent', sa.REAL(), nullable=False),
    sa.Column('count_currency_received', sa.REAL(), nullable=False),
    sa.Column('commission', sa.REAL(), nullable=False),
    sa.Column('id_account_output', sa.INTEGER(), nullable=False),
    sa.Column('id_account_input', sa.INTEGER(), nullable=False),
    sa.Column('date_operation', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('User',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('login', sa.TEXT(), nullable=False),
    sa.Column('password', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('User')
    op.drop_table('Transaction')
    op.drop_table('Review')
    op.drop_table('Deposit')
    op.drop_table('Currency')
    op.drop_table('Account')
    # ### end Alembic commands ###