# -*- coding: utf-8 -*-

import pandas as pd
import logging
from mydatabasemodule import database_helpers as mydb
from enum import Enum
from dataclasses import dataclass
from os import environ
import asyncio
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

def set_zen_obj_vars(praw_object, existing_id_collection = None):
    schema_name = get_zen_kind(praw_object).name + 's'
    
    unique_reddit_id = praw_object.fullname
    zen_ids = mydb.get_id_params(
                    unique_reddit_id, schema_name, 
                    existing_id_collection = existing_id_collection)
    
    obj_vars = vars(praw_object)
    # everything has a full name, but for some reason the Redditor
    # object does not return the full name in the vars
    obj_vars['unique_reddit_id'] = unique_reddit_id
    
    obj_vars.update(zen_ids)


def update_existing_object_collection(existing_id_collection, praw_object):
    unique_reddit_id = praw_object.fullname
    
    if unique_reddit_id not in existing_id_collection:
        set_zen_obj_vars(praw_object, existing_id_collection)
        
        # set default ensures there are no duplicates
        obj_vars = vars(praw_object)
        existing_id_collection.setdefault(unique_reddit_id, obj_vars)
    

def has_valid_praw_author(praw_object_with_author):
    valid = False
    if praw_object_with_author.author:
        # TODO: Add suspended accounts to dwh
        _ = praw_object_with_author.author._fetch()
        if not praw_object_with_author.author.__dict__.get('is_suspended'):
            valid = True
            
    return valid

def json_normalize_with_id(df):
    newdf = pd.json_normalize(df).set_index(df.index).dropna(how='all')
    newdf.columns = [x.replace('.','_') for x in newdf.columns]
    return newdf

def pd_json_normalize_list_of_dicts(df, index_name = None):
    index_name = index_name or df.index.name
    if not index_name:
        ermsg = "Must provide index name or name the index in the dataframe"
        raise ValueError(ermsg)
        
    all_data = pd.DataFrame()
    for id_col, data in df.items():
        data = pd.json_normalize(data)
        data.insert(0,index_name, id_col)
                            
        all_data = pd.concat([
            all_data,
            data], 
            axis = 0,
            ignore_index = True)
    all_data.columns = [x.replace('.','_') for x in all_data.columns]
    return all_data.set_index(index_name)


def clean_and_sort(df):
    """
    Removes columns whose values are python objects and returns a 
    dictionary of dataframes
    """
    log.debug('Cleaning and sorting')
    id_col = df.index.name or ''
    if 'id' in id_col:
        df = df.reset_index()
    else:
        raise Exception("""
        Bad ID Col. Primary ID (but not neccesarily key) must be index.
        Index name must have 'id' in it.
        """)
    
    # Remove leading underscores from column names and replace
    # periods with underscores
    df.columns = [x[1:] if x.startswith('_') else x for x in df.columns]
    df.columns = [x.replace('.','_') for x in df.columns]
    
    # The ID column is a repetition of data available in an object's full name
    if 'id' in df.columns:
        df.drop(columns='id', inplace=True)
    # Create dictionary of column names and first real values
    cols_dict = {}
    for col in df:
        idx = df[col].first_valid_index()
        cols_dict.update({col: df[col].iloc[idx or 0]})
    del cols_dict[id_col]
    
    # Misc stuff
    int_bools = ['gilded','edited']
    for col in int_bools:
        if col in df.columns:
            df[col] = df[col].astype(int)
    
    # Cols to rename to reddit_obj_id
    fullnamekeys = {'t1_' : 'comment',
                    't2_' : 'account',
                    't3_' : 'post',
                    't4_' : 'message',
                    't5_' : 'subreddit',
                    't6_' : 'award'}
    rename_dict = {}
    for key, obj_name in fullnamekeys.items():
        for col, value in cols_dict.items():
            if isinstance(value, str) and value.startswith(key):
                if 'parent' in col:
                    rename_col = 'reddit_parent_id'
                else:
                    rename_col = f'reddit_{obj_name}_id'
                    
                if rename_col not in rename_dict.values():
                    rename_dict[col] = rename_col
                    
    for key, value in rename_dict.items():
        # This adds the columns to be renamed to the cols_dict so that
        # they remain in the dataframe due to their presence in the cols_dict
        # keys
        if not cols_dict.get(value):
            cols_dict[value] = cols_dict[key]
            del cols_dict[key]
                
    df = df.rename(columns=rename_dict)
    
    # Break out dataframe into columns whose values are classes, iterables,
    # and all else
    class_cols = [id_col]
    iter_cols = [id_col]
    keep_cols = [id_col]
    for col, value in cols_dict.items():
        is_iterable = hasattr(value, '__iter__') and not isinstance(value, str)
        is_class = hasattr(value, '__module__') and not isinstance(value, pd.Timestamp)
        if is_class:
            class_cols.append(col)
        elif is_iterable:
            iter_cols.append(col)
        else:
            keep_cols.append(col)
    
    # Return dictionary of dataframes
    return {'cleaned_dataframe' : df[keep_cols].set_index(id_col),
            'iterables'         : df[iter_cols].set_index(id_col),
            'objects'           : df[class_cols].set_index(id_col)}


