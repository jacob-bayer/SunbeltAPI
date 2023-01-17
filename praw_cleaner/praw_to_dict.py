# -*- coding: utf-8 -*-

import pandas as pd
import logging
from enum import Enum
from dataclasses import dataclass
from os import environ
from datetime import datetime
import pytz
east_time = pytz.timezone('US/Eastern')

log = logging.getLogger("CLEANER")

WriteMode = Enum('WriteMode', ['overwrite','append'])

@dataclass
class SchemaConfig:
    name: str
    writemode: Enum = WriteMode.append
    

class zen_kind_enum(Enum):
    post = 1
    comment = 2
    subreddit = 3
    account = 4

def get_zen_kind(praw_object):
    lookup_dict = {
                 'Submission' : zen_kind_enum['post'],
                 'Comment'    : zen_kind_enum['comment'],
                 'Subreddit'  : zen_kind_enum['subreddit'],
                 'Redditor'   : zen_kind_enum['account']
                 }
    input_class_name = praw_object.__class__.__name__
    return lookup_dict[input_class_name]


def has_valid_praw_author(praw_object_with_author):
    valid = False
    if praw_object_with_author.author:
        # TODO: Add suspended accounts to dwh
        _ = praw_object_with_author.author._fetch()
        if not praw_object_with_author.author.__dict__.get('is_suspended'):
            valid = True
            
    return valid


def praw_to_dict(praw_object):
    if not praw_object._fetched:
        praw_object._fetch()
    
    obj_vars = vars(praw_object).copy()

    # Misc stuff
    int_bools = ['gilded','edited']
    for field in int_bools:
        if field in obj_vars:
            obj_vars[field] = int(obj_vars[field])


    
    # Cols to rename to reddit_obj_id
    fullnamekeys = {'t1_' : 'comment',
                    't2_' : 'account',
                    't3_' : 'post',
                    't4_' : 'message',
                    't5_' : 'subreddit',
                    't6_' : 'award'}
    
    # ensure that the self id is present no matter what
    kind_code = praw_object._kind + '_'
    kind = fullnamekeys[kind_code]
    obj_vars['reddit' + '_' + kind + '_id'] = kind_code + obj_vars.pop('id')
    
    # Rename fields to reddit_obj_id
    for key, obj_name in fullnamekeys.items():
        for field, value in obj_vars.copy().items():
            if isinstance(value, str) and value.startswith(key):
                if 'parent' in field:
                    rename_field = 'reddit_parent_id'
                else:
                    rename_field = f'reddit_{obj_name}_id'
                    
                    obj_vars[rename_field] = obj_vars.pop(field)
    
                
    for field, value in obj_vars.copy().items():
        # delete private variables
        if field.startswith('_'):
            del obj_vars[field]
            continue
        
        # delete object vars
        is_class = hasattr(value, '__module__') and not isinstance(value, pd.Timestamp)
        if is_class:
            del obj_vars[field]
            continue
        
        # delete empty iterables
        is_dict_or_list = isinstance(value, dict) or isinstance(value, list)
        if is_dict_or_list:
            if len(value) == 0:
                del obj_vars[field]
        

            
            
    
    zen_kind = get_zen_kind(praw_object)
    is_post = False
    is_comment = False
    
    if zen_kind == zen_kind_enum['post']:
        is_post = True
    elif zen_kind == zen_kind_enum['comment']:
        is_comment = True
        
    if is_post or is_comment:
        print('Unpacking subreddit')
        obj_vars['subreddit'] = praw_to_dict(praw_object.subreddit)
        
        if has_valid_praw_author(praw_object):
            print('Unpacking author')
            obj_vars['author'] = praw_to_dict(praw_object.author)
    
    if is_comment:
        print('Unpacking post')
        obj_vars['post'] = praw_to_dict(praw_object.submission)
    
    
    return obj_vars

            
            
                
    
