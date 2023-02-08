"""change suspended to is_suspended

Revision ID: 36ad68ca3490
Revises: 8fe7eb2e590e
Create Date: 2023-02-03 16:13:44.611318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36ad68ca3490'
down_revision = '8fe7eb2e590e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(schema = 'accounts',
                table_name = 'account_details',
                column = sa.Column('is_suspended', 
                                    sa.Boolean(), 
                                    server_default=sa.text('false'), 
                                    nullable=True))

    with op.batch_alter_table('account_details', schema='accounts') as batch_op:
        batch_op.execute("UPDATE accounts.account_details SET is_suspended = suspended")
        batch_op.drop_column('suspended')
        batch_op.alter_column('is_suspended', nullable=False)


def downgrade():
    op.add_column(schema = 'accounts',
                table_name = 'account_details',
                column = sa.Column('suspended', 
                                    sa.Boolean(), 
                                    server_default=sa.text('false'), 
                                    nullable=True))

    with op.batch_alter_table('account_details', schema='accounts') as batch_op:
        batch_op.execute("UPDATE accounts.account_details SET suspended = is_suspended")
        batch_op.drop_column('is_suspended')
        batch_op.alter_column('suspended', nullable=False)
