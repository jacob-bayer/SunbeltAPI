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
HOURS_TO_WAIT_DICT = {'subreddit': 24,
                        'account': 24,
                        'post': 1,
                        'comment': 0.25}

import pytz
from SAWP import SunbeltClient
import pandas as pd
from database_helpers.praw_output_cleaner import (
                        clean_and_normalize,
                        insert_from_cleaned_frames,
                        SchemaConfig)

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
    sunbelt_func = sunbelt_funcs[kind]
    
    age_cutoff = now_et - timedelta(hours=hours_to_wait)
    age_cutoff = age_cutoff.strftime("%d-%m-%Y %H:%M:%S")
    


    zen_objs = sunbelt_func.all(updatedBefore = age_cutoff)

    zen_objs = list(zen_objs)

    log.info(f" Updating {len(zen_objs)} {kind}s")
    
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
        obj_vars = vars(praw_object)
        obj_vars[f'zen_{kind}_id'] = zen_obj.zen_unique_id
        obj_vars[f'zen_{kind}_version_id'] = zen_obj.most_recent_zen_version_id + 1
        obj_vars[f'zen_{kind}_detail_id'] = max(sunbelt.post_details.zen_detail_id) + 1
        df = pd.DataFrame([obj_vars]).set_index(f'zen_{kind}_detail_id')
        cleaned_frames, _ = clean_and_normalize(df, kind + 's')
        insert_from_cleaned_frames(cleaned_frames, SchemaConfig(kind + 's'))
        
    

