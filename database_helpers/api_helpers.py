# -*- coding: utf-8 -*-


import pandas as pd
import logging

log = logging.getLogger("ZEN-HELPER")


def get_next_id(schema_name, table_name):
    object_name = table_name[:-1] if table_name[-1] == 's' else table_name
    QUERY = f"SELECT MAX(zen_{object_name}_id) FROM {schema_name}.{table_name};"
    log.debug(" QUERY:" + QUERY)
    last_id = pd.read_sql(QUERY, engine).iloc[0,0]
    return last_id + 1 if last_id else 1

def get_id_params(object_id, object_name,
                            existing_id_collection = None):
    
    if isinstance(existing_id_collection, dict):
        existing_id_collection = list(existing_id_collection.values())

    if not object_id.startswith('t'):
        raise Exception("Object id must start with t. \n Try using 'fullname' attribute.")
    object_name = object_name[:-1] if object_name[-1] == 's' else object_name
    main_id = f'zen_{object_name}_id'
    version_id = f'zen_{object_name}_version_id'
    object_ids = [main_id, version_id]
    obj_id_fields = []
    for field in object_ids:
        obj_id_fields.append(f'COALESCE({field},0) AS {field}')
    obj_id_fields = ', '.join(obj_id_fields)
    try:
        QUERY = f"""
            SELECT {obj_id_fields}
            FROM {object_name}s.most_recent_details
            WHERE reddit_lookup_id = '{object_id}';
            """
        log.debug(" QUERY:" + QUERY)
        matching_ids = pd.read_sql(QUERY,engine).T.to_dict()
        found_matches = bool(matching_ids)
        if found_matches:
            matching_ids = matching_ids[0]
    except:
        SCHEMA_QUERY = """
        SELECT DISTINCT table_schema
        FROM information_schema.tables
        WHERE table_schema NOT IN ('public','pg_catalog','information_schema')
        """
        log.debug(" QUERY:" + SCHEMA_QUERY)
        valid_schemas = pd.read_sql(SCHEMA_QUERY,engine)
        valid_schemas = ' \n '.join(valid_schemas.table_schema)
        ERROR_MESSAGE = f"""
        Object name '{object_name}' invalid. Must be one of:\n
        {valid_schemas}
            """
        raise Exception(ERROR_MESSAGE)
    
    detail_id = f'zen_{object_name}_detail_id'
    
    new_ids = matching_ids.copy()
    
    if existing_id_collection:
        new_ids[detail_id] = max(x[detail_id] for x in existing_id_collection) + 1
    else:
        new_ids[detail_id] = get_next_id(object_name+'s', object_name+'_details')
        
    if found_matches:
        new_ids[version_id] += 1
    else:
        new_ids[version_id] = 1
    
    if existing_id_collection and not found_matches:
        new_ids[main_id] = max(x[main_id] for x in existing_id_collection) + 1
    elif not found_matches:
        new_ids[main_id] = get_next_id(object_name+'s', object_name+'s')
    
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
    log.info(f' Regenerating {schema_name} schema')
    with engine.connect() as conn:
        conn.execute(sql)
