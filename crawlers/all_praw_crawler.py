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

main_write_mode = WriteMode.append

@dataclass
class SchemaConfig:
    name: str
    writemode: Enum
    frames: dict = None
        
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
        all_required_columns = []
        data = data_dicts[schema.name].values()
        log.info(f" {len(data)} {schema.name}")
        schema_sing = schema.name[:-1]
        main_id = f'zen_{schema_sing}_id'
        reddit_id = f'reddit_{schema_sing}_id'
        detail_id = f'zen_{schema_sing}_detail_id'
        version_id = f'zen_{schema_sing}_version_id'
        dirty_df = pd.DataFrame(data).set_index(detail_id)
        
        cleaned_frames, _ = clean_and_normalize(dirty_df, schema.name)
        
        mrd = mydb.most_recent_details(schema.name)
        reddit_ids = cleaned_frames[schema.name][reddit_id]
        needs_entry = reddit_ids.apply(lambda x: x in mrd.reddit_lookup_id)
        needs_entry_indexes = cleaned_frames[schema.name][needs_entry][main_id].reset_index()
        
        target_sources = [(x,x) for x in cleaned_frames.keys()]\
                            + [(schema_sing + '_versions', schema.name),
                               (schema_sing + '_details', schema.name)]
        
        is_append = schema.writemode == WriteMode.append
        
        table_columns = {}
        # change this to parse from ddl to avoid querying the db
        # This parsing of the ddl should also establish which tables
        # are dependent on the details table
        for target, source in target_sources:
            required_columns = mydb.get_target_columns(schema.name, target)
            table_columns[target] = required_columns
            all_required_columns += required_columns
        

        # must be sorted so that things depending on details come last
        main_version_detail_tables = [x for x in target_sources if schema.name == x[1]]
        details_dependent_tables = [x for x in target_sources if schema.name != x[1]]
        target_sources = main_version_detail_tables + details_dependent_tables
        ##
        
        for target, source in target_sources:
            required_columns = table_columns[target]
            df = cleaned_frames[source].reset_index()
            version_1 = df[version_id] == 1
            cols_to_drop = set(df.columns).difference(required_columns)
            cols_to_drop.discard(main_id)
            df.drop(columns = cols_to_drop, inplace = True)
            df_version_1 = df[version_1]
            df_not_version_1 = df[~version_1]
            if is_append: 
                
                if target == schema.name:
                    df = df_version_1
                
                if 'details' in target:
                    seen_details = mrd[mrd[main_id].apply(lambda x: x in df_not_version_1[main_id])]
                    drop_dupes = pd.concat([seen_details[df_not_version_1.columns],df_not_version_1])
                    drop_dupes.drop(columns = detail_id, inplace = True)
                    drop_dupes = drop_dupes.drop_duplicates(keep=False)
                    zen_ids_to_write = set(drop_dupes[main_id])
                    
                    mask = df_not_version_1[main_id].apply(lambda x: x in zen_ids_to_write)
                    df_not_version_1 = df_not_version_1[mask]
                    zen_detail_ids_to_write = df_not_version_1[detail_id].to_list()
                    
                    df = pd.concat([df_version_1,df_not_version_1])
                
                if schema.name not in source:
                    mask = df[detail_id].apply(lambda x: x in zen_detail_ids_to_write)
                    df = df[mask]
            
            cols_to_drop = set(df.columns).difference(required_columns)
            if len(cols_to_drop):
                cols_to_drop_text = '\n'.join(cols_to_drop)
                log.info(f"Dropping from {target}:\n {cols_to_drop_text}")
            log.info(" Writing " + target)

            
            df.drop(columns = cols_to_drop)\
                .to_sql(name = target,
                        schema = schema.name,
                        con = environ['MAIN_MEDIA_DATABASE'], 
                        if_exists = 'append', # DO NOT CHANGE THIS
                        index = False)
            log.info(" Success \n")
        
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
    
    
    
    
