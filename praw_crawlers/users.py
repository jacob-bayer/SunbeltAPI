#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 11:54:01 2022

@author: jacob
"""

import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
#from praw.models.base import PRAWBase

load_dotenv()

reddit = praw.Reddit(
    client_id=environ.get('REDDIT_CLIENT_ID'),
    client_secret=environ.get('REDDIT_SECRET_KEY'),
    user_agent="jacobsapp by jacob087",
    check_for_async=False
)



"""
r/geopolitics - battleground
r/sino - pro-china
r/China_Debate
r/chinesepolitics
"""
    
api_query = reddit.subreddit("all")\
                  .top(limit=1000, 
                       time_filter = 'year')
                  
posts_raw = [x for x in api_query]
posts = []
comments = []
users = []
subreddits = []
for post in posts_raw:
    posts.append(vars(post))
    subreddits.append(post.subreddit)
    comments = comments + [vars(x) for x in post.comments.list()]
    users = users + [vars(x['author'])
                          for x in comments
                          if x.get('author')] + [post.author]



"""
future idea:
    create some kind of data profile for the user based on
    subreddits they are active in and what they usually say
"""
    
posts_df = pd.DataFrame(posts_list)
#comments_df = pd.DataFrame(comments)

def clean_data_frame(df, dtypes = [str, bool, int, float, type(None)]):
    df.columns =[x.replace('_','') for x in df.columns]
    keepcols_dict = {}
    for col in df:
        idx = df[col].first_valid_index()
        keepcols_dict.update({col: df[col].iloc[idx or 0]})
    keepcols_dict = {k:v for k,v in keepcols_dict.items()
                     if type(v) in dtypes}
    keepcols = list(keepcols_dict.keys())
    return df[keepcols]

dataframes = {'posts': posts_df,
              #'comments' : comments_df
              }

for name, df in dataframes.items():
    print(f"Writing {name}")
    clean_data_frame(df)\
        .to_sql(name = name,
                schema = 'reddit',
                con = environ['MAIN_MEDIA_DATABASE'], 
                if_exists='replace', 
                index = False)
    print("Success \n")
