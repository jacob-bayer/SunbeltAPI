#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 17:33:29 2022

@author: jacob
"""

import praw
from os import environ
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id = environ.get('REDDIT_CLIENT_ID'),
    client_secret = environ.get('REDDIT_SECRET_KEY'),
    user_agent ="abelengineer-test-app by u/abelengineer",
    check_for_async = False
)


from pmaw import PushshiftAPI

api = PushshiftAPI()

# The `search_comments` and `search_submissions` methods return generator objects
gen = api.search_comments(limit=100)
results = list(gen)

