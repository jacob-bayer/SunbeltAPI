"""add reddit unique index

Revision ID: da13d58916b5
Revises: 19d4e2826f8b
Create Date: 2023-02-21 10:56:09.196377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da13d58916b5'
down_revision = '19d4e2826f8b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('accounts', schema='accounts') as batch_op:
        batch_op.alter_column('reddit_account_id',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.create_index(batch_op.f('ix_accounts_accounts_reddit_account_id'), ['reddit_account_id'], unique=False)

    with op.batch_alter_table('comments', schema='comments') as batch_op:
        batch_op.create_index(batch_op.f('ix_comments_comments_reddit_comment_id'), ['reddit_comment_id'], unique=False)

    with op.batch_alter_table('posts', schema='posts') as batch_op:
        batch_op.create_index(batch_op.f('ix_posts_posts_reddit_post_id'), ['reddit_post_id'], unique=False)

    with op.batch_alter_table('subreddits', schema='subreddits') as batch_op:
        batch_op.create_index(batch_op.f('ix_subreddits_subreddits_reddit_subreddit_id'), ['reddit_subreddit_id'], unique=False)



def downgrade():
    with op.batch_alter_table('subreddits', schema='subreddits') as batch_op:
        batch_op.drop_index(batch_op.f('ix_subreddits_subreddits_reddit_subreddit_id'))

    with op.batch_alter_table('posts', schema='posts') as batch_op:
        batch_op.drop_index(batch_op.f('ix_posts_posts_reddit_post_id'))

    with op.batch_alter_table('comments', schema='comments') as batch_op:
        batch_op.drop_index(batch_op.f('ix_comments_comments_reddit_comment_id'))

    with op.batch_alter_table('accounts', schema='accounts') as batch_op:
        batch_op.drop_index(batch_op.f('ix_accounts_accounts_reddit_account_id'))
        batch_op.alter_column('reddit_account_id',
               existing_type=sa.TEXT(),
               nullable=True)

