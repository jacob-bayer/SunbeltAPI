#! /Users/jacob/Documents/github_local/database/venv/bin/python3
# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
from database_helpers.praw_output_cleaner import insert_praw_object
import threading
import logging
import argparse
import signal
import queue

parser = argparse.ArgumentParser(description="Crawler parser")
parser.add_argument("--debug", 
                    help = "Set the log level to debug", 
                    action = 'store_const',
                    const = True,
                    default = False)
parser.add_argument("--suppress_logs", 
                    help = "Suppress logs", 
                    action = 'store_const',
                    const = True,
                    default = False)
parser.add_argument("--comments", 
                    help = "Listen to comments.",
                    action = 'store_const',
                    const = True,
                    default = False)
parser.add_argument("--posts", 
                    help = "Listen to posts.",
                    action = 'store_const',
                    const = True,
                    default = False)
args = parser.parse_args()

# The last 100 are fetched instantly, then new ones are listened for
# https://www.reddit.com/r/redditdev/comments/7vj6ox/comment/dtszfzb/?context=3
# https://github.com/praw-dev/praw/issues/1025

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
if not args.suppress_logs:
    logging.basicConfig(level=logging.INFO)

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

if args.comments:
    kind = 'COMMENTS'
    stream = subreddit.stream.comments(pause_after=-1, skip_existing = True)
if args.posts:
    kind = 'POSTS'
    stream = subreddit.stream.submissions(pause_after=-1, skip_existing = True)
else:
    kind = 'ALL'
    post_stream = subreddit.stream.submissions(pause_after=-1, skip_existing = True)
    comment_stream = subreddit.stream.comments(pause_after=-1, skip_existing = True)
    
log = logging.getLogger(f'{kind} LISTENER')

q = queue.Queue()
stop_event = threading.Event()
    
def listen_to(stream, kind):
    for praw_object in stream:
        if praw_object is not None:
            log.info(' ' + praw_object.__repr__() + f'added to queue by {kind} stream')
            q.put(praw_object)
        else:
            if stop_event.is_set():
                break


def insert_worker():
    while True:
        praw_object = q.get()
        log.info(f' Working on {praw_object}')
        try:
            insert_praw_object(praw_object)
            q.task_done()
        except Exception as e:
            log.info(f" Exception for {praw_object.__repr__()}")
            raise e
            stop_event.set()
        if not q.unfinished_tasks and stop_event.is_set():
            break


def interrupt_handler(signum, frame):
    log.info(f" Gracefully exiting. There are still {q.unfinished_tasks} unfinished_tasks in the queue.")
    stop_event.set()

# No clue how this works but it does
signal.signal(signal.SIGINT, interrupt_handler)

worker_thread = threading.Thread(name = 'worker_thread', target=insert_worker, daemon=True)
comment_thread = threading.Thread(name = 'comment_thread', target=listen_to, args = [comment_stream,'comment'], daemon=True)
post_thread = threading.Thread(name = 'post_thread', target=listen_to, args = [post_stream,'post'], daemon=True)

post_thread.start()
comment_thread.start()
worker_thread.start()
log.info(" Listening")
worker_thread.join()

