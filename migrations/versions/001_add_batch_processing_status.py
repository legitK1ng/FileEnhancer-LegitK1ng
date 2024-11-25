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
    op.add_column('file_metadata', sa.Column('batch_id', sa.String(36), nullable=True))
    op.add_column('file_metadata', sa.Column('processing_status', sa.String(20), nullable=True))
    op.add_column('file_metadata', sa.Column('processing_started_at', sa.DateTime, nullable=True))
    op.add_column('file_metadata', sa.Column('processing_completed_at', sa.DateTime, nullable=True))
    op.add_column('file_metadata', sa.Column('processing_error', sa.Text, nullable=True))
    op.create_index('ix_file_metadata_batch_id', 'file_metadata', ['batch_id'])

def downgrade():
    op.drop_index('ix_file_metadata_batch_id')
    op.drop_column('file_metadata', 'processing_error')
    op.drop_column('file_metadata', 'processing_completed_at')
    op.drop_column('file_metadata', 'processing_started_at')
    op.drop_column('file_metadata', 'processing_status')
    op.drop_column('file_metadata', 'batch_id')
