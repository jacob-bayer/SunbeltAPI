#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 11:37:05 2023

@author: jacob
"""

from SAWP import SunbeltClient
# =============================================================================
# from dotenv import load_dotenv
# from os import environ
# import praw
# from praw_cleaner.praw_to_dict import praw_to_dict
# import json
# 
# load_dotenv()
# 
# reddit = praw.Reddit(
#     client_id = environ['REDDIT_CLIENT_ID'],
#     client_secret = environ['REDDIT_SECRET_KEY'],
#     user_agent = "jacobsapp by jacob087",
#     check_for_async = False
# )
# 
#     
# praw_object = reddit.comment('fv6csdb')
# praw_dict = praw_to_dict(praw_object)
# praw_json = json.dumps(praw_dict)
# 
# with open('temp.json','w') as temp_json:
#     temp_json.write(praw_json)
# =============================================================================
    
with open('temp.json','r') as temp_json:
    praw_json = temp_json.read()

sunbelt = SunbeltClient("http://127.0.0.1:5000/graphql")
sunbelt.mutation('createComment', praw_json)


