"""create_payment_receive_accounts

Revision ID: fc096a99cd69
Revises: 54cd79ec6250
Create Date: 2024-04-14 18:35:37.692994

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = 'fc096a99cd69'
down_revision = '54cd79ec6250'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'payment_receive_accounts',
        sa.Column('id', UUIDType(), nullable=False, primary_key=True),
        sa.Column('restaurant_id', UUIDType(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('onboarding_completed', sa.Boolean(), nullable=False)
    )
    op.create_index('idx_payment_receive_accounts_restaurant_id', 'payment_receive_accounts', ['restaurant_id'])
    op.create_index('idx_payment_receive_accounts_external_id', 'payment_receive_accounts', ['external_id'])


def downgrade():
    op.drop_table('payment_receive_accounts')
