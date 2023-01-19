# -*- coding: utf-8 -*-


from sunbelt.models import *
from ariadne import convert_kwargs_to_snake_case
from datetime import datetime

######### POSTS ###########

@convert_kwargs_to_snake_case
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
    order_by = kwargs.get('order_by')

    posts = Post.query

    if updated_before or updated_after or order_by:
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
    
    if order_by:
        posts = posts.join(PostDetail)
        order_by_to_cols = {
            'zen_unique_id' : Post.zen_post_id,
            'most_recent_zen_version_id': PostVersion.zen_post_version_id,
            'most_recent_zen_detail_id': PostDetail.zen_post_detail_id
        }

        for col, sort_by in order_by.items():
            col_to_order_by = order_by_to_cols.get(col)
            if sort_by == 'asc':
                posts = posts.order_by(col_to_order_by.asc())
            elif sort_by == 'desc':
                posts = posts.order_by(col_to_order_by.desc())

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
    reddit_id = kwargs.get('reddit_id')
    errors = []

    if by_id and reddit_id:
        errors += ["Cannot specify both by_id and reddit_id"]

    if by_id:
        post = Post.query.get(by_id)
        if not post:
            errors += [f"No posts found with zen id {by_id}"]
    if reddit_id:
        post = Post.query.filter_by(reddit_post_id=reddit_id).all()
        if len(post) > 1:
            errors += [f"Multiple posts found with reddit_id {reddit_id}"]
        elif len(post) == 0: 
            errors += [f"No posts found with reddit_id {reddit_id}"]
        else:
            post = post[0]

    if not errors:
        payload = {
            "success": True,
            "post": post.to_dict()
        }
    else:
        payload = {
            "success": False,
            "errors": errors
        }

    return payload

@convert_kwargs_to_snake_case
def resolve_post_detail(obj, info, **kwargs):
    by_id = kwargs.get('by_id')

    try:
        post_detail = PostDetail.query.get(by_id)
        payload = {
            "success": True,
            "postdetail": post_detail.to_dict()
        }

    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Post detail matching id {by_id} not found"]
        }
    
    return payload

@convert_kwargs_to_snake_case
def resolve_post_details(obj, info, **kwargs):
    zen_post_id = kwargs.get('zen_unique_id') or kwargs.get('zen_post_id')
    
    if zen_post_id:
        post = Post.query.get(zen_post_id)
        details = [v.detail.to_dict() for v in post.versions]
    else:
        details = [detail.to_dict() for detail in PostDetail.query.all()] 
    
    try:
        post = Post.query.get(zen_post_id)
        payload = {
            "success": True,
            "postdetails": details
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Post matching id {zen_post_id} not found"]
        }

    return payload




######## COMMENTS ##########

@convert_kwargs_to_snake_case
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
    order_by = kwargs.get('order_by')

    comments = Comment.query

    if updated_before or updated_after or order_by:
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

    if order_by:
        comments = comments.join(CommentDetail)
        order_by_to_cols = {
            'zen_unique_id' : Comment.zen_comment_id,
            'most_recent_zen_version_id': CommentVersion.zen_comment_version_id,
            'most_recent_zen_detail_id': CommentDetail.zen_comment_detail_id
        }

        for col, sort_by in order_by.items():
            col_to_order_by = order_by_to_cols.get(col)
            if sort_by == 'asc':
                comments = comments.order_by(col_to_order_by.asc())
            elif sort_by == 'desc':
                comments = comments.order_by(col_to_order_by.desc())

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
    reddit_id = kwargs.get('reddit_id')
    errors = []

    if by_id:
        comment = Comment.query.get(by_id)
        if not comment:
            errors += [f"No comments found with zen id {by_id}"]
    if reddit_id:
        comment = Comment.query.filter_by(reddit_comment_id=reddit_id).all()
        if len(comment) > 1:
            errors += [f"Multiple comments found with reddit_id {reddit_id}"]
        elif len(comment) == 0: 
            errors += [f"No comments found with reddit_id {reddit_id}"]
        else:
            comment = comment[0]

    if not errors:
        payload = {
            "success": True,
            "comment": comment.to_dict()
        }
    else:
        payload = {
            "success": False,
            "errors": errors
        }

    return payload


@convert_kwargs_to_snake_case
def resolve_comment_detail(obj, info, **kwargs):
    by_id = kwargs.get('by_id')

    try:
        comment_detail = CommentDetail.query.get(by_id)
        payload = {
            "success": True,
            "commentdetail": comment_detail.to_dict()
        }

    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Comment detail matching id {by_id} not found"]
        }

    return payload

@convert_kwargs_to_snake_case
def resolve_comment_details(obj, info, **kwargs):
    zen_comment_id = kwargs.get('zen_unique_id') or kwargs.get('zen_comment_id')
    
    if zen_comment_id:
        comment = Comment.query.get(zen_comment_id)
        details = [v.detail.to_dict() for v in comment.versions]
    else:
        details = [detail.to_dict() for detail in CommentDetail.query.all()] 
    
    try:
        comment = Comment.query.get(zen_comment_id)
        payload = {
            "success": True,
            "commentdetails": details
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Comment matching id {zen_comment_id} not found"]
        }

    return payload


######## ACCOUNTS ##########

