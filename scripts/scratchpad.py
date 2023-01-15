#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 11:37:05 2023

@author: jacob
"""

from SAWP import SunbeltClient

sunbelt = SunbeltClient("http://127.0.0.1:5000/graphql")
sunbelt.post_details.zen_detail_id
    
post = sunbelt.posts.first()

post.versions.all()

vs = list(post.versions.all())
max(sunbelt.post_details.zen_detail_id)