def normalize_iterables(df):
    """
    Does specific things depending on which column iteration needs
    to be performed
    """
    
    final_dict = {}
    for table, data in df.items():
        if table == 'gildings':
            log.debug('Iterating ' + table)
            gildings = json_normalize_with_id(data)
            gildings = gildings.melt(value_vars = gildings.columns, 
                                     var_name = 'reddit_gid', 
                                     #value_name = 'not sure',
                                     ignore_index = False)\
                                     .dropna(subset = ['value'])
            final_dict['gildings'] = gildings
                        
        if table == 'all_awardings':
            log.debug('Iterating ' + table)
            data = data[data.map(lambda x: len(x) > 0)]
            if len(data):
                all_awardings = pd_json_normalize_list_of_dicts(data)
                # I don't care about the iterables they are stupid for this one
                all_awardings = clean_and_sort(all_awardings)['cleaned_dataframe']
                keepcols = [x for x in all_awardings.columns 
                           if 'tiers_by_required_awardings' not in x]
                all_awardings = all_awardings[keepcols]
                final_dict['awardings'] = all_awardings
            
        if table == 'previews':
            log.debug('Iterating ' + table)
            previews = json_normalize_with_id(data)
            previews = clean_and_sort(previews)
            images = pd_json_normalize_list_of_dicts(previews['iterables']['images'])
            previews = previews['cleaned_dataframe']
            final_dict['resolutions'] = pd_json_normalize_list_of_dicts(images['resolutions'])
            images.drop(columns='resolutions', inplace = True)
            final_dict['previews'] = pd.concat([previews,images], axis=1)
            
        if table == 'media':
            log.debug('Iterating ' + table)
            final_dict['media'] = json_normalize_with_id(data).rename(columns={'type':'media_type'})
        if table == 'media_embed':
            log.debug('Iterating ' + table)
            final_dict['media_embed'] = json_normalize_with_id(data)
        if table == 'secure_media': 
            log.debug('Iterating ' + table)
            final_dict['secure_media'] = json_normalize_with_id(data)
        
    return final_dict
        # TODO:
        # unknown format
        # secure_media_embed
        # mod_reports
        # comments_by_id
        # user_reports
        # author_flair_richtext

        # dont care about data
        # treatment_tags
        # link_flair_richtext

        # not sure if i want it
        # content_categories

            
def clean_and_normalize(df, schema_name):
    ready_to_write_dict = {}
    cleaned_dict = clean_and_sort(df)
    normalized_iterables_dict = normalize_iterables(cleaned_dict['iterables'])
    # main one must come first
    ready_to_write_dict.update({schema_name : 
                                cleaned_dict['cleaned_dataframe']})
    ready_to_write_dict.update(normalized_iterables_dict)

    return ready_to_write_dict, cleaned_dict['objects']

          
async def async_insert_praw_object(praw_object):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, 
                                  insert_praw_object, 
                                  praw_object)

def insert_praw_object(praw_object):
    print(f"insert_praw_object: {praw_object.__repr__()} ")
    zen_kind = get_zen_kind(praw_object)
    is_post = False
    is_comment = False
    
    if zen_kind == zen_kind_enum['post']:
        is_post = True
    elif zen_kind == zen_kind_enum['comment']:
        is_comment = True

    set_zen_obj_vars(praw_object)
    obj_vars = vars(praw_object)
    version = obj_vars[f'zen_{zen_kind.name}_version_id']
    schema_name = zen_kind.name + 's'
    
    if is_post or is_comment:
        subreddit = praw_object.subreddit
        subreddit_ids = mydb.get_id_params(subreddit.fullname, 'subreddits')
        obj_vars['zen_subreddit_id'] = subreddit_ids['zen_subreddit_id']
        insert_praw_object(subreddit)
        
        if has_valid_praw_author(praw_object):
            account = praw_object.author
            account_ids = mydb.get_id_params(account.fullname, 'accounts')
            obj_vars['zen_account_id'] = account_ids['zen_account_id']
            insert_praw_object(account)
    
    if is_comment:
        post = praw_object.submission
        post_ids = mydb.get_id_params(post.fullname, 'posts')
        obj_vars['zen_post_id'] = post_ids['zen_post_id']
        insert_praw_object(post)

    df = pd.DataFrame([obj_vars]).set_index(f'zen_{zen_kind.name}_detail_id')
    cleaned_frames, _ = clean_and_normalize(df, schema_name)
    schema = SchemaConfig(schema_name)
    insert_from_cleaned_frames(cleaned_frames, schema)

