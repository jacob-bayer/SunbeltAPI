from sunbelt.models import *
from ariadne import convert_kwargs_to_snake_case
import json

# create comment
@convert_kwargs_to_snake_case
def resolve_create_comment(obj, info, from_json):

    praw_obj = json.loads(from_json)

    comment_columns = Comment.__table__.c.keys()
    version_columns = CommentVersion.__table__.c.keys()
    detail_columns = CommentDetail.__table__.c.keys()
    gilding_columns = CommentGilding.__table__.c.keys()
    awarding_columns = CommentAwarding.__table__.c.keys()

    #exists
    comments = Comment.query.filter_by(reddit_comment_id=praw_obj["reddit_comment_id"]).all()

    if len(comments) == 1:  
        comment = comments[0]
        latest_version = CommentVersion.query.filter_by(zen_comment_id=comment.zen_comment_id)\
                                        .order_by(CommentVersion.zen_comment_version_id.desc())\
                                            .first().zen_comment_version_id
        praw_obj['zen_comment_id'] = comment.zen_comment_id
        praw_obj['zen_comment_version_id'] = latest_version + 1
    elif len(comments) == 0:
        last_id = Comment.query.order_by(Comment.zen_comment_id.desc()).first().zen_comment_id
        praw_obj['zen_comment_id'] = last_id + 1
        praw_obj['zen_comment_version_id'] = 1
    elif len(comments) > 1:
        found_zen_ids = ', '.join(str(comment.zen_comment_id) for comment in comments)
        reddit_id = praw_obj["reddit_comment_id"]
        raise Exception(f"Multiple comments (Zen IDs: {found_zen_ids}) with same reddit comment id: {reddit_id}")

    if praw_obj.get('author'):
        accounts = Account.query.filter_by(reddit_account_id=praw_obj['reddit_account_id']).all()
        if len(accounts) == 0:
            last_account_id = Account.query.order_by(Account.zen_account_id.desc()).first().zen_account_id
            praw_obj['zen_account_id'] = last_account_id + 1
            resolve_create_account('','',json.dumps(praw_obj['author']))
        elif len(accounts) == 1:
            praw_obj['zen_account_id'] = accounts[0].zen_account_id
        elif len(accounts) > 1:
            raise Exception(f"Multiple accounts with same reddit author id: {praw_obj['reddit_account_id']}")

    last_detail_id = CommentDetail.query.order_by(CommentDetail.zen_comment_detail_id.desc()).first().zen_comment_detail_id
    praw_obj['zen_comment_detail_id'] = last_detail_id + 1

    posts = Post.query.filter_by(reddit_post_id=praw_obj['reddit_post_id']).all()
    if len(posts) == 0:
        last_post_id = Post.query.order_by(Post.zen_post_id.desc()).first().zen_post_id
        praw_obj['zen_post_id'] = last_post_id + 1
        resolve_create_post('','',json.dumps(praw_obj['post']))
    elif len(posts) == 1:
        praw_obj['zen_post_id'] = posts[0].zen_post_id
    elif len(posts) > 1:
        raise Exception(f"Multiple posts with same reddit post id: {praw_obj['reddit_post_id']}")

    subreddits = Subreddit.query.filter_by(reddit_subreddit_id=praw_obj['reddit_subreddit_id']).all()
    if len(subreddits) == 0:
        last_subreddit_id = Subreddit.query.order_by(Subreddit.zen_subreddit_id.desc()).first().zen_subreddit_id
        praw_obj['zen_subreddit_id'] = last_subreddit_id + 1
        resolve_create_subreddit('','',json.dumps(praw_obj['subreddit']))
    elif len(subreddits) == 1:
        praw_obj['zen_subreddit_id'] = subreddits[0].zen_subreddit_id
    elif len(subreddits) > 1:
        raise Exception(f"Multiple subreddits with same reddit subreddit id: {praw_obj['reddit_subreddit_id']}")
    

    praw_obj['zen_subreddit_id'] = Post.query.filter_by(reddit_post_id=praw_obj['reddit_post_id']).first().zen_post_id

    comment = {key: praw_obj[key] for key in comment_columns if key in praw_obj}
    version = {key: praw_obj[key] for key in version_columns if key in praw_obj}
    detail = {key: praw_obj[key] for key in detail_columns if key in praw_obj}

    comment = Comment(**comment)
    db.session.add(comment)
    version = CommentVersion(**version)
    db.session.add(version)
    detail = CommentDetail(**detail)
    db.session.add(detail)

    if 'all_awardings' in praw_obj:
        all_awardings = praw_obj.pop('all_awardings')
        for praw_awarding in all_awardings:
            awarding = {key: praw_awarding[key] for key in awarding_columns if key in praw_awarding}
            awarding['zen_comment_detail_id'] = praw_obj['zen_comment_detail_id']
            awarding = CommentAwarding(**awarding)
            db.session.add(awarding)
        
    if 'gildings' in praw_obj:
        gildings = praw_obj.pop('gildings')
        for praw_gilding in gildings:
            gilding = {key: praw_gilding[key] for key in gilding_columns if key in praw_gilding}
            gilding['zen_comment_detail_id'] = praw_obj['zen_comment_detail_id']
            gilding = CommentGilding(**gilding)
            db.session.add(gilding)

    try:
        db.session.commit()
        payload = {
            "success": True,
            "comment": comment.to_dict()
        }
    except ValueError:  # date format errors
        payload = {
            "success": False,
            "errors": ["Error creating comment"]
        }
        db.session.rollback() # does this do anything?
    return payload

