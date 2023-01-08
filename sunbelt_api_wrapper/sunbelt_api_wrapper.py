# -*- coding: utf-8 -*-
import requests
import json
import pandas as pd

def wrap_in_brackets(string):
    return '{' + string + '}'

class SunbeltClient():
    
    def __init__(self, host):
        self.host = host
        
    def posts(self, *args, **kwargs):
        return self.search(kind = 'posts', *args, **kwargs)
        
        
    def search(self, kind, *args, **kwargs):
        #variables_dict = {'$' + key: value for key, value in kwargs.items()}
        variables_str = ', '.join(f'{key}: "{value}"' for key, value in kwargs.items())
        
    # =============================================================================
    #         declare_args = {'$updated_before': 'String!',
    #                      '$updated_after': 'String!',
    #                      '$posted_before': 'String!',
    #                      '$posted_after': 'String!'}
    # 
    #         declare_args = ', '.join(f'{key}: {value}' for key, value in declare_args.items()
    #                      if variables_dict.get(key))
    # =============================================================================
                
    
        graphql_query_name = '' #f'GetPosts({declare_args}) '
        graphql_post_func = f'{kind}({variables_str}) '
        
        fields = wrap_in_brackets(' \n '.join(args))
        body = graphql_post_func + wrap_in_brackets(f'{kind} ' + fields)
        body = wrap_in_brackets(body)
        
        query = 'query ' + graphql_query_name + body
        
        data = {
          'query': query,
          #'variables' : variables
        }
        
        headers = {'Content-Type': 'application/json'}
        
        r = requests.post(self.host, 
                          data=json.dumps(data), 
                          headers=headers)
        
        if r.ok:
            return r.json()['data'][kind][kind]
        else:
            print(query)
            return r.json() 
        