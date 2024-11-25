"""add password reset fields

Revision ID: 003
Revises: 002
Create Date: 2024-11-25 08:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # Add password reset fields to user table
    op.add_column('user', sa.Column('password_reset_token', sa.String(64), unique=True, nullable=True))
    op.add_column('user', sa.Column('token_expiry', sa.DateTime, nullable=True))
    op.create_index('ix_user_password_reset_token', 'user', ['password_reset_token'], unique=True)

def downgrade():
    # Remove password reset fields from user table
    op.drop_index('ix_user_password_reset_token')
    op.drop_column('user', 'token_expiry')
    op.drop_column('user', 'password_reset_token')
