"""change_upload_urls_to_keys

Revision ID: 1cbd575a3e96
Revises: 8bc71c81e058
Create Date: 2024-03-02 10:14:48.006575

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '1cbd575a3e96'
down_revision = '8bc71c81e058'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('products', 'image_url', new_column_name='image_key')
    op.alter_column('restaurants', 'logo_url', new_column_name='logo_key')


def downgrade():
    op.alter_column('products', 'image_key', new_column_name='image_url')
    op.alter_column('restaurants', 'logo_key', new_column_name='logo_url')
