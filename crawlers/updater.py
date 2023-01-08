#! /Users/jacob/Documents/github_local/database/venv/bin/python3
# -*- coding: utf-8 -*-

import praw
from os import environ
from dotenv import load_dotenv
from database_helpers.praw_output_cleaner import insert_praw_object         
import logging
import argparse
from datetime import datetime, timedelta
from static import HOURS_TO_WAIT_DICT
import pytz
import json
import requests

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

sunbelt = SunbeltClient("http://127.0.0.1:5000/graphql")

log = logging.getLogger('UPDATER')

now_et = datetime.now(east_time)

post_time = (now_et - timedelta(hours=HOURS_TO_WAIT_DICT['posts'])).strftime("%d-%m-%Y %H:%M:%S")
comment_time = (now_et - timedelta(hours=HOURS_TO_WAIT_DICT['comments'])).strftime("%d-%m-%Y %H:%M:%S")
subreddit_time = (now_et - timedelta(hours=HOURS_TO_WAIT_DICT['subreddits'])).strftime("%d-%m-%Y %H:%M:%S")
account_time = (now_et - timedelta(hours=HOURS_TO_WAIT_DICT['accounts'])).strftime("%d-%m-%Y %H:%M:%S")

praw_funcs = {
    'posts' : reddit.submission,
    'comments' : reddit.comment,
    'subreddits' : reddit.subreddit,
    'accounts' : reddit.redditor
    }

for kind, hours_to_wait in HOURS_TO_WAIT_DICT.items():
    age_cutoff = now_et - timedelta(hours=hours_to_wait)
    age_cutoff = age_cutoff.strftime("%d-%m-%Y %H:%M:%S")
    
    ids_to_check = sunbelt.search(kind, 'reddit_unique_id', updated_before = age_cutoff)
    ids_to_check = [x['reddit_unique_id'].split('_')[1] for x in ids_to_check]
    
    log.info(f" Updating {len(ids_to_check)} {kind}")
    
    praw_func = praw_funcs[kind]
    for reddit_id in ids_to_check:
        praw_object = praw_func(id=reddit_id)
        insert_praw_object(praw_object)
    

