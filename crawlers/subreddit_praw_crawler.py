# -*- coding: utf-8 -*-


import praw
from os import environ
from dotenv import load_dotenv
import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_and_normalize
import mydatabasemodule.database_helpers as mydb
from datetime import datetime

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

# Just for testing
subs_to_read = ['dataisbeautiful',
             'assholedesign',
             'LeopardsAteMyFace']

for sub in subs_to_read:
    api_query = reddit.subreddit(sub).stream.submissions()

posts = []                
for post in api_query:
    posts.append(post)

posts_df = pd.DataFrame(posts)

    
