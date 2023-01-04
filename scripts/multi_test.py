# -*- coding: utf-8 -*-

import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from mydatabasemodule.praw_output_cleaner import (
                        clean_and_normalize, 
                        has_valid_praw_author,
                        update_existing_object_collection,
                        insert_from_cleaned_frames,
                        SchemaConfig,
                        WriteMode
                        )



load_dotenv()

reddit = praw.Reddit(
    client_id = environ.get('REDDIT_CLIENT_ID'),
    client_secret = environ.get('REDDIT_SECRET_KEY'),
    user_agent ="jacobsapp by jacob087",
    check_for_async = False
)

subs_to_read = 'dataisbeautiful'

api_query = reddit.subreddit(subs_to_read)\
                  .top(limit = 10,
                       time_filter = 'week')

def fetch_post_and_wait(post):
    post._fetch()
    print(f"{post.fullname} fetched!")
    time.sleep(10)

def print_something(i):
    print("hello", i)
    time.sleep(10)
    print("finished", i)

futures = {}
with ThreadPoolExecutor(3) as executor:
    for post in api_query:
        future = executor.submit(fetch_post_and_wait, post)
        futures[future] = post
    
    # Check that it worked
    for future in as_completed(futures):
        post = futures[future]
        try:
            future.result()
        except Exception as exc:
            print(f'{post} generated an exception: {exc}')
        else:
            print(f'{post.fullname} is ok')
