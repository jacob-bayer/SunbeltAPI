# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
from mydatabasemodule.praw_output_cleaner import (
                        SchemaConfig,
                        WriteMode,
                        async_insert_praw_object
                        )
from datetime import datetime
import asyncio

load_dotenv()

schemas = [SchemaConfig('subreddits', WriteMode.append),
           SchemaConfig('accounts', WriteMode.append),
           SchemaConfig('posts', WriteMode.append),
           SchemaConfig('comments', WriteMode.append)]

reddit = praw.Reddit(
    client_id = environ.get('REDDIT_CLIENT_ID'),
    client_secret = environ.get('REDDIT_SECRET_KEY'),
    user_agent ="jacobsapp by jacob087",
    check_for_async = False
)

subs_to_read = ['dataisbeautiful',
                 'assholedesign',
                 'LeopardsAteMyFace']

subs_to_read = '+'.join(subs_to_read)
subreddit = reddit.subreddit(subs_to_read)

# Solution comes from here
# The last 100 are fetched instantly, then new ones are listened for
# https://www.reddit.com/r/redditdev/comments/7vj6ox/comment/dtszfzb/?context=3
# https://github.com/praw-dev/praw/issues/1025
comment_stream = subreddit.stream.comments(pause_after=-1, skip_existing = True)
submission_stream = subreddit.stream.submissions(pause_after=-1, skip_existing = True)
start_time = datetime.now()

async def listen_to(stream):
    print("Switching stream")
    for praw_object in stream:
        if praw_object is not None:
            print(praw_object.fullname)
            await async_insert_praw_object(praw_object)
            print("Moving on from await call")
        break
        
async def listen_to_all():
    task1 = asyncio.create_task(listen_to(comment_stream))
    task2 = asyncio.create_task(listen_to(submission_stream))
    await asyncio.gather(task1, task2)


while True:
    asyncio.run(listen_to_all())

        




