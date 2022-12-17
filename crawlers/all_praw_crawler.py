# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_and_normalize, has_valid_praw_author
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


top_subs = ['AskReddit',
             'worldnews',
             'news',
             'Unexpected',
             'videos',
             'wallstreetbets',
             'PublicFreakout',
             'mildlyinteresting',
             'WhitePeopleTwitter',
             'funny',
             'politics',
             'Damnthatsinteresting',
             'pics',
             'MadeMeSmile',
             'facepalm',
             'movies',
             'todayilearned',
             'technology',
             'nextfuckinglevel',
             'gaming',
             'memes',
             'IdiotsInCars',
             'interestingasfuck',
             'tifu',
             'dankmemes',
             'aww',
             'science',
             'Wellthatsucks',
             'LifeProTips',
             'WatchPeopleDieInside',
             'oddlysatisfying',
             'teenagers',
             'wholesomememes',
             'comics',
             'PrequelMemes',
             'Futurology',
             'dataisbeautiful',
             'assholedesign',
             'LeopardsAteMyFace',
             'Showerthoughts',
             'DunderMifflin',
             'EarthPorn',
             'books',
             'space',
             'trashy',
             'me_irl',
             'awfuleverything',
             'gifs',
             'IAmA',
             'Music',
             'rickandmorty',
             'nottheonion',
             'freefolk',
             'BikiniBottomTwitter',
             'MurderedByWords',
             'JusticeServed',
             'PewdiepieSubmissions',
             'announcements',
             'StarWarsBattlefront',
             'thanosdidnothingwrong',
             'MemeEconomy']

subs_to_read = '+'.join(top_subs)

# This is actually going to be dev data so it will
# pull hot posts from a moderately active subreddit instead of all
# This will ensure that all data is real but not overwhelming to pull
subs_to_read = 'datascience'

total_posts_to_get = 3
post_batch_size = 3
completed = 0
start_time = datetime.now()
params = {}
subreddits = []
accounts = []
while completed < total_posts_to_get:
    comments = []
    posts = []
    log.info(f' Reading {post_batch_size} posts')
    api_query = reddit.subreddit(subs_to_read)\
                      .hot(limit = post_batch_size, # hot not top
                           #time_filter = 'all',
                           params = params)
    

    for post in api_query:
        subreddit = post.subreddit
        
        zen_post_ids = mydb.get_id_params(
                        post.fullname, 'posts', 
                        existing_id_collection = posts)
        
        zen_subreddit_ids = mydb.get_id_params(
                            subreddit.fullname,
                            'subreddits',
                            existing_id_collection = subreddits)
        
        post_vars = vars(post)
        # is there user data in the sub vars that is needed?
        # cases where 'user' in sub_vars key
        sub_vars = vars(subreddit)
        sub_vars.update(zen_subreddit_ids)
        
        if has_valid_praw_author(post):
            zen_account_id = mydb.get_id_params(
                                post.author.fullname, 'accounts', 
                                existing_id_collection = accounts)
            post_account_vars = vars(post.author)
            post_account_vars.update(zen_account_id)
            post_vars.update({'author_subscribed' : post_account_vars['has_subscribed'],
                              'author_is_mod': post_account_vars['is_mod']})
              


        # All objects need to reach the fetched
        # state so that all the vars are available.
        # This is achieved by calling any attribute of the
        # object that is not available in the basic vars (such as url).
        # For posts this is acheived by replace more
        
        # https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
        current_time = datetime.now().strftime("%b-%d %-I:%M:%S %p")
        log.info(f" Replacing comments for post. Started at {current_time}. This may take a while.")
        _ = post.comments.replace_more(limit = None)
        # not calling list leaves out some comments somehow
        # all replies to comments (all comments total) will be included here
        current_time = datetime.now().strftime("%b-%d %-I:%M:%S %p")
        log.info(f" Finished replacing comments at {current_time}.")
        
        
        # Posts have a parent id and crosspost count so no real need to get these
        #crossposts = crossposts + [vars(x) for x in post.duplicates()]
        
      


        ## Comments ##
        log.info("Iterating comments.")
        comments_added = 0
        for comment in post.comments.list():
            comment_vars = vars(comment)
            
            zen_comment_ids = mydb.get_id_params(
                                comment.fullname, 
                                'comments', 
                                existing_id_collection = comments)
           
            
            if has_valid_praw_author(comment):
                zen_account_ids = mydb.get_id_params(
                                    comment.author.fullname, 
                                    'accounts', 
                                    existing_id_collection = accounts)
               
                comment_account_vars = vars(comment.author)
                zen_account_ids['reddit_account_id'] = 't2_' + comment_account_vars['id']
                comment_account_vars.update(zen_account_ids)
                comment_vars['author_subscribed'] = comment_account_vars['has_subscribed']
                comment_vars['author_is_mod'] = comment_account_vars['is_mod']
                zen_comment_ids['zen_account_id'] = zen_account_ids['zen_account_id']
                
            comment_vars.update(zen_comment_ids)
            comments.append(comment_vars)
            comments_added += 1
            
        #log.info('Sleeping 30 secs between posts')
        #time.sleep(30)
        
    ##############
    batch_reading_time = datetime.now() - start_time
    params = {'after': post.name}
    log.info(f"{len(posts)} posts")
    log.info(f"{len(comments)} comments")
    log.info(f"{len(subreddits)} subreddits")
    log.info(f"{len(accounts)} accounts")
    
    posts_df = pd.DataFrame(posts).set_index('zen_post_id')
    subreddits_df = pd.DataFrame(subreddits.values()).set_index('zen_subreddit_id')
    accounts_df = pd.DataFrame(accounts.values()).set_index('zen_account_id')
    accounts_df['id'] = accounts_df.id
    comments_df = pd.DataFrame(comments)
    comments_df.index = comments_df.index + mydb.get_next_id('comments')
    comments_df.index.name = 'zen_comment_id'
        
    posts_frames, post_objects = clean_and_normalize(posts_df, 'posts')
    comments_frames, comment_objects = clean_and_normalize(comments_df, 'comments')
    subreddits_frames, subreddit_objects = clean_and_normalize(subreddits_df, 'subreddits')
    accounts_frames, account_objects = clean_and_normalize(accounts_df, 'accounts')

    
    all_frames = {'subreddits': subreddits_frames,
                  'accounts': accounts_frames,
                  'posts' : posts_frames, 
                  'comments': comments_frames
    }
    
    for schema, item_frames in all_frames.items():
        for table, df in item_frames.items():
            target_cols = mydb.get_target_columns(schema, table)
            cols_to_drop = set(df.columns).difference(target_cols)
            if len(cols_to_drop):
                cols_to_drop_text = '\n'.join(cols_to_drop)
                log.info(f"Dropping from {table}:\n {cols_to_drop_text}")
            log.info("Writing " + table)
            df['zen_modified_at'] = datetime.now()
            df.drop(columns = cols_to_drop)\
                .to_sql(name = table,
                        schema = schema,
                        con = environ['MAIN_MEDIA_DATABASE'], 
                        if_exists = 'append', # DO NOT CHANGE THIS
                        index = True)
            log.info("Success \n")
    
    completed = completed + post_batch_size
    
    
    
    
