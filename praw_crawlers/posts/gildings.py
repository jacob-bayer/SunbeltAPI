#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 18:17:11 2022

@author: jacob
"""


if frames['iterables']
gildings = frames['iterables']['gildings']
gildings = json_normalize_with_id(gildings)
gildings = gildings.melt(value_vars = gildings.columns, 
                         var_name = 'reddit_gid', 
                         #value_name = 'not sure',
                         ignore_index=False)\
                         .dropna(subset=['value'])

all_awardings = frames['iterables']['all_awardings']
all_awardings = pd_json_normalize_list_of_dicts(all_awardings)
# I don't care about the iterables they are stupid for this one
all_awardings = clean_data_frame(all_awardings)['cleaned_dataframe']
keepcols = [x for x in all_awardings.columns 
           if 'tiers_by_required_awardings' not in x]
all_awardings = all_awardings[keepcols]


previews = frames['iterables']['preview']
previews = json_normalize_with_id(previews)
previews = clean_data_frame(previews)
images = pd_json_normalize_list_of_dicts(previews['iterables']['images'])
previews = previews['cleaned_dataframe']
resolutions = pd_json_normalize_list_of_dicts(images['resolutions'])
images.drop(columns='resolutions', inplace = True)
previews = pd.concat([previews,images], axis=1)


media = json_normalize_with_id(frames['iterables']['media'])
media_embed = json_normalize_with_id(frames['iterables']['media_embed'])
secure_media = json_normalize_with_id(frames['iterables']['secure_media'])



# unknown
frames['iterables']['secure_media_embed']

# unknown    
frames['iterables']['mod_reports']
   
# unknown 
frames['iterables']['comments_by_id']

# dont care
frames['iterables']['treatment_tags']

# not sure if i want it
frames['iterables']['content_categories']

# unknown
frames['iterables']['user_reports']

# dont care
frames['iterables']['link_flair_richtext']

# unknown
frames['iterables']['author_flair_richtext']


    