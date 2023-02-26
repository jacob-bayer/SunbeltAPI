"""add epoch timestamp

Revision ID: 581822d8495e
Revises: 
Create Date: 2023-02-25 12:51:53.167945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '581822d8495e'
down_revision = None
branch_labels = None
depends_on = None

# list of the tables and their schemas that need to be updated
tables = [
    ('account_details', 'accounts'),
    ('accounts', 'accounts'),
    ('comment_details', 'comments'),
    ('comments', 'comments'),
    ('post_details', 'posts'),
    ('posts', 'posts'),
    ('subreddit_details', 'subreddits'),
    ('subreddits', 'subreddits')
]

def upgrade():
    for table_schema in tables:
        table = table_schema[0]
        schema = table_schema[1]
        with op.batch_alter_table(table, schema=schema) as batch_op:
            batch_op.add_column(sa.Column('sun_created_at_epoch', sa.BigInteger(), server_default=sa.text("extract(epoch from timezone('utc', now()))::INTEGER"), nullable=True))
        
        with op.batch_alter_table(table, schema=schema) as batch_op:
            batch_op.execute(f"UPDATE {schema}.{table} SET sun_created_at_epoch = extract(epoch from sun_created_at)::INTEGER")
            batch_op.alter_column('sun_created_at_epoch', nullable=False)


def downgrade():
    for table_schema in tables:
        table = table_schema[0]
        schema = table_schema[1]
        with op.batch_alter_table(table, schema=schema) as batch_op:
            batch_op.drop_column('sun_created_at_epoch')