# create post
@convert_kwargs_to_snake_case
def resolve_create_post(obj, info, from_json):

    praw_obj = json.loads(from_json)

    post_columns = Post.__table__.c.keys()
    version_columns = PostVersion.__table__.c.keys()
    detail_columns = PostDetail.__table__.c.keys()
    awarding_columns = PostAwarding.__table__.c.keys()
    gilding_columns = PostGilding.__table__.c.keys()
    media_columns = PostMedia.__table__.c.keys()
    media_embed_columns = PostMediaEmbed.__table__.c.keys()
    secure_media_columns = PostSecureMedia.__table__.c.keys()

    #exists
    posts = Post.query.filter_by(reddit_post_id=praw_obj["reddit_post_id"]).all()
    if len(posts) == 1:  
        post = posts[0]
        latest_version = PostVersion.query.filter_by(zen_post_id=post.zen_post_id)\
                                        .order_by(PostVersion.zen_post_version_id.desc())\
                                            .first().zen_post_version_id
        praw_obj['zen_post_id'] = post.zen_post_id
        praw_obj['zen_post_version_id'] = latest_version + 1
    elif len(posts) == 0:
        last_id = Post.query.order_by(Post.zen_post_id.desc()).first().zen_post_id
        praw_obj['zen_post_id'] = last_id + 1
        praw_obj['zen_post_version_id'] = 1
    elif len(posts) > 1:
        found_zen_ids = ', '.join(str(post.zen_post_id) for post in posts)
        reddit_id = praw_obj["reddit_post_id"]
        raise Exception(f"Multiple posts (Zen IDs: {found_zen_ids}) with same reddit post id: {reddit_id}")


    if praw_obj.get('author'):
        accounts = Account.query.filter_by(reddit_account_id=praw_obj['reddit_account_id']).all()
        if len(accounts) == 0:
            account_payload = resolve_create_account('','',json.dumps(praw_obj['author']))
            praw_obj['zen_account_id'] = account_payload['account']['zen_account_id']
        elif len(accounts) == 1:
            praw_obj['zen_account_id'] = accounts[0].zen_account_id
        elif len(accounts) > 1:
            raise Exception(f"Multiple accounts with same reddit author id: {praw_obj['reddit_account_id']}")

    last_detail_id = PostDetail.query.order_by(PostDetail.zen_post_detail_id.desc()).first().zen_post_detail_id
    praw_obj['zen_post_detail_id'] = last_detail_id + 1

    subreddits = Subreddit.query.filter_by(reddit_subreddit_id=praw_obj['reddit_subreddit_id']).all()
    if len(subreddits) == 0:
        subreddit_payload = resolve_create_subreddit('','',json.dumps(praw_obj['subreddit']))
        praw_obj['zen_subreddit_id'] = subreddit_payload['subreddit']['zen_subreddit_id']
    elif len(subreddits) == 1:
        praw_obj['zen_subreddit_id'] = subreddits[0].zen_subreddit_id
    elif len(subreddits) > 1:
        raise Exception(f"Multiple subreddits with same reddit subreddit id: {praw_obj['reddit_subreddit_id']}")


    post = {key: praw_obj[key] for key in post_columns if key in praw_obj}
    version = {key: praw_obj[key] for key in version_columns if key in praw_obj}
    detail = {key: praw_obj[key] for key in detail_columns if key in praw_obj}

    post = Post(**post)
    db.session.add(post)
    version = PostVersion(**version)
    db.session.add(version)
    detail = PostDetail(**detail)
    db.session.add(detail)

    if 'all_awardings' in praw_obj:
        all_awardings = praw_obj.pop('all_awardings')
        for praw_awarding in all_awardings:
            awarding = {key: praw_awarding[key] for key in awarding_columns if key in praw_awarding}
            awarding['zen_post_detail_id'] = praw_obj['zen_post_detail_id']
            awarding = PostAwarding(**awarding)
            db.session.add(awarding)

    if 'gildings' in praw_obj:
        gildings = praw_obj.pop('gildings')
        for praw_gilding in gildings:
            gilding = {key: praw_gilding[key] for key in gilding_columns if key in praw_gilding}
            gilding['zen_post_detail_id'] = praw_obj['zen_post_detail_id']
            gilding = PostGilding(**gilding)
            db.session.add(gilding)

    if 'media' in praw_obj:
        media = praw_obj.pop('media')
        media_type = media.keys()[0]
        media = media[media_type]
        media['media_type'] = media_type
        media = {key: media[key] for key in media_columns if key in media}
        media['zen_post_detail_id'] = praw_obj['zen_post_detail_id']
        media = PostMedia(**media)
        db.session.add(media)

    if 'media_embed' in praw_obj:
        media_embed = praw_obj.pop('media_embed')
        media_type = media_embed.keys()[0]
        media_embed = media_embed[media_type]
        media_embed['media_type'] = media_type
        media_embed = {key: media_embed[key] for key in media_embed_columns if key in media_embed}
        media_embed['zen_post_detail_id'] = praw_obj['zen_post_detail_id']
        media_embed = PostMediaEmbed(**media_embed)
        db.session.add(media_embed)

    if 'secure_media' in praw_obj:
        secure_media = praw_obj.pop('secure_media')
        media_type = secure_media.keys()[0]
        secure_media = secure_media[media_type]
        secure_media['media_type'] = media_type
        secure_media = {key: secure_media[key] for key in secure_media_columns if key in secure_media}
        secure_media['zen_post_detail_id'] = praw_obj['zen_post_detail_id']
        secure_media = PostSecureMedia(**secure_media)
        db.session.add(secure_media)

    try:
        db.session.commit()
        payload = {
            "success": True,
            "post": post.to_dict()
        }
    except: 
        db.session.rollback() # does this do anything?
        payload = {
            "success": False,
            "errors": ["Error creating post"]
        }
    return payload


