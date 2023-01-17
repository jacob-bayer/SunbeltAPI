from sunbelt.model_lookup import lookup_dict
from ariadne import convert_kwargs_to_snake_case
import json
from sunbelt import db
from datetime import datetime, timedelta
import pytz

et = pytz.timezone('US/Eastern')

def create_object(kind, from_dict):

    # Returns bool indicating whether a new version of the object should be created
    def set_zen_ids(kind, obj_dict_to_update):
        should_write = True

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
        last_detail = detail.query.order_by(detail.zen_detail_id.desc()).first()
        if last_detail:
            obj_dict_to_update[f'zen_{kind}_detail_id'] = last_detail.zen_detail_id + 1
        else:
            obj_dict_to_update[f'zen_{kind}_detail_id'] = 1

        # case 2: no results
        if len(results) == 0:

            # main_id
            last_main = model.query.order_by(model.zen_unique_id.desc()).first()
            if last_main:
                obj_dict_to_update[f'zen_{kind}_id'] = last_main.zen_unique_id + 1
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
            last_version = version.query.filter_by(zen_unique_id=existing_obj.zen_unique_id)\
                                .order_by(version.zen_version_id.desc()).first()

            last_version_id = last_version.zen_version_id

            obj_dict_to_update[f'zen_{kind}_version_id'] = last_version_id + 1

            mins_ago = datetime.now() - timedelta(minutes = 15)
            should_write = last_version.zen_created_at < mins_ago

        return should_write


    # The zen ids for higher level objects must be added to the dictionary first
    if kind in ['post','comment']:
        if kind == 'post':
            subreddit = from_dict['subreddit']
            create_object('subreddit', subreddit)
            from_dict['zen_subreddit_id'] = subreddit['zen_subreddit_id']

        if 'author' in from_dict:
            author = from_dict['author']
            create_object('account', author)
            from_dict['zen_account_id'] = author['zen_account_id']

        if kind == 'comment':
            post = from_dict['post']
            create_object('post', post)
            from_dict['zen_post_id'] = post['zen_post_id']
            from_dict['zen_subreddit_id'] = post['zen_subreddit_id']
    
    
    models = lookup_dict[kind]

    should_write = set_zen_ids(kind, from_dict)
    if should_write:


        v1 = from_dict[f'zen_{kind}_version_id'] == 1

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
        final_result = models['main'].query.get(from_dict[f'zen_{kind}_id'])
        payload = {'success': True,
                    kind : final_result.to_dict()}
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
