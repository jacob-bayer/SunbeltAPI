"""add source_is_pushshift column

Revision ID: 9ac9aa31af5d
Revises: 36ad68ca3490
Create Date: 2023-02-13 20:40:46.660646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ac9aa31af5d'
down_revision = '36ad68ca3490'
branch_labels = None
depends_on = None


def upgrade():
    for item in ['post','comment']:
        table_name = f'{item}_details'
        schema = item + 's'

        op.add_column(schema = schema,
                    table_name = table_name,
                    column = sa.Column('source_is_pushshift', 
                                        sa.Boolean(), 
                                        server_default=sa.text('false'), 
                                        nullable=True))

        with op.batch_alter_table(table_name, schema=schema) as batch_op:
            batch_op.execute(f"UPDATE {schema}.{table_name} SET source_is_pushshift = false")
            batch_op.alter_column('source_is_pushshift', nullable=False)



def downgrade():
    for item in ['post','comment']:
        table_name = f'{item}_details'
        schema = item + 's'
        with op.batch_alter_table(table_name, schema=schema) as batch_op:
            batch_op.drop_column('source_is_pushshift')
