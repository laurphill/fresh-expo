"""empty message

Revision ID: b2df353b7b41
Revises: 7c79b8e27c61
Create Date: 2025-05-03 14:12:45.842043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2df353b7b41'
down_revision = '7c79b8e27c61'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('events', schema=None) as batch_op:
        # Temporarily allow NULL values for user_id
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)

    # Set a default value for existing rows (e.g., assign all events to user_id=1)
    op.execute('UPDATE events SET user_id = 1 WHERE user_id IS NULL')

    with op.batch_alter_table('events', schema=None) as batch_op:
        # Drop the foreign key constraint if it exists
        batch_op.drop_constraint('fk_events_user_id', type_='foreignkey', if_exists=True)

        # Now enforce NOT NULL constraint
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)

        # Explicitly name the foreign key constraint
        batch_op.create_foreign_key('fk_events_user_id', 'users', ['user_id'], ['id'])

def downgrade():
    with op.batch_alter_table('events', schema=None) as batch_op:
        # Drop the named foreign key constraint
        batch_op.drop_constraint('fk_events_user_id', type_='foreignkey')
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)