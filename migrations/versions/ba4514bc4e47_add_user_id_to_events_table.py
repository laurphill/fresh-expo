"""Add user_id to Events table

Revision ID: ba4514bc4e47
Revises: 7c894f71e9fb
Create Date: 2025-05-03 17:46:09.299535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba4514bc4e47'
down_revision = '7c894f71e9fb'
branch_labels = None
depends_on = None


def upgrade():
        # Modify the 'user_id' column to allow NULL values temporarily
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=True)

    # Set a default value for rows with NULL 'user_id'
    op.execute('UPDATE events SET user_id = 1 WHERE user_id IS NULL')

    # Enforce the NOT NULL constraint on 'user_id'
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=False)


def downgrade():
    # Allow NULL values for 'user_id' during downgrade
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=True)