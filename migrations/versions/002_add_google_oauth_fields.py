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
    # Add Google OAuth columns to user table with error handling
    try:
        # Add columns one by one with error handling
        for column in [
            ('google_id', sa.String(256), True),
            ('google_profile_pic', sa.String(512), True),
            ('google_email_verified', sa.Boolean(), False)
        ]:
            try:
                if len(column) == 3:
                    op.add_column('user', sa.Column(
                        column[0], 
                        column[1], 
                        nullable=column[2],
                        server_default='false' if column[0] == 'google_email_verified' else None
                    ))
            except Exception as e:
                if "already exists" not in str(e):
                    raise e
    except Exception as e:
        if "already exists" not in str(e):
            raise e

def downgrade():
    # Remove Google OAuth columns from user table
    op.drop_column('user', 'google_email_verified')
    op.drop_column('user', 'google_profile_pic')
    op.drop_column('user', 'google_id')
