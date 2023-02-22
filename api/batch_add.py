from .model_lookup import lookup_dict
from .models import *
import json
from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta
import secrets
import os

def datetime_now_if_true(some_bool):
    return datetime.now() if some_bool else None

def write_statistics_to_file(checkpoints, length_of_data, kind):
    # Checkpoints is a dictionary of the form {checkpoint_name : datetime}
    
    checkpoint_enumerated_keys_dict = {i : key for i, key in enumerate(checkpoints.keys())}
    # Convert checkpoints to the form {checkpoint_name : time_since_last_checkpoint}
    results = {}
    results['checkpoints'] = {}
    for i, key in enumerate(checkpoints.keys()):
        if not i == 0:
            previous_key = checkpoint_enumerated_keys_dict[i - 1]
            difference = checkpoints[key] - checkpoints[previous_key]
        else:
            difference = timedelta(0)

        start_time = checkpoints[key].strftime('%H:%M:%S')
        difference = difference.total_seconds()
        results['checkpoints'][i+1] = {'checkpoint' : key, 'checkpoint_at' : start_time, 'seconds_since_last_checkpoint' : difference}

    results['length_of_data'] = length_of_data
    results['kind'] = kind
    results['total_time'] = (checkpoints['committed'] - checkpoints['started_set_obj_dicts']).total_seconds()
    
    today = datetime.now().strftime('%Y_%m_%d')
    filepath = f'../analysis/system_statistics/api_write_stats_{today}.json'
    
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            f.write('[{}]')

    with open(filepath, mode="r+") as file:
        file.seek(0,2)
        position = file.tell() -1
        file.seek(position)
        file.write( ",{}]".format(json.dumps({'job': secrets.token_hex(4), 'results' : results})) )


def create_objects(kind, dict_of_dicts):

    checkpoints = {}

    write_statistics = False

    # Returns bool indicating whether a new version of the object should be created
    
    models = lookup_dict[kind]
    model = models["main"]
    version = models["version"]
    
    def set_obj_ids(dict_of_dicts):

        reddit_ids = list(dict_of_dicts.keys())

        checkpoints['started_set_obj_dicts'] = datetime_now_if_true(write_statistics)
        last_ids = db.session.query(db.func.max(version.sun_unique_id).label('sun_unique_id'),
                                    db.func.max(version.sun_detail_id).label('sun_detail_id'),
                                    ).one()

        last_ids = {col : last_ids[col] or 1 for col in last_ids.keys()}

        checkpoints['last_ids_complete'] = datetime_now_if_true(write_statistics)
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

        checkpoints['mr_query_complete'] = datetime_now_if_true(write_statistics)
        mr_dict = {}
        for row in mr_query:
            mr_dict[row.reddit_unique_id] = {col: row[col] for col in row.keys()}

        checkpoints['mr_dict_created'] = datetime_now_if_true(write_statistics)
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
    checkpoints['set_ids_completed'] = datetime_now_if_true(write_statistics)

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

    checkpoints['return_id_dict_created'] = datetime_now_if_true(write_statistics)

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

    checkpoints['db_objs_created'] = datetime_now_if_true(write_statistics)
    db.session.add_all(sqla_objs_to_write)

    checkpoints['db_objs_added_to_session'] = datetime_now_if_true(write_statistics)

    try:
        db.session.commit()
        payload = {'success': True,
                    'objs_created' : return_confirm_result}

    except IntegrityError as e:
        db.session.rollback()
        payload = {'success': False,
                   'error': '''IntegrityError. Likely concurrent write attempts 
                   or dev data that is out of sync with the database.
                   
                   Error: {}'''.format(e)
                     }
        raise e

    except Exception as e:
        db.session.rollback()
        payload = {'success': False,
                   'error': e}
        raise e

    checkpoints['committed'] = datetime_now_if_true(write_statistics)
    if write_statistics:
        write_statistics_to_file(checkpoints, len(dict_of_dicts), kind)
        
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