"""empty message

Revision ID: 11425ee6092b
Revises: b2df353b7b41
Create Date: 2025-05-03 14:16:53.455259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11425ee6092b'
down_revision = 'b2df353b7b41'
branch_labels = None
depends_on = None


def upgrade():
    # Temporarily allow NULL values for user_id
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)

    # Set a default value for existing rows (e.g., assign all events to user_id=1)
    op.execute('UPDATE events SET user_id = 1 WHERE user_id IS NULL')

    # Enforce NOT NULL constraint and add the foreign key constraint
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)
        batch_op.create_foreign_key('fk_events_user_id', 'users', ['user_id'], ['id'])

def downgrade():
    # Drop the foreign key constraint and allow NULL values for user_id
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_constraint('fk_events_user_id', type_='foreignkey')
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)