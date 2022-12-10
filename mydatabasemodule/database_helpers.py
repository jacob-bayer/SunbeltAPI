# -*- coding: utf-8 -*-

import pandas as pd
from os import environ
from sqlalchemy import create_engine

def get_next_id(object_name):
    idname = object_name[:-1] + '_id'
    last_id = pd.read_sql(
            f"""
            SELECT MAX({idname}) FROM {object_name}.{object_name};
            """, 
             environ['MAIN_MEDIA_DATABASE']).iloc[0,0]
    return last_id + 1 if last_id else 1

def get_existing_or_next_id(object_id, object_name):
    if not object_id.startswith('t'):
        raise Exception("Object id must start with t. \n Try using 'fullname' attribute.")
    idname = object_name[:-1] + '_id'
    matching_id = pd.read_sql(f"""
        SELECT {idname} FROM {object_name}.{object_name}
        WHERE reddit_{idname} = '{object_id}';
        """,
        environ['MAIN_MEDIA_DATABASE'])
    if len(matching_id):
        return matching_id.iloc[0,0]
    else:
        return get_next_id(object_name)
    
    
def get_target_columns(schema, table):
    return pd.read_sql(
            f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = '{schema}'
            AND table_name = '{table}';
            """, 
             environ['MAIN_MEDIA_DATABASE']).squeeze().to_list()

def regen_schema(schema_name):
    with open(f'./ddl/{schema_name}.sql') as file:
        sql = file.read()
    print(f'Regenerating {schema_name} schema')
    engine = create_engine(environ['MAIN_MEDIA_DATABASE'])
    with engine.connect() as conn:
        conn.execute(sql)
