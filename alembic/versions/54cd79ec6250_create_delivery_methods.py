"""create_delivery_methods

Revision ID: 54cd79ec6250
Revises: 1cbd575a3e96
Create Date: 2024-04-13 14:04:55.038468

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = '54cd79ec6250'
down_revision = '1cbd575a3e96'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'delivery_methods',
        sa.Column('id', UUIDType(), nullable=False, primary_key=True),
        sa.Column('restaurant_id', UUIDType(), nullable=False),
        sa.Column('delivery_type', sa.String(), nullable=False),
        sa.Column('delivery_radius', sa.Integer(), nullable=True),
        sa.Column('delivery_fee', sa.Integer(), nullable=False),
        sa.Column('estimated_delivery_time', sa.Integer(), nullable=False)
    )
    op.create_foreign_key('fk_delivery_methods_restaurants', 'delivery_methods', 'restaurants', ['restaurant_id'],
                          ['id'])
    op.create_index('idx_delivery_methods_restaurant_id', 'delivery_methods', ['restaurant_id'])


def downgrade():
    op.drop_table('delivery_methods')
