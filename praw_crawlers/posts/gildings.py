#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 18:17:11 2022

@author: jacob
"""


import pandas as pd
from mydatabasemodule.praw_output_cleaner import clean_data_frame

### THE FUNC CAN ALREADY DO THIS
help(pd.json_normalize)

def pd_json_normalize_list_of_dicts(df, index_name = None):
    index_name = index_name or df.index.name
    if not index_name:
        ermsg = "Must provide index name or name the index in the dataframe"
        raise ValueError(ermsg)
        
    all_data = pd.DataFrame()
    for id_col, data in df.items():
        data = pd.json_normalize(data)
        data.insert(0,'post_id', id_col)
                            
        all_data = pd.concat([
            all_data,
            data], 
            axis = 0,
            ignore_index = True)
    all_data.columns = [x.replace('.','_') for x in all_data.columns]
    return all_data.set_index(index_name)

gildings = frames['iterables']['gildings']
gildings = pd.json_normalize(gildings)
gildings = gildings.melt(value_vars = gildings.columns, 
                         var_name = 'reddit_gid', 
                         #value_name = 'not sure',
                         ignore_index=False)\
                        .dropna(subset=['value'])
gildings.index.name = 'post_id'

all_awardings = frames['iterables']['all_awardings']
all_awardings = pd_json_normalize_list_of_dicts(all_awardings)
# I don't care about the iterables they are stupid for this one
all_awardings = clean_data_frame(all_awardings)['cleaned_dataframe']
keepcols = [x for x in all_awardings.columns 
           if 'tiers_by_required_awardings' not in x]
all_awardings = all_awardings[keepcols]


previews = frames['iterables']['preview']
previews = pd.json_normalize(previews)
previews = clean_data_frame(previews)
previews = pd_json_normalize_list_of_dicts(previews['cleaned_dataframe'])
images = pd_json_normalize_list_of_dicts(previews['images'])
resolutions = pd_json_normalize_list_of_dicts(images['resolutions'])



media = frames['iterables']['media']
    
media = pd.json_normalize(media)
    
    
    
    
    
    
    