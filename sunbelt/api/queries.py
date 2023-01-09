# -*- coding: utf-8 -*-


from sunbelt.models import *
from ariadne import convert_kwargs_to_snake_case
from datetime import datetime

######### POSTS ###########

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
    
    #breakpoint()
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
    by_id = kwargs.get('by_id')

    try:
        post = Post.query.get(by_id)
        payload = {
            "success": True,
            "post": post.to_dict()
        }

    except AttributeError:  # post not found
        payload = {
            "success": False,
            "errors": [f"Post item matching id {by_id} not found"]
        }

    return payload


######## COMMENTS ##########

def resolve_comments(obj, info, **kwargs):


    def convert_date(date):
        try:
            return datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
        except ValueError:
            return datetime.strptime(date, '%d-%m-%Y')
        except:
            raise ValueError("Invalid date format, should be 'dd-mm-yyyy' or 'dd-mm-yyyy hh:mm:ss'")
    
    commented_before = kwargs.get('commented_before')
    commented_after = kwargs.get('commented_after')
    updated_before = kwargs.get('updated_before')
    updated_after = kwargs.get('updated_after')

    comments = Comment.query

    if updated_before or updated_after:
        comments = comments.join(CommentVersion)

    if updated_before:
        updated_before = convert_date(updated_before)
        comments = comments.filter(CommentVersion.zen_created_at < updated_before)

    if updated_after:
        updated_after = convert_date(updated_after)
        comments = comments.filter(CommentVersion.zen_created_at > updated_after)

    if commented_before:
        commented_before = convert_date(commented_before)
        comments = comments.filter(Comment.zen_created_at < commented_before)

    if commented_after:
        commented_after = convert_date(commented_after)
        comments = comments.filter(Comment.zen_created_at > commented_after)

    try:
        comments = [comment.to_dict() for comment in comments]
        payload = {
            "success": True,
            "comments": comments
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload

@convert_kwargs_to_snake_case
def resolve_comment(obj, info, **kwargs):
    by_id = kwargs.get('by_id')

    try:
        comment = Comment.query.get(by_id)
        payload = {
            "success": True,
            "comment": comment.to_dict()
        }

    except AttributeError:  # comment not found
        payload = {
            "success": False,
            "errors": [f"Comment item matching id {by_id} not found"]
        }

    return payload

######## ACCOUNTS ##########

def resolve_accounts(obj, info, **kwargs):
        
    def convert_date(date):
        try:
            return datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
        except ValueError:
            return datetime.strptime(date, '%d-%m-%Y')
        except:
            raise ValueError("Invalid date format, should be 'dd-mm-yyyy' or 'dd-mm-yyyy hh:mm:ss'")
    
    created_before = kwargs.get('created_before')
    created_after = kwargs.get('created_after')
    updated_before = kwargs.get('updated_before')
    updated_after = kwargs.get('updated_after')

    accounts = Account.query

    if updated_before or updated_after:
        accounts = accounts.join(AccountVersion)

    if updated_before:
        updated_before = convert_date(updated_before)
        accounts = accounts.filter(AccountVersion.zen_created_at < updated_before)

    if updated_after:
        updated_after = convert_date(updated_after)
        accounts = accounts.filter(AccountVersion.zen_created_at > updated_after)

    if created_before:
        created_before = convert_date(created_before)
        accounts = accounts.filter(Account.zen_created_at < created_before)

    if created_after:
        created_after = convert_date(created_after)
        accounts = accounts.filter(Account.zen_created_at > created_after)
        
    try:
        accounts = [account.to_dict() for account in accounts]
        payload = {
            "success": True,
            "accounts": accounts
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload

@convert_kwargs_to_snake_case
def resolve_account(obj, info, **kwargs):
    by_id = kwargs.get('by_id')

    try:
        account = Account.query.get(by_id)
        payload = {
            "success": True,
            "account": account.to_dict()
        }

    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Account matching id {by_id} not found"]
        }

    return payload

######## SUBREDDITS ##########

def resolve_subreddits(obj, info, **kwargs):
        
        def convert_date(date):
            try:
                return datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
            except ValueError:
                return datetime.strptime(date, '%d-%m-%Y')
            except:
                raise ValueError("Invalid date format, should be 'dd-mm-yyyy' or 'dd-mm-yyyy hh:mm:ss'")
        
        created_before = kwargs.get('created_before')
        created_after = kwargs.get('created_after')
        updated_before = kwargs.get('updated_before')
        updated_after = kwargs.get('updated_after')
    
        subreddits = Subreddit.query
    
        if updated_before or updated_after:
            subreddits = subreddits.join(SubredditVersion)
    
        if updated_before:
            updated_before = convert_date(updated_before)
            subreddits = subreddits.filter(SubredditVersion.zen_created_at < updated_before)
    
        if updated_after:
            updated_after = convert_date(updated_after)
            subreddits = subreddits.filter(SubredditVersion.zen_created_at > updated_after)
    
        if created_before:
            created_before = convert_date(created_before)
            subreddits = subreddits.filter(Subreddit.zen_created_at < created_before)
    
        if created_after:
            created_after = convert_date(created_after)
            subreddits = subreddits.filter(Subreddit.zen_created_at > created_after)
            
        try:
            subreddits = [subreddit.to_dict() for subreddit in subreddits]
            payload = {
                "success": True,
                "subreddits": subreddits
            }
        except Exception as error:
            payload = {
                "success": False,
                "errors": [str(error)]
            }
        return payload

@convert_kwargs_to_snake_case
def resolve_subreddit(obj, info, **kwargs):
    by_id = kwargs.get('by_id')

    try:
        subreddit = Subreddit.query.get(by_id)
        payload = {
            "success": True,
            "subreddit": subreddit.to_dict()
        }

    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Subreddit matching id {by_id} not found"]
        }

    return payload