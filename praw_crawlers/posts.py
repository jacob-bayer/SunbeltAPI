# -*- coding: utf-8 -*-

import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_and_normalize
from sqlalchemy import create_engine
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


last_ids = {}
db_url = environ['MAIN_MEDIA_DATABASE']
engine = create_engine(db_url)
for schema in schemas:
    if schema.writemode == WriteMode.overwrite:
        with open(f'./ddl/{schema.name}.sql') as file:
            sql = file.read()
        with engine.connect() as conn:
            conn.execute(sql)
    elif schema.writemode == WriteMode.append:
        idname = schema[:-1] + '_id'
        last_ids[schema] = pd.read_sql(f"""
                SELECT MAX({idname}) FROM {schema.name}.{schema.name};
                """, 
                 db_url)

total_posts_to_get = 30
batch_size = 3
comments = []
posts = []
crossposts = []
start_time = datetime.now()
params = {}
while len(posts) < total_posts_to_get:
    print('reading', batch_size, 'posts')
    api_query = reddit.subreddit("all")\
                      .top(limit=batch_size, 
                           time_filter = 'all')
    api_query.params.update(params)
    post_id = 1 # or last_id
    for post in api_query:
        post_id_param = {'post_id' : post_id} # or last_id
        # Posts have a parent id and crosspost count so no real need to get these
        #crossposts = crossposts + [vars(x) for x in post.duplicates()]
        
        # https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
        _ = post.comments.replace_more(limit = 0)
        # not calling list leaves out some comments somehow
        # all replies to comments (all comments total) should be included here
        for x in post.comments.list():
            print(len(comments),'comments added')
            comment_vars = vars(x)
            comment_vars.update(post_id_param)
            comments.append(comment_vars)
        
        post_vars = vars(post)
        post_vars.update(post_id_param)
        posts.append(post_vars)
        
        post_id = post_id + 1
    
    
    batch_reading_time = datetime.now() - start_time
    params = {'after': post.name}
    print(len(posts), 'posts')
    print(len(comments), 'comments')
    
    posts_df = pd.DataFrame(posts).set_index('post_id')
    comments_df = pd.DataFrame(comments)
    comments_df.index.name = 'comment_id'
        
    
    posts_frames, objects = clean_and_normalize(posts_df, 'posts')
    comments_frames, objects = clean_and_normalize(comments_df, 'comments')
    
    frames = [posts_frames, 
              comments_frames]
    
    for frame in frames:
        for table, df in posts_frames.items():
            print("Writing",table)
            df['modified_at'] = datetime.now()
            df.to_sql(name = table,
                        schema = 'posts',
                        con = environ['MAIN_MEDIA_DATABASE'], 
                        if_exists='append', # DO NOT CHANGE THIS
                        index = True)
            print("Success \n")
    
    for table, df in comments_frames.items():
        print("Writing",table)
        df['modified_at'] = datetime.now()
        df.to_sql(name = table,
                    schema = 'comments',
                    con = environ['MAIN_MEDIA_DATABASE'], 
                    if_exists='append', # DO NOT CHANGE THIS
                    index = True)
        print("Success \n")
    
    
    
    
    
