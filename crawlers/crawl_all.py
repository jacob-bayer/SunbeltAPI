# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd

from mydatabasemodule.praw_output_cleaner import (
                        clean_and_normalize, 
                        has_valid_praw_author,
                        update_existing_object_collection,
                        insert_from_cleaned_frames,
                        SchemaConfig,
                        WriteMode
                        )

import mydatabasemodule.database_helpers as mydb
from datetime import datetime
import logging
import argparse


parser = argparse.ArgumentParser(description="Crawler parser")
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
parser.add_argument("--overwrite", 
                    help = "Overwrite all data. Requires confirmation.",
                    action = 'store_const',
                    const = True,
                    default = False)
args = parser.parse_args()


if args.debug:
    logging.basicConfig(level=logging.DEBUG)
if not args.suppress_logs:
    logging.basicConfig(level=logging.INFO)
    

log = logging.getLogger('CRAWLER')

    
if args.overwrite:
    overwrite_input = input("Type Overwrite to confirm that you want to overwrite:\n\n")
    if overwrite_input == "Overwrite":
        main_write_mode = WriteMode.overwrite
    else:
        raise Exception("Overwrite not confirmed.")
else:
    main_write_mode = WriteMode.append

# This is the hierarchy required
schemas = [SchemaConfig('subreddits', main_write_mode),
           SchemaConfig('accounts', main_write_mode),
           SchemaConfig('posts', main_write_mode),
           SchemaConfig('comments', main_write_mode)]

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
subs_to_read = 'dataisbeautiful'
author_transfer_to_parent = ['is_mod', 'has_subscribed']
total_posts_to_get = 1
post_batch_size = 1
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
        update_existing_object_collection(subreddits, praw_post.subreddit)
        update_existing_object_collection(posts, praw_post)
        
        zen_subreddit = subreddits[praw_post.subreddit.fullname]
        zen_post = posts[praw_post.fullname]
        zen_post['zen_subreddit_id'] = zen_subreddit['zen_subreddit_id']
        
        if has_valid_praw_author(praw_post):
            update_existing_object_collection(accounts, praw_post.author)
            zen_author = accounts[praw_post.author.fullname]
            
            for field in author_transfer_to_parent:
                zen_post['author_' + field] = zen_author.pop(field, None)
                zen_post['zen_account_id'] = zen_author['zen_account_id']

        _ = praw_post.comments.replace_more(limit = 1)
        all_comments = praw_post.comments.list()[:10]
        log.info(f" Fetching {len(all_comments)} comments. (Limited to 10)")
        for praw_comment in all_comments:
            update_existing_object_collection(comments, praw_comment)
            zen_comment = comments[praw_comment.fullname]
            
            if has_valid_praw_author(praw_comment):
                update_existing_object_collection(accounts, praw_comment.author)
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
        all_required_columns = []
        data = data_dicts[schema.name].values()
        log.info(f" {len(data)} {schema.name}")
        detail_id = f'zen_{schema.name[:-1]}_detail_id'

        dirty_df = pd.DataFrame(data).set_index(detail_id)
        
        cleaned_frames, _ = clean_and_normalize(dirty_df, schema.name)
        
        insert_from_cleaned_frames(cleaned_frames, schema)
            
                # this doesn't account for tables that snowflake off of details like 
                # gildings and awardings
                # This is no longer accurate. Fix to be accurate.
    # =============================================================================
    #             no_home = set(cleaned_frames[schema.name].columns).difference(all_required_columns)
    #             if len(no_home):
    #                 log.info(f" The following columns don't belong in {schema.name}:\n {no_home}")
    #                 
    # =============================================================================
    completed = completed + post_batch_size
    
    
    
    
