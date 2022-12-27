#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 17:33:29 2022

@author: jacob
"""
from pmaw import PushshiftAPI

api = PushshiftAPI()

# The `search_comments` and `search_submissions` methods return generator objects
gen = api.search_comments(subreddit='dataisbeautiful')
results = list(gen)

import pandas as pd
import os

con = os.environ['MAIN_MEDIA_DATABASE']
db_df = pd.read_sql("""
                    SELECT * 
                    FROM comments.comments
                    JOIN comments.most_recent_details USING (zen_comment_id)
                    """, con).set_index('zen_comment_id')

results_df = pd.DataFrame(results)

from mydatabasemodule.praw_output_cleaner import clean_and_normalize

results_df.index.name = 'zen_comment_id'
results_frames, _ = clean_and_normalize(results_df, 'comments')

cleaned_results_df = results_frames['comments']

missing_from_pmaw = set(db_df.columns).difference(cleaned_results_df.columns)
missing_from_praw = set(cleaned_results_df.columns).difference(db_df.columns)

missing_from_pmaw_dict = {}
for col in missing_from_pmaw:
    datum = db_df[col].iloc[0]
    if isinstance(datum, pd.Timestamp):
        datum = datum.strftime('%m-%d-%Y')
    missing_from_pmaw_dict[col] = datum

missing_from_praw_dict = {}
for col in missing_from_praw:
    missing_from_praw_dict[col] = cleaned_results_df[col].iloc[0]


