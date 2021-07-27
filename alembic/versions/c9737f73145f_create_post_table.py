"""create post table

Revision ID: c9737f73145f
Revises: ef5be30269cc
Create Date: 2021-07-27 14:57:57.614793

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9737f73145f'
down_revision = 'ef5be30269cc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True, unique=True),
        sa.Column('created_date', sa.DateTime),
        sa.Column('is_active', sa.Boolean),
        sa.Column('title', sa.String(100)),
        sa.Column('body', sa.String(1000)),
        sa.Column('owner_id', sa.Integer)
    )


def downgrade():
    pass
