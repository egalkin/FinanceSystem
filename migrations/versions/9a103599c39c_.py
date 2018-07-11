"""empty message

Revision ID: 9a103599c39c
Revises: 
Create Date: 2018-07-11 16:13:11.428818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a103599c39c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bank_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_name', sa.String(length=64), nullable=True),
    sa.Column('cash_amount', sa.Float(), nullable=True),
    sa.Column('account_currency', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_account_account_currency'), 'bank_account', ['account_currency'], unique=False)
    op.create_index(op.f('ix_bank_account_account_name'), 'bank_account', ['account_name'], unique=True)
    op.create_index(op.f('ix_bank_account_cash_amount'), 'bank_account', ['cash_amount'], unique=False)
    op.create_table('operation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('operation_amount', sa.Float(), nullable=True),
    sa.Column('account_amount_before_operation', sa.Float(), nullable=True),
    sa.Column('operation_currency', sa.String(length=64), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('is_income', sa.Boolean(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['bank_account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_operation_account_amount_before_operation'), 'operation', ['account_amount_before_operation'], unique=False)
    op.create_index(op.f('ix_operation_category'), 'operation', ['category'], unique=False)
    op.create_index(op.f('ix_operation_is_income'), 'operation', ['is_income'], unique=False)
    op.create_index(op.f('ix_operation_operation_amount'), 'operation', ['operation_amount'], unique=False)
    op.create_index(op.f('ix_operation_operation_currency'), 'operation', ['operation_currency'], unique=False)
    op.create_index(op.f('ix_operation_timestamp'), 'operation', ['timestamp'], unique=False)
    op.create_table('saving_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_amount', sa.Float(), nullable=True),
    sa.Column('account_name', sa.String(length=128), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('raise_percent', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['bank_account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saving_account_account_amount'), 'saving_account', ['account_amount'], unique=False)
    op.create_index(op.f('ix_saving_account_account_name'), 'saving_account', ['account_name'], unique=False)
    op.create_index(op.f('ix_saving_account_raise_percent'), 'saving_account', ['raise_percent'], unique=False)
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transaction_amount', sa.Float(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('transaction_currency', sa.String(length=64), nullable=True),
    sa.Column('is_income', sa.Boolean(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('sender_name', sa.String(length=64), nullable=True),
    sa.Column('recipient_name', sa.String(length=64), nullable=True),
    sa.Column('category', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['bank_account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_category'), 'transaction', ['category'], unique=False)
    op.create_index(op.f('ix_transaction_is_income'), 'transaction', ['is_income'], unique=False)
    op.create_index(op.f('ix_transaction_recipient_name'), 'transaction', ['recipient_name'], unique=False)
    op.create_index(op.f('ix_transaction_sender_name'), 'transaction', ['sender_name'], unique=False)
    op.create_index(op.f('ix_transaction_timestamp'), 'transaction', ['timestamp'], unique=False)
    op.create_index(op.f('ix_transaction_transaction_amount'), 'transaction', ['transaction_amount'], unique=False)
    op.create_index(op.f('ix_transaction_transaction_currency'), 'transaction', ['transaction_currency'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_transaction_currency'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_transaction_amount'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_timestamp'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_sender_name'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_recipient_name'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_is_income'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_category'), table_name='transaction')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_saving_account_raise_percent'), table_name='saving_account')
    op.drop_index(op.f('ix_saving_account_account_name'), table_name='saving_account')
    op.drop_index(op.f('ix_saving_account_account_amount'), table_name='saving_account')
    op.drop_table('saving_account')
    op.drop_index(op.f('ix_operation_timestamp'), table_name='operation')
    op.drop_index(op.f('ix_operation_operation_currency'), table_name='operation')
    op.drop_index(op.f('ix_operation_operation_amount'), table_name='operation')
    op.drop_index(op.f('ix_operation_is_income'), table_name='operation')
    op.drop_index(op.f('ix_operation_category'), table_name='operation')
    op.drop_index(op.f('ix_operation_account_amount_before_operation'), table_name='operation')
    op.drop_table('operation')
    op.drop_index(op.f('ix_bank_account_cash_amount'), table_name='bank_account')
    op.drop_index(op.f('ix_bank_account_account_name'), table_name='bank_account')
    op.drop_index(op.f('ix_bank_account_account_currency'), table_name='bank_account')
    op.drop_table('bank_account')
    # ### end Alembic commands ###
