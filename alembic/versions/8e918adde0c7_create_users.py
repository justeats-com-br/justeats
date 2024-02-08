"""create_users

Revision ID: 8e918adde0c7
Revises: f4e01a42c3bf
Create Date: 2024-02-07 21:30:17.039899

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = '8e918adde0c7'
down_revision = 'f4e01a42c3bf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', UUIDType(), nullable=False, primary_key=True),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('type', sa.String(), nullable=False),
                    )
    op.create_index('idx_uniq_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_type', 'users', ['type'])


def downgrade():
    op.drop_table('users')
