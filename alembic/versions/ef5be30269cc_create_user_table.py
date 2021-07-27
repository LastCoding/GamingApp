"""create user table

Revision ID: ef5be30269cc
Revises: 
Create Date: 2021-07-27 14:15:58.031486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef5be30269cc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, unique=True),
        sa.Column('created_date', sa.DateTime),
        sa.Column('email', sa.String(200)),
        sa.Column('username', sa.String(100), unique=True),
        sa.Column('hashed_password', sa.String(100)),
        sa.Column('is_active', sa.Boolean)
    )


def downgrade():
    pass
