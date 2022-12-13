#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 08:20:53 2022

@author: jacob
"""
import mydatabasemodule.database_helpers as mydb
from mydatabasemodule.praw_output_cleaner import clean_and_normalize
import pandas as pd
from datetime import datetime
from os import environ

def parse_post(post):
    zen_post_id = mydb.get_next_id('posts')
    
    # All objects need to reach the fetched
    # state so that all the vars are available.
    # This is achieved by calling any attribute of the
    # object that is not available in the basic vars (such as url).
    _ = post.author.name
    
    zen_subreddit_id = mydb.get_existing_or_next_id(
                        post.subreddit.fullname, 'subreddits')
    
    post_vars = vars(post)
    sub_vars = vars(post.subreddit)
    sub_vars.update({'zen_subreddit_id': zen_subreddit_id})
    

    if post.author:
        zen_account_id = mydb.get_existing_or_next_id(
                            post.author.fullname, 'accounts')
        post_account_vars = vars(post.author)
        post_account_vars.update({'zen_account_id': zen_account_id})
        post_vars.update({'author_subscribed' : post_account_vars['has_subscribed'],
                          'author_is_mod': post_account_vars['is_mod']})
          
    id_params = {'zen_post_id' : zen_post_id,
                 'zen_subreddit_id' : zen_subreddit_id,
                 'zen_account_id' : zen_account_id}
    print(id_params)

    post_vars.update(id_params)
    
            
    return post_vars, sub_vars, post_account_vars



def parse_comment(comment, accounts):
    id_params = {'zen_comment_id' : mydb.get_next_id('comments')}
    
    comment_vars = vars(comment)
    comment_account_vars = None
    if comment.author:
        # TODO: Handle suspended accounts
        _ = comment.author.total_karma
        if not comment.author.__dict__.get('is_suspended'):
            zen_account_id = mydb.get_existing_or_next_id(
                                comment.author.fullname, 'accounts', 
                                existing_id_collection = accounts)
            id_params['zen_account_id'] = zen_account_id
            
            comment_account_vars = vars(comment.author)
            comment_account_vars.update(
            {'zen_account_id': zen_account_id,
             'reddit_account_id' : 't2_' + comment_account_vars['id']
             })
    
            
            comment_vars.update({'author_subscribed' : comment_account_vars['has_subscribed'],
                              'author_is_mod': comment_account_vars['is_mod']})

    print(id_params)
    comment_vars.update(id_params)
    return comment_vars, comment_account_vars


def insert_comment(comment):
    comment_vars, comment_account_vars = parse_comment(comment, accounts)
    
    
    
    
def insert_post(post):
    post_vars, sub_vars, post_account_vars = parse_post(post)
    
    # https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
    _ = post.comments.replace_more(limit = 0)
    # not calling list leaves out some comments somehow
    # all replies to comments (all comments total) will be included here
    
    comments = []
    accounts = {int(post_account_vars['zen_account_id']) : post_account_vars}
    for comment in post.comments.list():
        comment_vars, comment_account_vars = parse_comment(comment, accounts)
        comments.append(comment_vars)
        if comment_account_vars:
            comment_account_zen_id = int(comment_account_vars['zen_account_id'])
            accounts[comment_account_zen_id] = comment_account_vars
    
    posts_df = pd.DataFrame([post_vars]).set_index('zen_post_id')
    subreddits_df = pd.DataFrame([sub_vars]).set_index('zen_subreddit_id')
    accounts_df = pd.DataFrame(accounts.values()).set_index('zen_account_id')
    comments_df = pd.DataFrame(comments).set_index('zen_comment_id')
    
    posts_frames, post_objects = clean_and_normalize(posts_df, 'posts')
    comments_frames, comment_objects = clean_and_normalize(comments_df, 'comments')
    subreddits_frames, subreddit_objects = clean_and_normalize(subreddits_df, 'subreddits')
    accounts_frames, account_objects = clean_and_normalize(accounts_df, 'accounts')
    
    
    all_frames = {'subreddits': subreddits_frames,
                  'accounts': accounts_frames,
                  'posts' : posts_frames, 
                  'comments': comments_frames
    }
    
    for schema, item_frames in all_frames.items():
        for table, df in item_frames.items():
            target_cols = mydb.get_target_columns(schema, table)
            cols_to_drop = set(df.columns).difference(target_cols)
            if len(cols_to_drop):
                print(f'Dropping from {table}:\n', ',\n'.join(cols_to_drop))
            print("Writing",table)
            df['zen_modified_at'] = datetime.now()
            df.drop(columns = cols_to_drop)\
                .to_sql(name = table,
                        schema = schema,
                        con = environ['MAIN_MEDIA_DATABASE'], 
                        if_exists='append', # DO NOT CHANGE THIS
                        index = True)
            print("Success \n")
    
    
    
    
    
    
    