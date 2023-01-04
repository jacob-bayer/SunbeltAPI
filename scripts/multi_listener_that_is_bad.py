# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
from mydatabasemodule.praw_output_cleaner import insert_praw_object
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import argparse
import signal

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

log = logging.getLogger(f'{kind} LISTENER')

def futures_handler(futures):
    # Check that it worked
    for future in as_completed(futures):
        praw_object = futures[future]
        try:
            future.result()
        except Exception as exc:
            print(f'{praw_object} generated an exception: {exc}')
        else:
            print(f'{praw_object} is ok')
        finally:
            futures.pop(future)

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True
    
def listen_to(stream):
    futures = {}
    with ThreadPoolExecutor(10) as executor:
        while not killer.kill_now:
            for praw_object in stream:
                print("listening")
                if praw_object is not None:
                    print(praw_object.fullname)
                    future = executor.submit(insert_praw_object, praw_object)
                    futures[future] = praw_object
                else:
                    print("None")
                    if len(futures):
                        print("Handling futures")
                        future = executor.submit(futures_handler, futures)
                        futures[future] = 'Futures handler'
                    break
#while True:
killer = GracefulKiller()


listen_to(stream)

        




