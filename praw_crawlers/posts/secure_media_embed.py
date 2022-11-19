#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 18:17:11 2022

@author: jacob
"""

iterables = [x for x in frames['iterables'].columns if x != 'post_id']

for col in iterables:
    
    
    
    newframe = frames['iterables'][['post_id',col]].dropna(subset=col)
    valid = newframe[col].map(lambda x: len(x) > 0)
    if any(valid):  
        newframe = newframe[valid].reset_index(drop = True)
        layers_deep = count_lists(newframe[col].iloc[0])
        final_layer = pd.json_normalize(newframe[col])
        while layers_deep > 0:
            final_layer = pd.json_normalize(final_layer[0])
            layers_deep = layers_deep - 1
        final_layer['post_id'] = newframe['post_id']
        
        final_layer\
            .to_sql(name = col,
                    schema = schema_name,
                    con = environ['MAIN_MEDIA_DATABASE'], 
                    if_exists='replace',
                    index = False)
        
    
test = pd.json_normalize(notnull[valid])
test = pd.json_normalize(test[0])
