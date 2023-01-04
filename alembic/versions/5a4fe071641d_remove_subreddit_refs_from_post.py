"""remove subreddit refs from post

Revision ID: 5a4fe071641d
Revises: 
Create Date: 2023-01-04 07:23:18.845932

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5a4fe071641d'
down_revision = None
branch_labels = None
depends_on = None

cols_to_drop = ['subreddit_name_prefixed',
                'subreddit_type']

def upgrade() -> None:
    for col in cols_to_drop:
        op.drop_column(schema = 'posts', 
                       table_name = 'posts',
                       column_name = col)


def downgrade() -> None:
    for col in cols_to_drop:
        op.add_column(schema = 'posts', 
                      table_name = 'posts',
                      column = sa.Column(col, sa.Text))
        
        
