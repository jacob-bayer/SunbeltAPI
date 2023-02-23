# -*- coding: utf-8 -*-


from .models import *
from ariadne import convert_kwargs_to_snake_case
from datetime import datetime
from sqlalchemy import func

######### POSTS ###########

@convert_kwargs_to_snake_case
def resolve_posts(obj, info, **kwargs):
    post_selections = [x for x in info.field_nodes[0].selection_set.selections if x.name.value == 'posts'][0]
    fields = [x.name.value for x in post_selections.selection_set.selections]

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
    reddit_ids = kwargs.get('reddit_ids')
    sun_subreddit_id = kwargs.get('sun_subreddit_id')
    sun_account_id = kwargs.get('sun_account_id')
    limit = kwargs.get('limit')
    offset = kwargs.get('offset')

    posts = Post.query

    if reddit_ids:
        posts = posts.filter(Post.reddit_post_id.in_(reddit_ids))

    if sun_subreddit_id:
        posts = posts.filter(Post.sun_subreddit_id == sun_subreddit_id)

    if sun_account_id:
        posts = posts.filter(Post.sun_account_id == sun_account_id)

    if updated_before:
        updated_before = convert_date(updated_before)
        posts = posts.filter(Post.most_recent_version_updated_at < updated_before)

    if updated_after:
        updated_after = convert_date(updated_after)
        posts = posts.filter(Post.most_recent_version_updated_at > updated_after)

    if posted_before:
        posted_before = convert_date(posted_before)
        posts = posts.filter(Post.sun_created_at < posted_before)

    if posted_after:
        posted_after = convert_date(posted_after)
        posts = posts.filter(Post.sun_created_at > posted_after)
    


    if order_by: # Not sure this is necessary anymore
        posts = posts.join(PostVersion)
        posts = posts.join(PostDetail)
        order_by_to_cols = {
            'sun_unique_id' : Post.sun_post_id,
            'most_recent_sun_version_id': PostVersion.sun_post_version_id,
            'most_recent_sun_detail_id': PostDetail.sun_post_detail_id
        }

        for col, sort_by in order_by.items():
            col_to_order_by = order_by_to_cols.get(col)
            if sort_by == 'asc':
                posts = posts.order_by(col_to_order_by.asc())
            elif sort_by == 'desc':
                posts = posts.order_by(col_to_order_by.desc())

    total_count = posts.count()

    if offset:
        posts = posts.offset(offset)

    if limit:
        posts = posts.limit(limit)

    for field in fields.copy():
        if field in PostDetail.__table__.c.keys():
            fields.remove(field)
            fields.append('most_recent_detail.' + field)

    breakpoint()
    posts = posts.with_entities(*[getattr(Post, field) for field in fields]).all()    


    try:
        posts = [dict(zip(fields, post)) for post in posts]
        payload = {
            "success": True,
            "total_count": total_count,
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
            errors += [f"No posts found with Sun id {by_id}"]
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
    sun_post_id = kwargs.get('sun_unique_id') or kwargs.get('sun_post_id')
    
    if sun_post_id:
        post = Post.query.get(sun_post_id)
        details = [v.detail.to_dict() for v in post.versions]
    else:
        details = [detail.to_dict() for detail in PostDetail.query.all()] 
    
    try:
        post = Post.query.get(sun_post_id)
        payload = {
            "success": True,
            "postdetails": details
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Post matching id {sun_post_id} not found"]
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
    reddit_ids = kwargs.get('reddit_ids')
    order_by = kwargs.get('order_by')
    sun_post_id = kwargs.get('sun_post_id')
    reddit_ids = kwargs.get('reddit_ids')
    sun_subreddit_id = kwargs.get('sun_subreddit_id')
    limit = kwargs.get('limit')
    offset = kwargs.get('offset')

    comments = Comment.query

    if order_by: # Not sure this is necessary anymore
        comments = comments.join(CommentVersion)

    if reddit_ids:
        comments = comments.filter(Comment.reddit_comment_id.in_(reddit_ids))

    if sun_subreddit_id:
        comments = comments.filter(Comment.sun_subreddit_id == sun_subreddit_id)

    if updated_before:
        updated_before = convert_date(updated_before)
        comments = comments.filter(Comment.most_recent_version_updated_at < updated_before)

    if updated_after:
        updated_after = convert_date(updated_after)
        comments = comments.filter(Comment.most_recent_version_updated_at > updated_after)

    if commented_before:
        commented_before = convert_date(commented_before)
        comments = comments.filter(Comment.sun_created_at < commented_before)

    if commented_after:
        commented_after = convert_date(commented_after)
        comments = comments.filter(Comment.sun_created_at > commented_after)

    if sun_post_id:
        comments = comments.filter(Comment.sun_post_id == sun_post_id)

    if order_by: # Not sure this is necessary anymore
        comments = comments.join(CommentDetail)
        order_by_to_cols = {
            'sun_unique_id' : Comment.sun_comment_id,
            'most_recent_sun_version_id': CommentVersion.sun_comment_version_id,
            'most_recent_sun_detail_id': CommentDetail.sun_comment_detail_id
        }

        for col, sort_by in order_by.items():
            col_to_order_by = order_by_to_cols.get(col)
            if sort_by == 'asc':
                comments = comments.order_by(col_to_order_by.asc())
            elif sort_by == 'desc':
                comments = comments.order_by(col_to_order_by.desc())

    total_count = comments.count()

    if limit:
        comments = comments.limit(limit)

    if offset:
        comments = comments.offset(offset)

    try:
        comments = [comment.to_dict() for comment in comments]
        payload = {
            "success": True,
            "total_count": total_count,
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
            errors += [f"No comments found with Sun id {by_id}"]
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
    sun_comment_id = kwargs.get('sun_unique_id') or kwargs.get('sun_comment_id')
    
    if sun_comment_id:
        comment = Comment.query.get(sun_comment_id)
        details = [v.detail.to_dict() for v in comment.versions]
    else:
        details = [detail.to_dict() for detail in CommentDetail.query.all()] 
    
    try:
        comment = Comment.query.get(sun_comment_id)
        payload = {
            "success": True,
            "commentdetails": details
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Comment matching id {sun_comment_id} not found"]
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
    limit = kwargs.get('limit')
    offset = kwargs.get('offset')

    accounts = Account.query

    if order_by: # Not sure this is necessary anymore
        accounts = accounts.join(AccountVersion)

    if updated_before:
        updated_before = convert_date(updated_before)
        accounts = accounts.filter(Account.most_recent_version_updated_at < updated_before)

    if updated_after:
        updated_after = convert_date(updated_after)
        accounts = accounts.filter(Account.most_recent_version_updated_at > updated_after)

    if created_before:
        created_before = convert_date(created_before)
        accounts = accounts.filter(Account.sun_created_at < created_before)

    if created_after:
        created_after = convert_date(created_after)
        accounts = accounts.filter(Account.sun_created_at > created_after)

    if order_by: # Not sure this is necessary anymore
        accounts = accounts.join(AccountDetail)
        order_by_to_cols = {
            'sun_unique_id' : Account.sun_account_id,
            'most_recent_sun_version_id': AccountVersion.sun_account_version_id,
            'most_recent_sun_detail_id': AccountDetail.sun_account_detail_id
        }

        for col, sort_by in order_by.items():
            col_to_order_by = order_by_to_cols.get(col)
            if sort_by == 'asc':
                accounts = accounts.order_by(col_to_order_by.asc())
            elif sort_by == 'desc':
                accounts = accounts.order_by(col_to_order_by.desc())
    
    total_count = accounts.count()

    if limit:
        accounts = accounts.limit(limit)

    if offset:
        accounts = accounts.offset(offset)

    try:
        accounts = [account.to_dict() for account in accounts]
        payload = {
            "success": True,
            "total_count": total_count,
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
    name = kwargs.get('name')
    errors = []

    if by_id:
        account = Account.query.get(by_id)
        if not account:
            errors += [f"No accounts found with Sun id {by_id}"]
    if reddit_id:
        account = Account.query.filter_by(reddit_account_id=reddit_id).all()
        if len(account) > 1:
            errors += [f"Multiple accounts found with reddit_id {reddit_id}"]
        elif len(account) == 0: 
            errors += [f"No accounts found with reddit_id {reddit_id}"]
        else:
            account = account[0]

    if name:
        account = Account.query.filter_by(name=name).all()
        if len(account) > 1:
            errors += [f"Multiple accounts found with name {name}"]
        elif len(account) == 0: 
            errors += [f"No accounts found with name {name}"]
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
    sun_account_id = kwargs.get('sun_unique_id') or kwargs.get('sun_account_id')
    
    if sun_account_id:
        account = Account.query.get(sun_account_id)
        details = [v.detail.to_dict() for v in account.versions]
    else:
        details = [detail.to_dict() for detail in AccountDetail.query.all()] 
    
    try:
        account = Account.query.get(sun_account_id)
        payload = {
            "success": True,
            "accountdetails": details
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Account matching id {sun_account_id} not found"]
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
    reddit_ids = kwargs.get('reddit_ids')
    names = kwargs.get('names')
    order_by = kwargs.get('order_by')
    limit = kwargs.get('limit')
    offset = kwargs.get('offset')

    subreddits = Subreddit.query
    
    if names:
        subreddits = subreddits.filter(func.lower(Subreddit.display_name).in_(names))

    if reddit_ids:
        subreddits = subreddits.filter(Subreddit.reddit_subreddit_id.in_(reddit_ids))

    if updated_before:
        updated_before = convert_date(updated_before)
        subreddits = subreddits.filter(Subreddit.most_recent_version_updated_at < updated_before)

    if updated_after:
        updated_after = convert_date(updated_after)
        subreddits = subreddits.filter(Subreddit.most_recent_version_updated_at > updated_after)

    if created_before:
        created_before = convert_date(created_before)
        subreddits = subreddits.filter(Subreddit.sun_created_at < created_before)

    if created_after:
        created_after = convert_date(created_after)
        subreddits = subreddits.filter(Subreddit.sun_created_at > created_after)

    if order_by: # Not sure this is necessary anymore this should maybe be a hybrid property
        subreddits = subreddits.join(SubredditVersion)
        subreddits = subreddits.join(SubredditDetail)
        order_by_to_cols = {
            'sun_unique_id' : Subreddit.sun_subreddit_id,
            'most_recent_sun_version_id': SubredditVersion.sun_subreddit_version_id,
            'most_recent_sun_detail_id': SubredditDetail.sun_subreddit_detail_id
        }

        for col, sort_by in order_by.items():
            col_to_order_by = order_by_to_cols.get(col)
            if sort_by == 'asc':
                subreddits = subreddits.order_by(col_to_order_by.asc())
            elif sort_by == 'desc':
                subreddits = subreddits.order_by(col_to_order_by.desc())

    total_count = subreddits.count()

    if limit:
        subreddits = subreddits.limit(limit)

    if offset:
        subreddits = subreddits.offset(offset)
        
    try:
        subreddits = [subreddit.to_dict() for subreddit in subreddits]
        payload = {
            "success": True,
            "total_count": total_count,
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
    name = kwargs.get('name')
    errors = []

    if by_id:
        subreddit = Subreddit.query.get(by_id)
        if not subreddit:
            errors += [f"No subreddits found with Sun id {by_id}"]
    if reddit_id:
        subreddit = Subreddit.query.filter_by(reddit_subreddit_id=reddit_id).all()
        if len(subreddit) > 1:
            errors += [f"Multiple subreddits found with reddit_id {reddit_id}"]
        elif len(subreddit) == 0: 
            errors += [f"No subreddits found with reddit_id {reddit_id}"]
        else:
            subreddit = subreddit[0]

    if name:
        subreddit = Subreddit.query.filter(func.lower(Subreddit.display_name)==name).first()
        if not subreddit:
            errors += [f"No subreddits found with name {name}"]


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
    sun_subreddit_id = kwargs.get('sun_unique_id') or kwargs.get('sun_subreddit_id')
    
    if sun_subreddit_id:
        subreddit = Subreddit.query.get(sun_subreddit_id)
        details = [v.detail.to_dict() for v in subreddit.versions]
    else:
        details = [detail.to_dict() for detail in SubredditDetail.query.all()] 
    
    try:
        subreddit = Subreddit.query.get(sun_subreddit_id)
        payload = {
            "success": True,
            "subredditdetails": details
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Subreddit matching id {sun_subreddit_id} not found"]
        }

    return payload
    