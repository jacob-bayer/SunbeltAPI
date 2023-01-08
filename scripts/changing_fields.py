#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 10:51:45 2022

@author: jacob
"""
import praw
import pandas as pd
from database_helpers.praw_output_cleaner import clean_and_normalize
from os import environ
from dotenv import load_dotenv
import time

load_dotenv()

reddit = praw.Reddit(
    client_id = environ.get('REDDIT_CLIENT_ID'),
    client_secret = environ.get('REDDIT_SECRET_KEY'),
    user_agent ="jacobsapp by jacob087",
    check_for_async = False
)

api_query = reddit.subreddit('all').hot(limit = 1)
post = next(api_query)

times_to_check = 10
post_vars_list = []
for check_id in range(times_to_check):
    post = reddit.submission('znfw7y')
    _ = post.score
    post_vars = vars(post)
    post_vars['check_id'] = check_id
    post_vars_list.append(post_vars)
    
    sleep_secs = 60
    print(f"sleeping for {sleep_secs} secs")
    time.sleep(sleep_secs)
        

posts_df = pd.DataFrame(post_vars_list).set_index('check_id')
posts_frames, _ = clean_and_normalize(posts_df, 'posts')

df = posts_frames['media']

examine = df.copy()

not_dup_cols = [x for x in test.columns if not all(test[x].duplicated(keep=False))]



