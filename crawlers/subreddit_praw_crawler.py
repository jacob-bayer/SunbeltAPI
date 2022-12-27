# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
from mydatabasemodule.praw_output_cleaner import set_default_zen_vars
from datetime import datetime

load_dotenv()

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
while True:
    for comment in comment_stream:
        print("Comment stream")
        if comment is None:
            break
        comment
        print("New comment:", comment.permalink)
    for post in submission_stream:
        print("Post stream")
        if post is None:
            break
        print("New post:", post.permalink)
        posts += post
        #object_parser.insert_post(post)
        
        
total_time = datetime.now() - start_time

minutes_elapsed = total_time.seconds/60
print(posts/minutes_elapsed, 'posts per minute')
print(comments/minutes_elapsed, 'comments per minute')




