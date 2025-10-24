"""Initial migration - baseline schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-10-24 07:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create user table
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=True),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    
    # Create property table
    op.create_table('property',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=200), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('property_type', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create review table
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('reviewer_name', sa.String(length=100), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('review_text', sa.Text(), nullable=True),
    sa.Column('landlord_name', sa.String(length=100), nullable=True),
    sa.Column('landlord_rating', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['property_id'], ['property.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on review.user_id
    op.create_index('idx_review_user_id', 'review', ['user_id'], unique=False)
    
    # Create photo table
    op.create_table('photo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('review_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('filepath', sa.String(length=500), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['review_id'], ['review.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create translation table
    op.create_table('translation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('original_text', sa.Text(), nullable=False),
    sa.Column('source_lang', sa.String(length=10), nullable=False),
    sa.Column('target_lang', sa.String(length=10), nullable=False),
    sa.Column('translated_text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on translation lookup
    op.create_index('idx_translation_lookup', 'translation', ['original_text', 'source_lang', 'target_lang'], unique=False)


def downgrade():
    # Drop all tables in reverse order
    op.drop_index('idx_translation_lookup', table_name='translation')
    op.drop_table('translation')
    op.drop_table('photo')
    op.drop_index('idx_review_user_id', table_name='review')
    op.drop_table('review')
    op.drop_table('property')
    op.drop_table('user')
