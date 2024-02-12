"""create_restaurants

Revision ID: 1a90794b0988
Revises: 8e918adde0c7
Create Date: 2024-02-10 00:12:10.194570

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = '1a90794b0988'
down_revision = '8e918adde0c7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('restaurants',
                    sa.Column('id', UUIDType(), nullable=False, primary_key=True),
                    sa.Column('user_id', UUIDType(), nullable=False),
                    sa.Column('category', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('address_street', sa.String(), nullable=False),
                    sa.Column('address_number', sa.String(), nullable=False),
                    sa.Column('address_neighborhood', sa.String(), nullable=False),
                    sa.Column('address_city', sa.String(), nullable=False),
                    sa.Column('address_state', sa.String(), nullable=False),
                    sa.Column('address_zip_code', sa.String(), nullable=False),
                    sa.Column('address_complement', sa.String(), nullable=True),
                    sa.Column('address_latitude', sa.DECIMAL(), nullable=True),
                    sa.Column('address_longitude', sa.DECIMAL(), nullable=True),
                    sa.Column('document_number', sa.String(), nullable=False),
                    sa.Column('logo_url', sa.String(), nullable=True),
                    sa.Column('description', sa.String(), nullable=True),
                    )
    op.create_index('idx_restaurants_user_id', 'restaurants', ['user_id'])
    op.create_index('idx_restaurants_category', 'restaurants', ['category'])
    op.create_index('idx_restaurants_document_number', 'restaurants', ['document_number'])
    op.create_table('working_hours',
                    sa.Column('id', UUIDType(), nullable=False, primary_key=True),
                    sa.Column('restaurant_id', UUIDType(), nullable=False),
                    sa.Column('day_of_week', sa.SMALLINT(), nullable=False),
                    sa.Column('opening_time', sa.Time(), nullable=False),
                    sa.Column('closing_time', sa.Time(), nullable=False),
                    )
    op.create_index('idx_working_hours_restaurant_id', 'working_hours', ['restaurant_id'])
    op.create_foreign_key('fk_working_hours_restaurants', 'working_hours', 'restaurants', ['restaurant_id'], ['id'])


def downgrade():
    op.drop_table('working_hours')
    op.drop_table('restaurants')
