"""add replit auth fields

Revision ID: 004
Revises: 003
Create Date: 2024-11-25 08:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Add Replit authentication columns to user table
    try:
        op.add_column('user', sa.Column('replit_user_id', sa.String(256), unique=True, nullable=True))
        op.add_column('user', sa.Column('last_login', sa.DateTime, nullable=True))
        op.create_index('ix_user_replit_user_id', 'user', ['replit_user_id'], unique=True)
    except Exception as e:
        if "already exists" not in str(e):
            raise e

def downgrade():
    # Remove Replit authentication columns from user table
    op.drop_index('ix_user_replit_user_id')
    op.drop_column('user', 'last_login')
    op.drop_column('user', 'replit_user_id')
