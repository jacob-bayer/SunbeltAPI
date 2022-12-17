# -*- coding: utf-8 -*-


import pandas as pd
from os import environ
from sqlalchemy import create_engine
import logging

log = logging.getLogger(" DB-HELPER")
engine = create_engine(environ['MAIN_MEDIA_DATABASE'])


def get_next_id(object_name):
    object_name = object_name[:-1] if object_name[-1] == 's' else object_name
    QUERY = f"SELECT MAX(zen_{object_name}_id) FROM most_recent_{object_name}_details;"
    log.debug(" QUERY:" + QUERY)
    last_id = pd.read_sql(QUERY, engine).iloc[0,0]
    return last_id + 1 if last_id else 1

def get_id_params(object_id, object_name,
                            existing_id_collection = None):

    if not object_id.startswith('t'):
        raise Exception("Object id must start with t. \n Try using 'fullname' attribute.")
    object_name = object_name[:-1] if object_name[-1] == 's' else object_name
    main_id = f'zen_{object_name}_id'
    version_detail_ids = [f'zen_{object_name}_version_id',
                          f'zen_{object_name}_detail_id']
    object_ids = [main_id] + version_detail_ids
    obj_id_fields = ', '.join(object_ids)
    try:
        QUERY = f"""
            SELECT {obj_id_fields}
            FROM most_recent_{object_name}_details
            WHERE reddit_lookup_id = '{object_id}';
            """
        log.debug(" QUERY:" + QUERY)
        matching_ids = pd.read_sql(QUERY,engine)
    except:
        SCHEMA_QUERY = """
        SELECT DISTINCT table_schema
        FROM information_schema.tables
        WHERE table_schema NOT IN ('public','pg_catalog','information_schema')
        """
        valid_schemas = pd.read_sql(SCHEMA_QUERY,engine)
        valid_schemas = ' \n '.join(valid_schemas.table_schema)
        ERROR_MESSAGE = f"""
        Object name '{object_name}' invalid. Must be one of:\n
        {valid_schemas}
            """
        raise Exception(ERROR_MESSAGE)
    
    if len(matching_ids):
        matching_ids[version_detail_ids] += 1
        return matching_ids.T.to_dict()
         
    elif existing_id_collection:
        existing_ids = {x: existing_id_collection[-1][x] for x in object_ids}
        existing_ids[main_id] += 1
        
        """
        if isinstance(existing_id_collection, list):
            existing_ids = existing_id_collection
        elif isinstance(existing_id_collection, dict):
            existing_ids = list(existing_id_collection.keys())
        else:
            raise TypeError("Existing ID collection must be dict or list")
        if all(isinstance(key, int) for key in existing_ids):
            return max(existing_ids) + 1
        else:
            raise TypeError("All keys of existing id collection must be ints")
        """
        
    else:
        new_ids = {x:1 for x in object_ids}
        new_ids[main_id] = get_next_id(object_name)
        return new_ids


def get_target_columns(schema, table):
    return pd.read_sql(
            f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = '{schema}'
            AND table_name = '{table}';
            """,
            engine).squeeze().to_list()


def regen_schema(schema_name):
    with open(f'./ddl/{schema_name}.sql') as file:
        sql = file.read()
    print(f'Regenerating {schema_name} schema')
    with engine.connect() as conn:
        conn.execute(sql)
