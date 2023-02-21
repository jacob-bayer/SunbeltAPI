from model_lookup import lookup_dict
from models import *
import json
from sqlalchemy.exc import IntegrityError

def create_objects(kind, dict_of_dicts):

    # Returns bool indicating whether a new version of the object should be created
    
    models = lookup_dict[kind]
    model = models["main"]
    version = models["version"]
    
    def set_obj_ids(dict_of_dicts):

        reddit_ids = list(dict_of_dicts.keys())

        last_ids = db.session.query(db.func.max(version.sun_unique_id).label('sun_unique_id'),
                                    db.func.max(version.sun_detail_id).label('sun_detail_id'),
                                    ).one()

        last_ids = {col : last_ids[col] or 1 for col in last_ids.keys()}


        subquery = db.session.query(
                            version.sun_unique_id.label('sun_unique_id'), 
                            db.func.max(version.sun_version_id).label('max_version_id'))\
                            .group_by(version.sun_unique_id).subquery()

        mr_query = model.query.join(version)\
                        .join(subquery, db.and_(version.sun_unique_id == subquery.c.sun_unique_id, 
                                                version.sun_version_id == subquery.c.max_version_id))\
                        .filter(model.reddit_unique_id.in_(reddit_ids))\
                        .with_entities(model.reddit_unique_id.label('reddit_unique_id'), 
                                    model.sun_unique_id.label('sun_unique_id'), 
                                    version.sun_version_id.label('most_recent_version_id'),
                                    version.sun_created_at.label('most_recent_version_updated_at'))

        mr_dict = {}
        for row in mr_query:
            mr_dict[row.reddit_unique_id] = {col: row[col] for col in row.keys()}

        final_result_ids = []
        for reddit_unique_id, obj_to_write in dict_of_dicts.items():

            mrv = mr_dict.get(reddit_unique_id)
            if mrv:
                ids_dict = {f'sun_{kind}_id' : mrv['sun_unique_id'],
                            f'sun_{kind}_version_id' : mrv['most_recent_version_id'] + 1,
                            f'sun_{kind}_detail_id' : last_ids['sun_detail_id'] + 1}
                last_ids['sun_detail_id'] += 1
  
            else:
                ids_dict = {f'sun_{kind}_id' : last_ids['sun_unique_id'] + 1,
                            f'sun_{kind}_version_id' : 1,
                            f'sun_{kind}_detail_id' : last_ids['sun_detail_id'] + 1}
                last_ids = {col : last_ids[col] + 1 for col in last_ids.keys()}

            obj_to_write.update(ids_dict)
            final_result_ids += [ids_dict]
        return final_result_ids

    obj_ids = set_obj_ids(dict_of_dicts)

    # Return the ids of the objects that will be written
    # This is returned from the mutation
    return_confirm_result = []
    for id_set in obj_ids:
        return_confirm_result.append(
            {'kind' : kind,
            'sun_unique_id' : id_set[f'sun_{kind}_id'],
            'most_recent_version_id' : id_set[f'sun_{kind}_version_id'],
            'most_recent_detail_id' : id_set[f'sun_{kind}_detail_id']}
        )

    def generate_sqla_obj(data, model, columns):
        data = {k: v for k, v in data.items() if k in columns}
        return model(**data)

    # Detail and version should be added if not v1, else add all including main
    model_columns = {model_name: model.__table__.c.keys() 
                    for model_name, model in models.items()}

    sqla_objs_to_write = []
    for item in dict_of_dicts.values():
        v1 = item[f'sun_{kind}_version_id'] == 1
        if v1:
            sqla_objs_to_write += [generate_sqla_obj(item, models['main'], model_columns['main'])]
        sqla_objs_to_write += [generate_sqla_obj(item, models['version'], model_columns['version'])]
        sqla_objs_to_write += [generate_sqla_obj(item, models['detail'], model_columns['detail'])]

        # for sqla_obj in sqla_objs_to_write:
        #     try:
        #         db.session.add(sqla_obj)
        #         db.session.commit()
        #     except:
        #         db.session.rollback()
        #         print(sqla_obj.reddit_unique_id)
        #         raise Exception('Error writing to database')

        db.session.add_all(sqla_objs_to_write)

    try:
        db.session.commit()
        payload = {'success': True,
                    'objs_created' : return_confirm_result}

    except IntegrityError as e:
        db.session.rollback()
        payload = {'success': False,
                   'error': 'IntegrityError. Your dev database is out of sync.'}
        raise e

    except Exception as e:
        db.session.rollback()
        payload = {'success': False,
                   'error': e}
        raise e

    return payload


def batch_create_from_json(from_json):
    from_dict = json.loads(from_json)

    objs_created = []
    kinds = ['post', 'comment', 'account', 'subreddit']
    for kind in kinds:
        data = {x[f'reddit_{kind}_id']: x for x in from_dict if x['kind'] == kind}
        result = create_objects(kind, data)
        if result['success']:
            objs_created += result['objs_created']
        elif result['error']:
            return {'success': False, 'error': result['error']}

    return {'success': True, 'objs_created': objs_created}