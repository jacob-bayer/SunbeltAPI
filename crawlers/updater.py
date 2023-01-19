#! ./venv/bin/python3
# -*- coding: utf-8 -*-

import json
from os import environ
import logging
import argparse
from datetime import datetime, timedelta
import pytz

import praw
from dotenv import load_dotenv
#from database_helpers.praw_output_cleaner import insert_praw_object         

#from static import HOURS_TO_WAIT_DICT
HOURS_TO_WAIT_DICT = {'subreddit': 24,
                        'account': 24,
                        'post': 1,
                        'comment': 0.25}


from SAWP import SunbeltClient
from praw_cleaner.praw_to_dict import praw_to_dict


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

post_time = (now_et - timedelta(hours=HOURS_TO_WAIT_DICT['post'])).strftime("%d-%m-%Y %H:%M:%S")
comment_time = (now_et - timedelta(hours=HOURS_TO_WAIT_DICT['comment'])).strftime("%d-%m-%Y %H:%M:%S")
subreddit_time = (now_et - timedelta(hours=HOURS_TO_WAIT_DICT['subreddit'])).strftime("%d-%m-%Y %H:%M:%S")
account_time = (now_et - timedelta(hours=HOURS_TO_WAIT_DICT['account'])).strftime("%d-%m-%Y %H:%M:%S")

praw_funcs = {
    'post' : reddit.submission,
    'comment' : reddit.comment,
    'subreddit' : reddit.subreddit,
    'account' : reddit.redditor
    }

sunbelt_funcs = {
    'post' : sunbelt.posts,
    'comment' : sunbelt.comments,
    'subreddit' : sunbelt.subreddits,
    'account' : sunbelt.accounts
    }

for kind, hours_to_wait in HOURS_TO_WAIT_DICT.items():
    write_list = []
    
    sunbelt_func = sunbelt_funcs[kind]
    
    age_cutoff = now_et - timedelta(hours=hours_to_wait)
    age_cutoff = age_cutoff.strftime("%d-%m-%Y %H:%M:%S")
    


    zen_objs = sunbelt_func.all(updatedBefore = age_cutoff)

    zen_objs = list(zen_objs)
    
    praw_func = praw_funcs[kind]
    
    for zen_obj in zen_objs:
        
        is_subreddit = kind == 'subreddit'
        is_account = kind == 'account'
        is_comment = kind == 'comment'
        is_post = kind == 'post'
        
        if is_subreddit:
            identifier = zen_obj.display_name
        elif is_account:
            identifier = zen_obj.name
        else:
            identifier = zen_obj.reddit_unique_id.split('_')[1]

        praw_object = praw_func(identifier)
        praw_dict = praw_to_dict(praw_object)
        praw_json = json.dumps(praw_dict)
        
        if is_comment or is_post:
            thresh = min(praw_object.ups*.05,100)
            diff = zen_obj.most_recent_ups - praw_object.ups
        elif is_subreddit:
            thresh = min(praw_object.subscribers*.01,1000)
            diff = zen_obj.most_recent_subscribers - praw_object.subscribers
        elif is_account:
            thresh = min(praw_object.total_karma*.01,100)
            diff = zen_obj.most_recent_total_karma - praw_object.total_karma
        
        should_write = diff > thresh
        if should_write:
            write_list += praw_json
        
    
    if len(write_list):
        log.info(f' Updating {len(write_list)} {kind}s')
    
    for praw_json in write_list:
        mutation_type = f'create{kind.title()}'
        sunbelt.mutation(mutation_type, praw_json)
