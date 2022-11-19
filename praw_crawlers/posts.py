# -*- coding: utf-8 -*-

import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_and_normalize
from sqlalchemy import create_engine
from datetime import datetime

modes = {'posts' : 'overwrite',
         'comments' : 'overwrite'}

load_dotenv()

reddit = praw.Reddit(
    client_id = environ.get('REDDIT_CLIENT_ID'),
    client_secret = environ.get('REDDIT_SECRET_KEY'),
    user_agent ="jacobsapp by jacob087",
    check_for_async = False
)

# =============================================================================
# engine = create_engine(environ['MAIN_MEDIA_DATABASE'])
# with engine.connect() as con:
# 
#     for schema, mode in modes.items():
#         if mode == 'overwrite':
#             con.execute(f"TRUNCATE TABLE {schema}.{schema} RESTART IDENTITY CASCADE;")
#         
#         else:
#             result = con.execute(f"SELECT max(post_id) FROM {schema_name}.posts")
#             last_post_id = result.first()[0]
# =============================================================================

last_ids = {}
for schema, mode in modes.items():
    idname = schema[:-1] + '_id'
    last_ids[schema] = pd.read_sql(f"""
            SELECT MAX({idname}) FROM {schema}.{schema};""", 
                               environ['MAIN_MEDIA_DATABASE'])

total_posts_to_get = 10000
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
        
    params = {'after': post.name}
    print(len(posts))

    batch_reading_time = datetime.now() - start_time
    
    posts_df = pd.DataFrame(posts)
    comments_df = pd.DataFrame(comments)
    
    """
    future idea:
        create some kind of data profile for the user based on
        subreddits they are active in and what they usually say
    """

    
    # Reset the index and keep the index column, renaming it to post_id
    # which is the identity based on the last known identity from the database
    # which should already have been used to reset the index on the df
    # before it was passed to this function
    posts_df = posts_df.reset_index().rename(columns={'index':'post_id'})
    comments_df = comments_df.reset_index().rename(columns={'index':'comment_id'})
    
    
    posts_frames, objects = clean_and_normalize(posts_df, 'posts')
    comments_frames, objects = clean_and_normalize(comments_df, 'comments')
    
    
    
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
    
    
    
    
    
