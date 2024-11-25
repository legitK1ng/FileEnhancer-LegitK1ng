"""add batch processing status

Revision ID: 001
Revises: 
Create Date: 2024-11-25 07:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    try:
        # Add columns one by one with error handling
        for column in [
            ('batch_id', sa.String(36)),
            ('processing_status', sa.String(20)),
            ('processing_started_at', sa.DateTime),
            ('processing_completed_at', sa.DateTime),
            ('processing_error', sa.Text)
        ]:
            try:
                op.add_column('file_metadata', sa.Column(column[0], column[1], nullable=True))
            except Exception as e:
                if "already exists" not in str(e):
                    raise e
                
        # Create index if it doesn't exist
        try:
            op.create_index('ix_file_metadata_batch_id', 'file_metadata', ['batch_id'])
        except Exception as e:
            if "already exists" not in str(e):
                raise e
    except Exception as e:
        if "already exists" not in str(e):
            raise e

def downgrade():
    op.drop_index('ix_file_metadata_batch_id')
    op.drop_column('file_metadata', 'processing_error')
    op.drop_column('file_metadata', 'processing_completed_at')
    op.drop_column('file_metadata', 'processing_started_at')
    op.drop_column('file_metadata', 'processing_status')
    op.drop_column('file_metadata', 'batch_id')
