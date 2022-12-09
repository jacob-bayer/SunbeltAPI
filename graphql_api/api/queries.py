# -*- coding: utf-8 -*-

from models import Post
from ariadne import convert_kwargs_to_snake_case
from datetime import datetime

def resolve_posts(obj, info):
    try:
        posts = [post.to_dict() for post in Post.query.all()]
        payload = {
            "success": True,
            "posts": posts
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload

@convert_kwargs_to_snake_case
def resolve_post(obj, info, post_post_id):
    try:
        post = Post.query.get(post_post_id)
        payload = {
            "success": True,
            "post": post.to_dict()
        }

    except AttributeError:  # post not found
        payload = {
            "success": False,
            "errors": [f"Post item matching id {post_post_id} not found"]
        }

    return payload

