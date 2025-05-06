"""Added user_id to events table

Revision ID: 3cc71db0c02f
Revises: 0dd7d777db01
Create Date: 2025-05-03 14:59:06.378197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3cc71db0c02f'
down_revision = '0dd7d777db01'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Create a new table with the desired schema
    op.create_table(
        'new_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('start', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),  # Allow NULL values initially
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_events_user_id')
    )

    # Step 2: Copy data from the old table to the new table, setting a default value for user_id
    op.execute("""
        INSERT INTO new_events (id, title, start, user_id)
        SELECT id, title, start, COALESCE(user_id, 1) FROM events
    """)

    # Step 3: Drop the old table
    op.drop_table('events')

    # Step 4: Rename the new table to the old table name
    op.rename_table('new_events', 'events')

    # Step 5: Enforce NOT NULL constraint on user_id
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('user_id', nullable=False)


def downgrade():
    # Reverse the changes by recreating the original table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('start', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_events_user_id')
    )

    # Copy data back from the new table to the old table
    op.execute("""
        INSERT INTO events (id, title, start, user_id)
        SELECT id, title, start, user_id FROM new_events
    """)

    # Drop the temporary table
    op.drop_table('new_events')