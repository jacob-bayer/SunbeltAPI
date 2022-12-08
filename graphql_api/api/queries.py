# -*- coding: utf-8 -*-

from .models import Post

def resolve_posts(obj, info):
    try:
        posts = [Post.to_dict() for Post in Post.query.all()]
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