def insert_from_cleaned_frames(cleaned_frames, schema):
    schema_sing = schema.name[:-1]
    main_id = f'zen_{schema_sing}_id'
    detail_id = f'zen_{schema_sing}_detail_id'
    version_id = f'zen_{schema_sing}_version_id'
    
    hours_to_wait_dict = {'subreddits': 24,
                          'accounts': 24,
                          'posts': 1,
                          'comments': 0.25}
    
    hours_to_wait = hours_to_wait_dict[schema.name]
    
    main_df = cleaned_frames[schema.name]
    v1_detail_ids = main_df[main_df[version_id] == 1].index.to_list()
    
    mrd = mydb.most_recent_details(schema.name)
    target_sources = [(x,x) for x in cleaned_frames.keys()]\
                    + [(schema_sing + '_versions', schema.name),
                       (schema_sing + '_details', schema.name)]
    
    is_append = schema.writemode.value == WriteMode.append.value
    
    table_columns = {}
    # change this to parse from ddl to avoid querying the db
    # This parsing of the ddl should also establish which tables
    # are dependent on the details table
    all_required_columns = []
    for target, source in target_sources:
        required_columns = mydb.get_target_columns(schema.name, target)
        table_columns[target] = required_columns
        all_required_columns += required_columns
    

    # must be sorted so that things depending on details come last
    main_version_detail_tables = [x for x in target_sources if schema.name == x[1]]
    details_dependent_tables = [x for x in target_sources if schema.name != x[1]]
    target_sources = main_version_detail_tables + details_dependent_tables
    ##
    
    for target, source in target_sources:
        
        required_columns = table_columns[target]
        df = cleaned_frames[source].reset_index()
        if len(df):
            version_1 = df[detail_id].apply(lambda x: x in v1_detail_ids)
            cols_to_drop = set(df.columns).difference(required_columns)
            cols_to_drop.discard(main_id)
            df.drop(columns = cols_to_drop, inplace = True)
            df_version_1 = df[version_1]
            df_not_version_1 = df[~version_1]
            
            
            if is_append and len(df_not_version_1): 
                if target == schema.name:
                    df = df_version_1
                else:
                    zen_detail_ids_to_write = df[detail_id]
                    now_eastern = datetime.now(east_time).replace(tzinfo=None)
                    time_since = now_eastern - mrd['zen_created_at'] 
                    time_since_mask = time_since.apply(lambda x: x.seconds/60/60 > hours_to_wait)
                    mrd = mrd[time_since_mask]
                    if len(mrd):
                        detail_ids_to_keep = mrd[detail_id].to_list()
                    else:
                        detail_ids_to_keep = []
                    
                    time_since_mask_df = df_not_version_1[detail_id].apply(lambda x: x in detail_ids_to_keep)
                    df_not_version_1 = df_not_version_1[time_since_mask_df]
                    detail_ids_to_keep = df_not_version_1[detail_id].drop_duplicates().to_list()
                    if len(df_not_version_1) and len(mrd): # If there's no new data old enought o justify being written
                    
                        if 'details' in target or 'versions' in target:
    
                            seen_details = mrd[mrd[main_id].apply(lambda x: x in df_not_version_1[main_id])]
                            drop_dupes = pd.concat([seen_details[df_not_version_1.columns],df_not_version_1])
                            drop_dupes.drop(columns = detail_id, inplace = True)
                            drop_dupes = drop_dupes.drop_duplicates(keep=False)
                            zen_ids_to_write = set(drop_dupes[main_id])
                            
                            mask = df_not_version_1[main_id].apply(lambda x: x in zen_ids_to_write)
                            df_not_version_1 = df_not_version_1[mask]
                            zen_detail_ids_to_write = df_not_version_1[detail_id].to_list()
                    
                        if target == 'gildings':
                            #TODO: Dynamically append new gildings
                            pass
                        
                        if target == 'all_awardings':
                            #TODO: Dynamically append new awardings
                            pass
                            
                    df = pd.concat([df_version_1,df_not_version_1])
                        
                    if schema.name not in source:
                        mask = df[detail_id].apply(lambda x: x in zen_detail_ids_to_write)
                        df = df[mask]
            
            if len(df):
                cols_to_drop = set(df.columns).difference(required_columns)
                if len(cols_to_drop):
                    cols_to_drop_text = '\n'.join(cols_to_drop)
                    log.debug(f" Dropping from {target}:\n {cols_to_drop_text}")
                log.info(" Writing " + target)
    
                df.drop(columns = cols_to_drop)\
                    .to_sql(name = target,
                            schema = schema.name,
                            con = environ['MAIN_MEDIA_DATABASE'], 
                            if_exists = 'append', # DO NOT CHANGE THIS
                            index = False)
                log.info(f" Wrote something to {schema.name}.{target}")
            else:
                log.info(f" Didn't write anything to {schema.name}.{target}")
  