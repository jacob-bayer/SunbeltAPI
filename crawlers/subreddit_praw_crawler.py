# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_and_normalize
import mydatabasemodule.database_helpers as mydb
from datetime import datetime
import object_parser

load_dotenv()

reddit = praw.Reddit(
    client_id = environ.get('REDDIT_CLIENT_ID'),
    client_secret = environ.get('REDDIT_SECRET_KEY'),
    user_agent ="jacobsapp by jacob087",
    check_for_async = False
)

top_subs = ['AskReddit',
             'worldnews',
             'news',
             'Unexpected',
             'videos',
             'wallstreetbets',
             'PublicFreakout',
             'mildlyinteresting',
             'WhitePeopleTwitter',
             'funny',
             'politics',
             'Damnthatsinteresting',
             'pics',
             'MadeMeSmile',
             'facepalm',
             'movies',
             'todayilearned',
             'technology',
             'nextfuckinglevel',
             'gaming',
             'memes',
             'IdiotsInCars',
             'interestingasfuck',
             'tifu',
             'dankmemes',
             'aww',
             'science',
             'Wellthatsucks',
             'LifeProTips',
             'WatchPeopleDieInside',
             'oddlysatisfying',
             'teenagers',
             'wholesomememes',
             'comics',
             'PrequelMemes',
             'Futurology',
             'dataisbeautiful',
             'assholedesign',
             'LeopardsAteMyFace',
             'Showerthoughts',
             'DunderMifflin',
             'EarthPorn',
             'books',
             'space',
             'trashy',
             'me_irl',
             'awfuleverything',
             'gifs',
             'IAmA',
             'Music',
             'rickandmorty',
             'nottheonion',
             'freefolk',
             'BikiniBottomTwitter',
             'MurderedByWords',
             'JusticeServed',
             'PewdiepieSubmissions',
             'announcements',
             'StarWarsBattlefront',
             'thanosdidnothingwrong',
             'MemeEconomy']

subs_to_read = '+'.join(top_subs)

# Just for testing
subs_to_read = ['dataisbeautiful',
             'assholedesign',
             'LeopardsAteMyFace']

subs_to_read = '+'.join(top_subs)
subreddit = reddit.subreddit(subs_to_read)

# Solution comes from here
# The last 100 are fetched instantly, then new ones are listened for
# https://www.reddit.com/r/redditdev/comments/7vj6ox/comment/dtszfzb/?context=3
# https://github.com/praw-dev/praw/issues/1025
comment_stream = subreddit.stream.comments(pause_after=-1, skip_existing = True)
submission_stream = subreddit.stream.submissions(pause_after=-1, skip_existing = True)
start_time = datetime.now()
posts = 0
comments = 0
while True:
    for comment in comment_stream:
        print("Comment stream")
        if comment is None:
            break
        comments += 1
        print("New comment:", comment.permalink)
    for post in submission_stream:
        print("Post stream")
        if post is None:
            break
        print("New post:", post.permalink)
        posts += 1
        #object_parser.insert_post(post)
        
        
total_time = datetime.now() - start_time

minutes_elapsed = total_time.seconds/60
print(posts/minutes_elapsed, 'posts per minute')
print(comments/minutes_elapsed, 'comments per minute')




