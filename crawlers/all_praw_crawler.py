# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd

from mydatabasemodule.praw_output_cleaner import (
                        clean_and_normalize, 
                        has_valid_praw_author,
                        append_praw_object_vars_to_list
                        )

import mydatabasemodule.database_helpers as mydb
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import time
import logging
import argparse


parser = argparse.ArgumentParser(description="Crawler parser")
parser.add_argument("--debug", 
                    help = "Set the log level to debug", 
                    action = 'store_const',
                    const = True,
                    default = False)
parser.add_argument("--suppress_logs", 
                    help = "Set the log level to debug", 
                    action = 'store_const',
                    const = True,
                    default = False)

args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
if not args.suppress_logs:
    logging.basicConfig(level=logging.INFO)
    

log = logging.getLogger('CRAWLER')

WriteMode = Enum('WriteMode', ['overwrite','append'])

@dataclass
class SchemaConfig:
    name: str
    writemode: Enum
    frames: dict = None
        
# This is the hierarchy required
schemas = [SchemaConfig('subreddits', WriteMode.overwrite),
           SchemaConfig('accounts', WriteMode.overwrite),
           SchemaConfig('posts', WriteMode.overwrite),
           SchemaConfig('comments', WriteMode.overwrite)]

load_dotenv()

reddit = praw.Reddit(
    client_id = environ.get('REDDIT_CLIENT_ID'),
    client_secret = environ.get('REDDIT_SECRET_KEY'),
    user_agent ="jacobsapp by jacob087",
    check_for_async = False
)

    
for schema in schemas:
    if schema.writemode == WriteMode.overwrite:
        mydb.regen_schema(schema.name)


# This is actually going to be dev data so it will
# pull hot posts from a moderately active subreddit instead of all
# This will ensure that all data is real but not overwhelming to pull
subs_to_read = 'pushshift'
author_sub_context_fields = ['is_mod', 'has_subscribed']
total_posts_to_get = 10
post_batch_size = 10
completed = 0
start_time = datetime.now()
params = {}
while completed < total_posts_to_get:
    seen_subreddits = []
    subreddits = []
    seen_accounts = []
    accounts = []
    comments = []
    posts = []
    log.info(f' Reading {post_batch_size} posts')
    api_query = reddit.subreddit(subs_to_read)\
                      .top(limit = post_batch_size, # hot not top
                           time_filter = 'week',
                           params = params)
    

    for post in api_query:
        if post.subreddit.fullname not in seen_subreddits:
            append_praw_object_vars_to_list(post.subreddit, subreddits)
            seen_subreddits.append(post.subreddit.fullname)
            
        append_praw_object_vars_to_list(post, posts)
        posts[-1]['zen_subreddit_id'] = subreddits[-1]['zen_subreddit_id']
        
        if has_valid_praw_author(post):
            if post.author.fullname not in seen_accounts:
                append_praw_object_vars_to_list(post.author, accounts)
                seen_accounts.append(post.author.fullname)
                for field in author_sub_context_fields:
                    posts[-1]['author_'+field] = accounts[-1].pop(field, None)
            

        _ = post.comments.replace_more(limit = None)
        all_comments = post.comments.list()
        log.info(f"Fetching {len(all_comments)} comments.")
        for comment in all_comments:
            append_praw_object_vars_to_list(comment, comments)
            
            if has_valid_praw_author(comment):
                append_praw_object_vars_to_list(comment.author, accounts)
                for field in author_sub_context_fields:
                    comments[-1]['author_' + field] = accounts[-1].pop(field, None)
            
            comments[-1]['zen_post_id'] = posts[-1]['zen_post_id']


    
    ##############
    batch_reading_time = datetime.now() - start_time
    params = {'after': post.name}
    
    data_dicts = [('subreddits', subreddits),
                    ('posts', posts),
                    ('accounts', accounts),
                    ('comments', comments)]
    
    dataframes = {}
    for obj_name, data in data_dicts:
        log.info(f" {len(data)} {obj_name}")
        obj_name_sing = obj_name[:-1]
        main_id = f'zen_{obj_name_sing}_id'
        dirty_df = pd.DataFrame(data).set_index(main_id)
        
        cleaned_frames, _ = clean_and_normalize(dirty_df, obj_name)
        
        for table, df in cleaned_frames.items():
            target_cols = mydb.get_target_columns(obj_name, table)
            cols_to_drop = set(df.columns).difference(target_cols)
            if len(cols_to_drop):
                cols_to_drop_text = '\n'.join(cols_to_drop)
                log.info(f"Dropping from {table}:\n {cols_to_drop_text}")
            log.info(" Writing " + table)
            df['zen_modified_at'] = datetime.now()
            df.drop(columns = cols_to_drop)\
                .to_sql(name = table,
                        schema = obj_name,
                        con = environ['MAIN_MEDIA_DATABASE'], 
                        if_exists = 'append', # DO NOT CHANGE THIS
                        index = True)
            log.info("Success \n")
    
    completed = completed + post_batch_size
    
    
    
    
