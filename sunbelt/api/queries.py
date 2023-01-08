# -*- coding: utf-8 -*-


from sunbelt.models import Post, PostVersion
from ariadne import convert_kwargs_to_snake_case
from datetime import datetime

def resolve_posts(obj, info, **kwargs):
    
    def convert_date(date):
        try:
            return datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
        except ValueError:
            return datetime.strptime(date, '%d-%m-%Y')
        except:
            raise ValueError("Invalid date format, should be 'dd-mm-yyyy' or 'dd-mm-yyyy hh:mm:ss'")
    
    posted_before = kwargs.get('posted_before')
    posted_after = kwargs.get('posted_after')
    updated_before = kwargs.get('updated_before')
    updated_after = kwargs.get('updated_after')

    posts = Post.query

    if updated_before or updated_after:
        posts = posts.join(PostVersion)

    if updated_before:
        updated_before = convert_date(updated_before)
        posts = posts.filter(PostVersion.zen_created_at < updated_before)

    if updated_after:
        updated_after = convert_date(updated_after)
        posts = posts.filter(PostVersion.zen_created_at > updated_after)

    if posted_before:
        posted_before = convert_date(posted_before)
        posts = posts.filter(Post.zen_created_at < posted_before)

    if posted_after:
        posted_after = convert_date(posted_after)
        posts = posts.filter(Post.zen_created_at > posted_after)
        
    try:
        posts = [post.to_dict() for post in posts]
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
def resolve_post(obj, info, **kwargs):
    post_by_id = kwargs.get('post_by_id')

    try:
        post = Post.query.get(post_by_id)
        payload = {
            "success": True,
            "post": post.to_dict()
        }

    except AttributeError:  # post not found
        payload = {
            "success": False,
            "errors": [f"Post item matching id {post_by_id} not found"]
        }

    return payload

