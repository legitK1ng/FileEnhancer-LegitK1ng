"""add google oauth fields

Revision ID: 002
Revises: 001
Create Date: 2024-11-25 07:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Add Google OAuth columns to user table
    op.add_column('user', sa.Column('google_id', sa.String(256), unique=True, nullable=True))
    op.add_column('user', sa.Column('google_profile_pic', sa.String(512), nullable=True))
    op.add_column('user', sa.Column('google_email_verified', sa.Boolean(), server_default='false', nullable=False))

def downgrade():
    # Remove Google OAuth columns from user table
    op.drop_column('user', 'google_email_verified')
    op.drop_column('user', 'google_profile_pic')
    op.drop_column('user', 'google_id')