@convert_kwargs_to_snake_case
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
    order_by = kwargs.get('order_by')

    accounts = Account.query

    if updated_before or updated_after or order_by:
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

    if order_by:
        accounts = accounts.join(AccountDetail)
        order_by_to_cols = {
            'zen_unique_id' : Account.zen_account_id,
            'most_recent_zen_version_id': AccountVersion.zen_account_version_id,
            'most_recent_zen_detail_id': AccountDetail.zen_account_detail_id
        }

        for col, sort_by in order_by.items():
            col_to_order_by = order_by_to_cols.get(col)
            if sort_by == 'asc':
                accounts = accounts.order_by(col_to_order_by.asc())
            elif sort_by == 'desc':
                accounts = accounts.order_by(col_to_order_by.desc())
        
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
    reddit_id = kwargs.get('reddit_id')
    errors = []

    if by_id:
        account = Account.query.get(by_id)
        if not account:
            errors += [f"No accounts found with zen id {by_id}"]
    if reddit_id:
        account = Account.query.filter_by(reddit_account_id=reddit_id).all()
        if len(account) > 1:
            errors += [f"Multiple accounts found with reddit_id {reddit_id}"]
        elif len(account) == 0: 
            errors += [f"No accounts found with reddit_id {reddit_id}"]
        else:
            account = account[0]

    if not errors:
        payload = {
            "success": True,
            "account": account.to_dict()
        }
    else:
        payload = {
            "success": False,
            "errors": errors
        }

    return payload

@convert_kwargs_to_snake_case
def resolve_account_detail(obj, info, **kwargs):
    by_id = kwargs.get('by_id')

    try:
        account_detail = AccountDetail.query.get(by_id)
        payload = {
            "success": True,
            "accountdetail": account_detail.to_dict()
        }

    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Account detail matching id {by_id} not found"]
        }

    return payload

@convert_kwargs_to_snake_case
def resolve_account_details(obj, info, **kwargs):
    zen_account_id = kwargs.get('zen_unique_id') or kwargs.get('zen_account_id')
    
    if zen_account_id:
        account = Account.query.get(zen_account_id)
        details = [v.detail.to_dict() for v in account.versions]
    else:
        details = [detail.to_dict() for detail in AccountDetail.query.all()] 
    
    try:
        account = Account.query.get(zen_account_id)
        payload = {
            "success": True,
            "accountdetails": details
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Account matching id {zen_account_id} not found"]
        }

    return payload

######## SUBREDDITS ##########

@convert_kwargs_to_snake_case
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
        order_by = kwargs.get('order_by')

        subreddits = Subreddit.query
    
        if updated_before or updated_after or order_by:
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

        if order_by:
            subreddits = subreddits.join(SubredditDetail)
            order_by_to_cols = {
                'zen_unique_id' : Subreddit.zen_subreddit_id,
                'most_recent_zen_version_id': SubredditVersion.zen_subreddit_version_id,
                'most_recent_zen_detail_id': SubredditDetail.zen_subreddit_detail_id
            }

            for col, sort_by in order_by.items():
                col_to_order_by = order_by_to_cols.get(col)
                if sort_by == 'asc':
                    subreddits = subreddits.order_by(col_to_order_by.asc())
                elif sort_by == 'desc':
                    subreddits = subreddits.order_by(col_to_order_by.desc())
            
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
    reddit_id = kwargs.get('reddit_id')
    errors = []

    if by_id:
        subreddit = Subreddit.query.get(by_id)
        if not subreddit:
            errors += [f"No subreddits found with zen id {by_id}"]
    if reddit_id:
        subreddit = Subreddit.query.filter_by(reddit_subreddit_id=reddit_id).all()
        if len(subreddit) > 1:
            errors += [f"Multiple subreddits found with reddit_id {reddit_id}"]
        elif len(subreddit) == 0: 
            errors += [f"No subreddits found with reddit_id {reddit_id}"]
        else:
            subreddit = subreddit[0]

    if not errors:
        payload = {
            "success": True,
            "subreddit": subreddit.to_dict()
        }
    else:
        payload = {
            "success": False,
            "errors": errors
        }

    return payload

@convert_kwargs_to_snake_case
def resolve_subreddit_detail(obj, info, **kwargs):
    by_id = kwargs.get('by_id')

    try:
        subreddit_detail = SubredditDetail.query.get(by_id)
        payload = {
            "success": True,
            "subredditdetail": subreddit_detail.to_dict()
        }

    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Subreddit detail matching id {by_id} not found"]
        }

    return payload

@convert_kwargs_to_snake_case
def resolve_subreddit_details(obj, info, **kwargs):
    zen_subreddit_id = kwargs.get('zen_unique_id') or kwargs.get('zen_subreddit_id')
    
    if zen_subreddit_id:
        subreddit = Subreddit.query.get(zen_subreddit_id)
        details = [v.detail.to_dict() for v in subreddit.versions]
    else:
        details = [detail.to_dict() for detail in SubredditDetail.query.all()] 
    
    try:
        subreddit = Subreddit.query.get(zen_subreddit_id)
        payload = {
            "success": True,
            "subredditdetails": details
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Subreddit matching id {zen_subreddit_id} not found"]
        }

    return payload
    