# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_and_normalize
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

args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

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

total_posts_to_get = 3
post_batch_size = 3
completed = 0
start_time = datetime.now()
params = {}
subreddits = {}
accounts = {}
zen_subreddit_id = mydb.get_next_id('subreddits')
while completed < total_posts_to_get:
    comments = []
    posts = []
    print('reading', post_batch_size, 'posts')
    api_query = reddit.subreddit(subs_to_read)\
                      .top(limit = post_batch_size, 
                           time_filter = 'all',
                           params = params)
    
    zen_post_id = mydb.get_next_id('posts')
    for post in api_query:
        # All objects need to reach the fetched
        # state so that all the vars are available.
        # This is achieved by calling any attribute of the
        # object that is not available in the basic vars (such as url).
        _ = post.author.name
        
        # https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
        _ = post.comments.replace_more(limit = None)
        # not calling list leaves out some comments somehow
        # all replies to comments (all comments total) will be included here
        
        
        zen_subreddit_id = mydb.get_existing_or_next_id(
                            post.subreddit.fullname, 'subreddits', 
                            existing_id_collection = subreddits)
        
        # Posts have a parent id and crosspost count so no real need to get these
        #crossposts = crossposts + [vars(x) for x in post.duplicates()]
                    

        post_vars = vars(post)
        sub_vars = vars(post.subreddit)
        sub_vars.update({'zen_subreddit_id': zen_subreddit_id})
        subreddits[zen_subreddit_id] = sub_vars
        

        if post.author:
            zen_account_id = mydb.get_existing_or_next_id(
                                post.author.fullname, 'accounts', 
                                existing_id_collection = accounts)
            post_account_vars = vars(post.author)
            post_account_vars.update({'zen_account_id': zen_account_id})
            accounts[zen_account_id] = post_account_vars
            post_vars.update({'author_subscribed' : post_account_vars['has_subscribed'],
                              'author_is_mod': post_account_vars['is_mod']})
              
        id_params = {'zen_post_id' : zen_post_id,
                     'zen_subreddit_id' : zen_subreddit_id,
                     'zen_account_id' : zen_account_id}
        print(id_params)

        post_vars.update(id_params)
        posts.append(post_vars)


        ## Comments ##
        comments_added = 0
        for comment in post.comments.list():
            comment_vars = vars(comment)
            
            if comment.author:
                # TODO: Handle suspended accounts
                _ = comment.author.total_karma
                if not comment.author.__dict__.get('is_suspended'):
                    zen_account_id = mydb.get_existing_or_next_id(
                                        comment.author.fullname, 'accounts', 
                                        existing_id_collection = accounts)
                    id_params['zen_account_id'] = zen_account_id
                    
                    comment_account_vars = vars(comment.author)
                    comment_account_vars.update(
                    {'zen_account_id': zen_account_id,
                     'reddit_account_id' : 't2_' + comment_account_vars['id']
                     })

                    accounts[zen_account_id] = comment_account_vars
                    
                    comment_vars.update({'author_subscribed' : comment_account_vars['has_subscribed'],
                                      'author_is_mod': comment_account_vars['is_mod']})
                    
                    
            print(id_params)
            comment_vars.update(id_params)
            comments.append(comment_vars)
            comments_added += 1
            if comments_added > 100:
                comments_added = 0
                print('Sleeping 15 secs')
                time.sleep(15)
            

        zen_post_id += 1
        print('Sleeping 15 secs')
        time.sleep(15)
        
    ##############
    batch_reading_time = datetime.now() - start_time
    params = {'after': post.name}
    print(len(posts), 'posts')
    print(len(comments), 'comments')
    print(len(subreddits), 'subreddits')
    
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
                print(f'Dropping from {table}:\n', ',\n'.join(cols_to_drop))
            print("Writing",table)
            df['zen_modified_at'] = datetime.now()
            df.drop(columns = cols_to_drop)\
                .to_sql(name = table,
                        schema = schema,
                        con = environ['MAIN_MEDIA_DATABASE'], 
                        if_exists='append', # DO NOT CHANGE THIS
                        index = True)
            print("Success \n")
    
    completed = completed + post_batch_size
    
    
    
    
