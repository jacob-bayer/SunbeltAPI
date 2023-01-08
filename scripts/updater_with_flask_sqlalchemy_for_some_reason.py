#! /Users/jacob/Documents/github_local/database/venv/bin/python3
# -*- coding: utf-8 -*-

import praw
from os import environ
from dotenv import load_dotenv
from sunbelt.database_helpers.praw_output_cleaner import insert_praw_object
from sunbelt.models import (
                        Post, 
                        PostVersion, 
                        Account,
                        AccountVersion, 
                        Subreddit, 
                        SubredditVersion,
                        Comment, 
                        CommentVersion
                        )            
import logging
import argparse
import signal
from datetime import datetime, timedelta
from static import HOURS_TO_WAIT_DICT
import pytz
east_time = pytz.timezone('US/Eastern')

parser = argparse.ArgumentParser(description="Updater parser")
parser.add_argument("--debug", 
                    help = "Set the log level to debug", 
                    action = 'store_const',
                    const = True,
                    default = False)
parser.add_argument("--suppress_logs", 
                    help = "Suppress logs", 
                    action = 'store_const',
                    const = True,
                    default = False)
args = parser.parse_args()


if args.debug:
    logging.basicConfig(level=logging.DEBUG)
if not args.suppress_logs:
    logging.basicConfig(level=logging.INFO)

load_dotenv()

reddit = praw.Reddit(
    client_id = environ.get('REDDIT_CLIENT_ID'),
    client_secret = environ.get('REDDIT_SECRET_KEY'),
    user_agent ="jacobsapp by jacob087",
    check_for_async = False
)

log = logging.getLogger(f'UPDATER')

post_time = (datetime.now(east_time) - timedelta(hours=HOURS_TO_WAIT_DICT['posts']))
comment_time = (datetime.now(east_time) - timedelta(hours=HOURS_TO_WAIT_DICT['comments']))
subreddit_time = (datetime.now(east_time) - timedelta(hours=HOURS_TO_WAIT_DICT['subreddits']))
account_time = (datetime.now(east_time) - timedelta(hours=HOURS_TO_WAIT_DICT['accounts']))

obj_dict = {
'posts' : Post.query.where(PostVersion.zen_created_at < post_time),
'comments' : Comment.query.where(CommentVersion.zen_created_at < comment_time),
'subreddits' : Subreddit.query.where(SubredditVersion.zen_created_at < subreddit_time),
'accounts' : Account.query.where(AccountVersion.zen_created_at < account_time)
}

praw_dict = {
'posts' : reddit.submission,
'comments' : reddit.comment,
'subreddits' : reddit.subreddit,
'accounts' : reddit.redditor
}

for kind, obj_list in obj_dict.items():
    log.info(f"Updating {len(obj_list)} {kind}")

    for zen_object in obj_list:
        reddit_id = zen_object.reddit_unique_id.split('_')[1]
        praw_object = praw_dict[kind](id = reddit_id)
        insert_praw_object(praw_object)

    log.info(f"Finished updating {kind}")
