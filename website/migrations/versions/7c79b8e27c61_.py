"""empty message

Revision ID: 7c79b8e27c61
Revises: 5316f5990914
Create Date: 2025-05-03 14:09:25.280238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c79b8e27c61'
down_revision = '5316f5990914'
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
        # Now enforce NOT NULL constraint
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)

        # Explicitly name the foreign key constraint
        batch_op.create_foreign_key('fk_events_user_id', 'users', ['user_id'], ['id'])
        
def downgrade():
    # Drop the foreign key constraint and allow NULL values for user_id
    with op.batch_alter_table('events', schema=None) as batch_op:
        # Drop the named foreign key constraint if it exists
        try:
            batch_op.drop_constraint('fk_events_user_id', type_='foreignkey')
        except ValueError:
            print("Constraint 'fk_events_user_id' does not exist. Skipping drop.")

        # Allow NULL values for user_id
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)
        
