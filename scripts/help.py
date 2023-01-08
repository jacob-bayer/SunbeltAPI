#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 12:57:19 2022

@author: jacob
"""

# All objects need to reach the fetched
# state so that all the vars are available.
# This is achieved by calling any attribute of the
# object that is not available in the basic vars (such as url).
# For posts this is acheived by replace more

# https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
# current_time = datetime.now().strftime("%b-%d %-I:%M:%S %p")
# log.info(f" Replacing comments for post. Started at {current_time}. This may take a while.")
   
# not calling list leaves out some comments somehow
# all replies to comments (all comments total) will be included here
# current_time = datetime.now().strftime("%b-%d %-I:%M:%S %p")
# log.info(f" Finished replacing comments at {current_time}.")


# Posts have a parent id and crosspost count so no real need to get these
#crossposts = crossposts + [vars(x) for x in post.duplicates()]


################### This is how duplicates works ###################################
crossposts = [x for x in post.duplicates()]
crosspost_comments = [[vars(y) for y in x.comments] for x in crossposts]
crosspostsdf = pd.DataFrame(vars(x) for x in crossposts]


crosspost_duplicates_example = [x for x in crossposts[0].duplicates()]
post in crosspost_duplicates_example # is true

######################################################


#################### This is how comments works ##################################
commentdf = pd.DataFrame()
commentdf['comment'] = comments
commentdf['depth'] = [x.depth for x in comments]
commentdf['permalink'] = [x.permalink for x in comments]
commentdf['submission'] = [x.submission for x in comments]
commentdf['parent_id'] = [x.parent_id for x in comments]
commentdf['body'] = [x.body for x in comments]
commentdf['parent_body'] = [x.parent().body if x.depth > 0 else None for x in comments]
commentdf['replies'] = [len(x.replies.list()) for x in comments]



######################################################