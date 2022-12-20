# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd

from mydatabasemodule.praw_output_cleaner import (
                        clean_and_normalize, 
                        has_valid_praw_author,
                        set_default_zen_vars
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
schemas = [SchemaConfig('subreddits', WriteMode.append),
           SchemaConfig('accounts', WriteMode.append),
           SchemaConfig('posts', WriteMode.append),
           SchemaConfig('comments', WriteMode.append)]

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
author_transfer_to_parent = ['is_mod', 'has_subscribed']
total_posts_to_get = 10
post_batch_size = 10
completed = 0
start_time = datetime.now()
params = {}
while completed < total_posts_to_get:
    subreddits = {}
    accounts = {}
    comments = {}
    posts = {}
    log.info(f' Reading {post_batch_size} posts')
    api_query = reddit.subreddit(subs_to_read)\
                      .top(limit = post_batch_size, # hot not top
                           time_filter = 'week',
                           params = params)
                      

    for praw_post in api_query:
        set_default_zen_vars(subreddits, praw_post.subreddit)
        set_default_zen_vars(posts, praw_post)
        
        zen_subreddit = subreddits[praw_post.subreddit.fullname]
        zen_post = posts[praw_post.fullname]
        zen_post['zen_subreddit_id'] = zen_subreddit['zen_subreddit_id']
        
        if has_valid_praw_author(praw_post):
            set_default_zen_vars(accounts, praw_post.author)
            zen_author = accounts[praw_post.author.fullname]
            
            for field in author_transfer_to_parent:
                zen_post['author_' + field] = zen_author.pop(field, None)
                zen_post['zen_account_id'] = zen_author['zen_account_id']

        _ = praw_post.comments.replace_more(limit = None)
        all_comments = praw_post.comments.list()
        log.info(f" Fetching {len(all_comments)} comments.")
        for praw_comment in all_comments:
            set_default_zen_vars(comments, praw_comment)
            zen_comment = comments[praw_comment.fullname]
            
            if has_valid_praw_author(praw_comment):
                set_default_zen_vars(accounts, praw_comment.author)
                zen_author = accounts[praw_comment.author.fullname]
                
                for field in author_transfer_to_parent:
                    zen_comment['author_' + field] = zen_author.pop(field, None)
            
                zen_comment['zen_account_id'] = zen_author['zen_account_id']
                
            zen_comment['zen_post_id'] = zen_post['zen_post_id']
            zen_comment['zen_subreddit_id'] = zen_post['zen_subreddit_id']

    
    ##############
    batch_reading_time = datetime.now() - start_time
    params = {'after': praw_post.fullname}
    
    data_dicts = {'subreddits':subreddits,
                  'accounts': accounts,
                  'posts': posts,
                  'comments': comments}
    
    dataframes = {}
    for schema in schemas:
        data = data_dicts[schema.name].values()
        log.info(f" {len(data)} {schema}")
        schema_sing = schema.name[:-1]
        detail_id = f'zen_{schema_sing}_detail_id'
        dirty_df = pd.DataFrame(data).set_index(detail_id)
        
        cleaned_frames, _ = clean_and_normalize(dirty_df, schema.name)
        
        target_sources = [(x,x) for x in cleaned_frames.keys()]\
                            + [(schema_sing + '_versions', schema.name),
                               (schema_sing + '_details', schema.name)]
        
        is_append = schema.writemode == WriteMode.append
            
        all_required_columns = []
        for target, source in target_sources:
            if not (target == schema.name and is_append):
                df = cleaned_frames[source].reset_index()
                required_columns = mydb.get_target_columns(schema.name, target)
                all_required_columns += required_columns
                cols_to_drop = set(df.columns).difference(required_columns)
                df = df.drop(columns = cols_to_drop)
            
                
                ## remove from here...
                final_target_columns = mydb.get_target_columns(schema.name, target)
                cols_to_drop = set(df.columns).difference(final_target_columns)
                if len(cols_to_drop):
                    cols_to_drop_text = '\n'.join(cols_to_drop)
                    log.info(f"Dropping from {target}:\n {cols_to_drop_text}")
                log.info(" Writing " + target)
                ## ...to here when breaking up into details, versions, and main
                ## Possibly keep a log statement indicating the 
                ## columns that were dropped
                
                if mydb.difference_in_existing(df, schema.name, target):
                    df.drop(columns = cols_to_drop)\
                        .to_sql(name = target,
                                schema = schema.name,
                                con = environ['MAIN_MEDIA_DATABASE'], 
                                if_exists = 'append', # DO NOT CHANGE THIS
                                index = False)
                log.info(" Success \n")
        
            # this doesn't account for tables that snowflake off of details like 
            # gildings and awardings
            no_home = set(cleaned_frames[schema.name].columns).difference(all_required_columns)
            if len(no_home):
                log.info(f" The following columns don't belong in {schema.name}:\n {no_home}")
                
    completed = completed + post_batch_size
    
    
    
    
