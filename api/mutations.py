from .model_lookup import lookup_dict
from .models import *
from ariadne import convert_kwargs_to_snake_case
import json
from main import db
from datetime import datetime, timedelta
import pytz

def create_object(kind, from_dict):
    # Returns bool indicating whether a new version of the object should be created

    def set_sun_ids(kind, obj_dict_to_update):
        should_write = True


        reddit_id = obj_dict_to_update[f'reddit_{kind}_id']
        model = lookup_dict[kind]["main"]
        detail = lookup_dict[kind]["detail"]
        version = lookup_dict[kind]["version"]
        # TODO: confirm that this works
        results = model.query.filter_by(reddit_unique_id=reddit_id).all()
        
        # case 1: too many results
        if len(results) > 1:
            sun_ids = ', '.join(r.sun_unique_id for r in results)
            raise ValueError(f"Multiple Sun ids {sun_ids} for same reddit id: {reddit_id}")
        
        # detail_id
        last_detail = detail.query.order_by(detail.sun_detail_id.desc()).first()
        if last_detail:
            obj_dict_to_update[f'sun_{kind}_detail_id'] = last_detail.sun_detail_id + 1
        else:
            obj_dict_to_update[f'sun_{kind}_detail_id'] = 1

        # case 2: no results
        if len(results) == 0:

            # main_id
            last_main = model.query.order_by(model.sun_unique_id.desc()).first()
            if last_main:
                obj_dict_to_update[f'sun_{kind}_id'] = last_main.sun_unique_id + 1
            else:
                obj_dict_to_update[f'sun_{kind}_id'] = 1

            # version_id
            obj_dict_to_update[f'sun_{kind}_version_id'] = 1

        # case 3: one result
        elif len(results) == 1:
            existing_obj = results[0]

            # main_id
            obj_dict_to_update[f'sun_{kind}_id'] = existing_obj.sun_unique_id

            # version_id
            last_version = version.query.filter_by(sun_unique_id=existing_obj.sun_unique_id)\
                                .order_by(version.sun_version_id.desc()).first()

            last_version_id = last_version.sun_version_id

            obj_dict_to_update[f'sun_{kind}_version_id'] = last_version_id + 1

            mins_ago = datetime.utcnow() - timedelta(minutes = 15)
            should_write = last_version.sun_created_at < mins_ago


        return should_write


    # The Sun ids for higher level objects must be added to the dictionary first
    if kind in ['post','comment']:
        if kind == 'post':
            from_dict['removed'] = from_dict['selftext'] == '[removed]'
            from_dict['deleted'] = from_dict['selftext'] == '[deleted]'
            
            subreddit = from_dict.get('subreddit')
            if subreddit:
                create_object('subreddit', subreddit)
                from_dict['sun_subreddit_id'] = subreddit['sun_subreddit_id']

            elif from_dict.get('reddit_subreddit_id'):
                subreddit = Subreddit.query.filter_by(reddit_subreddit_id = from_dict['reddit_subreddit_id']).first()
                if subreddit:
                    from_dict['sun_subreddit_id'] = subreddit.sun_subreddit_id

        author = from_dict.get('author')
        if author:
            if not isinstance(author, dict):
                author = {'reddit_account_id': from_dict['reddit_account_id'],
                          'name': from_dict['author']}
            create_object('account', author)
            from_dict['sun_account_id'] = author['sun_account_id']
        elif from_dict.get('reddit_account_id'):
            account = Account.query.filter_by(reddit_account_id = from_dict['reddit_account_id']).first()
            if account:
                from_dict['sun_account_id'] = account.sun_account_id


        if kind == 'comment':
            from_dict['removed'] = from_dict['body'] == '[removed]'
            from_dict['deleted'] = from_dict['body'] == '[deleted]'

            # It shouldn't have the post in most cases
            post = from_dict.get('post')
            if post:
                create_object('post', post)
                from_dict['sun_post_id'] = post['sun_post_id']
                from_dict['sun_subreddit_id'] = post['sun_subreddit_id']
            elif from_dict.get('reddit_post_id'):
                post = Post.query.filter_by(reddit_post_id = from_dict['reddit_post_id']).first()
                if post:
                    from_dict['sun_post_id'] = post.sun_post_id
                    from_dict['sun_subreddit_id'] = post.sun_subreddit_id
    
    
    models = lookup_dict[kind]

    should_write = set_sun_ids(kind, from_dict)

    if should_write:


        v1 = from_dict[f'sun_{kind}_version_id'] == 1

        def add_to_db(from_dict, model):
            columns_to_keep = model.__table__.c.keys()
            values = {k: v for k, v in from_dict.items() if k in columns_to_keep}
            db_obj = model(**values)
            db.session.add(db_obj)

        for table, model in models.items():
            if not v1 and table == 'main':
                continue
            add_to_db(from_dict, model)

        
    try:
        db.session.commit()

        final_result = models['main'].query.get(from_dict[f'sun_{kind}_id'])
        payload = {'success': True,
                    kind : final_result.to_dict(),
                    'created_new_version': should_write}
    except Exception as e:
        db.session.rollback()
        raise e
        payload = {'success': False,
                   'error': e}

    return payload

@convert_kwargs_to_snake_case
def resolve_create_comment(obj, info, from_json):
    from_dict = json.loads(from_json)
    return create_object("comment", from_dict)

@convert_kwargs_to_snake_case
def resolve_create_post(obj, info, from_json):
    from_dict = json.loads(from_json)
    return create_object("post", from_dict)

@convert_kwargs_to_snake_case
def resolve_create_account(obj, info, from_json):
    from_dict = json.loads(from_json)
    return create_object("account", from_dict)

@convert_kwargs_to_snake_case
def resolve_create_subreddit(obj, info, from_json):
    from_dict = json.loads(from_json)
    return create_object("subreddit", from_dict)
