# -*- coding: utf-8 -*-

import pandas as pd
import logging

log = logging.getLogger("CLEANER")

def has_valid_praw_author(praw_object_with_author):
    valid = False
    if praw_object_with_author.author:
        # TODO: Add suspended accounts to dwh
        _ = praw_object_with_author.author.total_karma
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
    log.info('Cleaning and sorting')
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
                    rename_dict[col] = 'reddit_parent_id'
                else:
                    rename_dict[col] = f'reddit_{obj_name}_id'
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
            log.info('Iterating ' + table)
            gildings = json_normalize_with_id(data)
            gildings = gildings.melt(value_vars = gildings.columns, 
                                     var_name = 'reddit_gid', 
                                     #value_name = 'not sure',
                                     ignore_index = False)\
                                     .dropna(subset = ['value'])
            final_dict['gildings'] = gildings
                        
        if table == 'all_awardings':
            log.info('Iterating ' + table)
            data = data[data.map(lambda x: len(x) > 0)]
            if len(data):
                all_awardings = pd_json_normalize_list_of_dicts(data)
                # I don't care about the iterables they are stupid for this one
                all_awardings = clean_and_sort(all_awardings)['cleaned_dataframe']
                keepcols = [x for x in all_awardings.columns 
                           if 'tiers_by_required_awardings' not in x]
                all_awardings = all_awardings[keepcols]
                final_dict['all_awardings'] = all_awardings
            
        if table == 'previews':
            log.info('Iterating ' + table)
            previews = json_normalize_with_id(data)
            previews = clean_and_sort(previews)
            images = pd_json_normalize_list_of_dicts(previews['iterables']['images'])
            previews = previews['cleaned_dataframe']
            final_dict['resolutions'] = pd_json_normalize_list_of_dicts(images['resolutions'])
            images.drop(columns='resolutions', inplace = True)
            final_dict['previews'] = pd.concat([previews,images], axis=1)
            
        if table == 'media':
            log.info('Iterating ' + table)
            final_dict['media'] = json_normalize_with_id(data)
        if table == 'media_embed':
            log.info('Iterating ' + table)
            final_dict['media_embed'] = json_normalize_with_id(data)
        if table == 'secure_media': 
            log.info('Iterating ' + table)
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

            
def clean_and_normalize(df, main_table_name):
    ready_to_write_dict = {}
    cleaned_dict = clean_and_sort(df)
    normalized_iterables_dict = normalize_iterables(cleaned_dict['iterables'])
    # main one must come first
    ready_to_write_dict.update({main_table_name : 
                                cleaned_dict['cleaned_dataframe']})
    ready_to_write_dict.update(normalized_iterables_dict)

    return ready_to_write_dict, cleaned_dict['objects']
