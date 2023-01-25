"""add post comment detail removed

Revision ID: 2c1d23d36916
Revises: 1c419e987838
Create Date: 2023-01-19 15:43:19.163665

"""
from alembic import op
from sqlalchemy import Column, BOOLEAN


# revision identifiers, used by Alembic.
revision = '2c1d23d36916'
down_revision = '1c419e987838'
branch_labels = None
depends_on = None


def upgrade() -> None:

    # add removed and deleted columns
    # populate removed and deleted based on selftext and body

    # each schema's detail table will have a removed and deleted column based on the body or selftext
    kind_sources = {'post':'selftext', 
                    'comment':'body'}

    for kind, source in kind_sources.items():
        for column in ['removed','deleted']:
            
            # add removed and deleted columns
            op.add_column(schema = f'{kind}s',
                          table_name = f'{kind}_details',
                          column = Column(column, BOOLEAN, nullable=True))

            # populate removed and deleted based on selftext and body
            op.execute(f"""
                UPDATE {kind}s.{kind}_details
                SET {column} = {source} = '[{column}]'
            """)

            # make removed and deleted not nullable
            op.alter_column(schema = f'{kind}s',
                            table_name = f'{kind}_details',
                            column_name = column,
                            nullable = False)
            
def downgrade() -> None:
    pass
