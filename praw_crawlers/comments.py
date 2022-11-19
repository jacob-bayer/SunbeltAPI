# -*- coding: utf-8 -*-

import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_data_frame
from sqlalchemy import create_engine
from datetime import datetime

schema_name = 'comments'
mode = 'append'

load_dotenv()

reddit = praw.Reddit(
    client_id=environ.get('REDDIT_CLIENT_ID'),
    client_secret=environ.get('REDDIT_SECRET_KEY'),
    user_agent="jacobsapp by jacob087",
    check_for_async=False
)

api_query = reddit.subreddit("all")\
                  .top(limit=100, 
                       time_filter = 'all')

comments = []

print("Reading query")
start_time = datetime.now()
posts = [x for x in api_query]
for post in posts:
    comments = comments + [vars(x) for x in post.comments]
    
comments_df = pd.DataFrame(comments)
end_time = datetime.now()
print(f"Dataframe is {str(len(comments_df))} rows")
print("Time to read query:", end_time - start_time)
"""
future idea:
    create some kind of data profile for the user based on
    subreddits they are active in and what they usually say
"""

table_dest = {
    'cleaned_dataframe' : 'comments',
    'iterables'         : 'source_iterables'
    }

engine = create_engine(environ['MAIN_MEDIA_DATABASE'])
with engine.connect() as con:
    if mode == 'overwrite':
        for table in table_dest.values():
            con.execute(f"""
            TRUNCATE TABLE {schema_name}.{table} RESTART IDENTITY CASCADE;
            """)
    else:
        result = con.execute(f"SELECT max(post_id) FROM {schema_name}.comments")
        last_id = result.first()[0]
        comments_df.index = comments_df.index + last_id
        
# Reset the index and keep the index column, renaming it to post_id
# which is the identity based on the last known identity from the database
# which should already have been used to reset the index on the df
# before it was passed to this function
comments_df = comments_df.reset_index()
comments_df = comments_df.rename(columns={'index':'comment_id'})
        
print("Cleaning data")
start_time = datetime.now()
frames = clean_data_frame(comments_df)
end_time = datetime.now()
print("Time to clean data:", end_time - start_time)
# The author and subreddit are included as objects but they get thrown away



for table, dest in table_dest.items():
    df = frames[table]
    df['modified_at'] = datetime.now()
    print("Writing",dest,f"({str(len(df))} rows)")
    start_time = datetime.now()
    df.to_sql(name = dest,
                schema = schema_name,
                con = environ['MAIN_MEDIA_DATABASE'], 
                if_exists='append', # DO NOT CHANGE THIS
                index = False)
    end_time = datetime.now()
    print("Success \n")
    print(f"Time to write {dest}", end_time - start_time)