# create account
@convert_kwargs_to_snake_case
def resolve_create_account(obj, info, from_json):
    
    praw_obj = json.loads(from_json)

    account_columns = Account.__table__.c.keys()
    version_columns = AccountVersion.__table__.c.keys()
    detail_columns = AccountDetail.__table__.c.keys()

    #exists
    accounts = Account.query.filter_by(reddit_account_id=praw_obj["reddit_account_id"]).all()
    if len(accounts) == 1:  
        account = accounts[0]
        latest_version = AccountVersion.query.filter_by(zen_account_id=account.zen_account_id)\
                                        .order_by(AccountVersion.zen_account_version_id.desc())\
                                            .first().zen_account_version_id
        praw_obj['zen_account_id'] = account.zen_account_id
        praw_obj['zen_account_version_id'] = latest_version + 1
    elif len(accounts) == 0:
        last_id = Account.query.order_by(Account.zen_account_id.desc()).first().zen_account_id
        praw_obj['zen_account_id'] = last_id + 1
        praw_obj['zen_account_version_id'] = 1
    elif len(accounts) > 1:
        found_zen_ids = ', '.join(str(account.zen_account_id) for account in accounts)
        reddit_id = praw_obj["reddit_account_id"]
        raise Exception(f"Multiple accounts (Zen IDs: {found_zen_ids}) with same reddit account id: {reddit_id}")



    account = {key: praw_obj[key] for key in account_columns if key in praw_obj}
    version = {key: praw_obj[key] for key in version_columns if key in praw_obj}
    detail = {key: praw_obj[key] for key in detail_columns if key in praw_obj}

    account = Account(**account)
    db.session.add(account)
    version = AccountVersion(**version)
    db.session.add(version)
    detail = AccountDetail(**detail)
    db.session.add(detail)

    try:
        db.session.commit()
        payload = {
            "success": True,
            "account": account.to_dict()
        }
    except: 
        db.session.rollback() # does this do anything?
        payload = {
            "success": False,
            "errors": ["Error creating account"]
        }
    return payload


def set_zen_ids(kind, obj_dict_to_update):
    reddit_id = obj_dict_to_update[f'reddit_{kind}_id']
    model = lookup_dict[kind]["main"]
    detail = lookup_dict[kind]["detail"]
    version = lookup_dict[kind]["version"]
    # TODO: confirm that this works
    results = model.query.filter_by(reddit_unique_id=reddit_id).all()

    # case 1: too many results
    if len(results) > 1:
        zen_ids = ', '.join(r.zen_unique_id for r in results)
        raise ValueError(f"Multiple zen ids {zen_ids} for same reddit id: {reddit_id}")
    
    # detail_id
    last_detail = detail.query.order_by(detail.zen_unique_id.desc()).first()
    if last_detail:
        obj_dict_to_update[f'zen_{kind}_detail_id'] = last_detail.zen_detail_id + 1
    else:
        obj_dict_to_update[f'zen_{kind}_detail_id'] = 1

    # case 2: no results
    if len(results) == 0:

        # main_id
        last_main = model.query.order_by(model.zen_unique_id.desc()).first()
        if last_obj:
            obj_dict_to_update[f'zen_{kind}_id'] = last_obj.zen_unique_id + 1
        else:
            obj_dict_to_update[f'zen_{kind}_id'] = 1

        # version_id
        obj_dict_to_update[f'zen_{kind}_version_id'] = 1

    # case 3: one result
    elif len(results) == 1:
        existing_obj = results[0]

        # main_id
        obj_dict_to_update[f'zen_{kind}_id'] = existing_obj.zen_unique_id

        # version_id
        last_version = version.query.filter_by(zen_unique_id=existing_obj.zen_unique_id).order_by(version.zen_unique_id.desc()).first().zen_version_id
        obj_dict_to_update[f'zen_{kind}_version_id'] = last_version + 1
