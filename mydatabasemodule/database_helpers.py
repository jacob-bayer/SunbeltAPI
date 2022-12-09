# -*- coding: utf-8 -*-

import pandas as pd
from os import environ
from sqlalchemy import create_engine

def get_next_id(schema_name):
    idname = schema_name[:-1] + '_id'
    last_id = pd.read_sql(
            f"""
            SELECT MAX({idname}) FROM {schema_name}.{schema_name};
            """, 
             environ['MAIN_MEDIA_DATABASE']).iloc[0,0]
    return last_id + 1 if last_id else 1

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
