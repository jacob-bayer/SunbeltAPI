#! ./venv/bin/python3
# -*- coding: utf-8 -*-

import praw
from os import environ
from dotenv import load_dotenv
#from database_helpers.praw_output_cleaner import insert_praw_object         
import logging
import argparse
from datetime import datetime, timedelta
#from static import HOURS_TO_WAIT_DICT
HOURS_TO_WAIT_DICT = {'subreddits': 24,
                        'accounts': 24,
                        'posts': 1,
                        'comments': 0.25}

import pytz
from SAWP import SunbeltClient

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
    client_id = environ['REDDIT_CLIENT_ID'],
    client_secret = environ['REDDIT_SECRET_KEY'],
    user_agent = "jacobsapp by jacob087",
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

sunbelt_funcs = {
    'posts' : sunbelt.posts,
    'comments' : sunbelt.comments,
    'subreddits' : sunbelt.subreddits,
    'accounts' : sunbelt.accounts
    }

for kind, hours_to_wait in HOURS_TO_WAIT_DICT.items():
    sunbelt_func = sunbelt_funcs[kind]
    
    age_cutoff = now_et - timedelta(hours=hours_to_wait)
    age_cutoff = age_cutoff.strftime("%d-%m-%Y %H:%M:%S")
    


    zen_objs = sunbelt_func.all(updated_before = age_cutoff)

    zen_objs = list(zen_objs)

    log.info(f" Updating {len(zen_objs)} {kind}")
    
    praw_func = praw_funcs[kind]

    for zen_obj in zen_objs:
        if kind == 'subreddits':
            identifier = zen_obj.display_name
        elif kind == 'accounts':
            identifier = zen_obj.name
        else:
            identifier = zen_obj.reddit_unique_id

        praw_object = praw_func(identifier)
        praw_object._fetch()
        
        
        
    

