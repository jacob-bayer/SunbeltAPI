# -*- coding: utf-8 -*-

import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_and_normalize
from sqlalchemy import create_engine
from datetime import datetime

schema_name = 'posts'
mode = 'overwrite'

load_dotenv()

reddit = praw.Reddit(
    client_id=environ.get('REDDIT_CLIENT_ID'),
    client_secret=environ.get('REDDIT_SECRET_KEY'),
    user_agent="jacobsapp by jacob087",
    check_for_async=False
)

api_query = reddit.subreddit("all")\
                  .top(limit=1, 
                       time_filter = 'all',
                       params ={'after':'t3_jptqj9'}
                       )
                  

post = next(api_query)
post.name == 't3_62sjuh'

comments = []
posts = []
crossposts = []
for post in api_query:
    # do this right
    crossposts = crossposts + [vars(x) for x in post.duplicates]
    comments = comments + [vars(x) for x in post.comments]

    posts.append(vars(post))

posts_df = pd.DataFrame(posts)

"""
future idea:
    create some kind of data profile for the user based on
    subreddits they are active in and what they usually say
"""

engine = create_engine(environ['MAIN_MEDIA_DATABASE'])
with engine.connect() as con:
    if mode == 'overwrite':
        con.execute(f"TRUNCATE TABLE {schema_name}.posts RESTART IDENTITY CASCADE;")
    else:
        result = con.execute(f"SELECT max(post_id) FROM {schema_name}.posts")
        last_id = result.first()[0]
        posts_df.index = posts_df.index + last_id

# Reset the index and keep the index column, renaming it to post_id
# which is the identity based on the last known identity from the database
# which should already have been used to reset the index on the df
# before it was passed to this function
posts_df = posts_df.reset_index().rename(columns={'index':'post_id'})

frames, objects = clean_and_normalize(posts_df, schema_name)

order_to_write = [
'posts',
'media_embed', 
'secure_media', 
'gildings', 
'all_awardings', 
'media']

for table in order_to_write:
    print("Writing",table)
    df = frames[table]
    df['modified_at'] = datetime.now()
    df.to_sql(name = table,
                schema = schema_name,
                con = environ['MAIN_MEDIA_DATABASE'], 
                if_exists='append', # DO NOT CHANGE THIS
                index = True)
    print("Success \n")






