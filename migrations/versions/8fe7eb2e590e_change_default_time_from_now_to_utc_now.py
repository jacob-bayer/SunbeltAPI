"""change default time from now to utc now

Revision ID: 8fe7eb2e590e
Revises: 020cc051a254
Create Date: 2023-02-03 11:59:22.085552

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fe7eb2e590e'
down_revision = '020cc051a254'
branch_labels = None
depends_on = None

schemas = ['post','subreddit','account','comment']
# using schemas list, generate a dictionary with table names as keys and a list of column names as values
schema_tables = {schema + 's': [f'{schema}s', f'{schema}_versions', f'{schema}_details'] for schema in schemas}

def upgrade():
    
    # iterate through the dictionary and alter the column for each table in each schema 
    # to use the utc now function as the default value instead of now
    for schema, tables in schema_tables.items():
        for table in tables:
            with op.batch_alter_table(table, schema=schema) as batch_op:
                batch_op.alter_column('sun_created_at', 
                            server_default=sa.text('now() at time zone \'utc\''))

  

def downgrade():
    # iterate through the dictionary and alter the column for each table in each schema 
    # to use the now function as the default value instead of utc now
    for schema, tables in schema_tables.items():
        for table in tables:
            with op.batch_alter_table(table, schema=schema) as batch_op:
                batch_op.alter_column('sun_created_at', 
                            server_default=sa.text('now()'))