"""create_catalogs

Revision ID: 8bc71c81e058
Revises: 1a90794b0988
Create Date: 2024-02-17 17:44:58.414069

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = '8bc71c81e058'
down_revision = '1a90794b0988'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('catalogs',
                    sa.Column('id', UUIDType(), nullable=False, primary_key=True),
                    sa.Column('restaurant_id', UUIDType(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    )
    op.create_index('idx_catalogs_restaurant_id', 'catalogs', ['restaurant_id'])
    op.create_foreign_key('fk_catalogs_restaurants', 'catalogs', 'restaurants', ['restaurant_id'], ['id'])

    op.create_table('sections',
                    sa.Column('id', UUIDType(), nullable=False, primary_key=True),
                    sa.Column('catalog_id', UUIDType(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('sort_order', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    )
    op.create_index('idx_sections_catalog_id', 'sections', ['catalog_id'])
    op.create_foreign_key('fk_sections_catalogs', 'sections', 'catalogs', ['catalog_id'], ['id'])

    op.create_table('products',
                    sa.Column('id', UUIDType(), nullable=False, primary_key=True),
                    sa.Column('section_id', UUIDType(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('price', sa.Integer(), nullable=True),
                    sa.Column('image_url', sa.String(), nullable=True),
                    sa.Column('status', sa.String(), nullable=False),
                    sa.Column('variants', sa.JSON(), nullable=False),
                    sa.Column('modifiers', sa.JSON(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    )
    op.create_index('idx_products_section_id', 'products', ['section_id'])
    op.create_foreign_key('fk_products_sections', 'products', 'sections', ['section_id'], ['id'])


def downgrade():
    op.drop_table('sections')
    op.drop_table('catalogs')
