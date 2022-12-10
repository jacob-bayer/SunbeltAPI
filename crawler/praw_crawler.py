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

WriteMode = Enum('WriteMode', ['overwrite','append'])

@dataclass
class SchemaConfig:
    name: str
    writemode: Enum
    frames: dict = None
        
schemas = [SchemaConfig('posts', WriteMode.overwrite),
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


total_posts_to_get = 30
post_batch_size = 30
completed = 0
start_time = datetime.now()
params = {}
subreddits = []
while completed < total_posts_to_get:
    comments = []
    posts = []
    print('reading', post_batch_size, 'posts')
    api_query = reddit.subreddit("all")\
                      .top(limit = post_batch_size, 
                           time_filter = 'all',
                           params = params)
    
    post_id = mydb.get_next_id('posts')
    for post in api_query:
        print('post_id:', post_id)
        post_id_param = {'post_id' : post_id} # or last_id
        # Posts have a parent id and crosspost count so no real need to get these
        #crossposts = crossposts + [vars(x) for x in post.duplicates()]
        
        # https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
        _ = post.comments.replace_more(limit = 0)
        # not calling list leaves out some comments somehow
        # all replies to comments (all comments total) will be included here
        

        for x in post.comments.list():
            comment_vars = vars(x)
            comment_vars.update(post_id_param)
            comments.append(comment_vars)
            
        subreddits.append(vars(post.subreddit))
        
        post_vars = vars(post)
        post_vars.update(post_id_param)
        posts.append(post_vars)
        post_id = post_id + 1

    batch_reading_time = datetime.now() - start_time
    params = {'after': post.name}
    print(len(posts), 'posts')
    print(len(comments), 'comments')
    
    subreddits_df = pd.DataFrame(subreddits)
    posts_df = pd.DataFrame(posts).set_index('post_id')
    comments_df = pd.DataFrame(comments)
    comments_df.index = comments_df.index + mydb.get_next_id('comments')
    comments_df.index.name = 'comment_id'
        
    posts_frames, post_objects = clean_and_normalize(posts_df, 'posts')
    comments_frames, comment_objects = clean_and_normalize(comments_df, 'comments')
    
    
    # these objects for subreddits are different here than they are
    # when they come straight out of the post. Not sure why that is.
    subreddit_df = pd.DataFrame([vars(x) for x in post_objects.subreddit])
    
    
    
    all_frames = {'posts' : posts_frames, 
              'comments': comments_frames}
    
    for schema, item_frames in all_frames.items():
        for table, df in item_frames.items():
            target_cols = mydb.get_target_columns(schema, table)
            cols_to_drop = set(df.columns).difference(target_cols)
            print("Writing",table)
            df['modified_at'] = datetime.now()
            df.drop(columns = cols_to_drop)\
                .to_sql(name = table,
                        schema = schema,
                        con = environ['MAIN_MEDIA_DATABASE'], 
                        if_exists='append', # DO NOT CHANGE THIS
                        index = True)
            print("Success \n")
            
    completed = completed + post_batch_size
    
    
    
    
