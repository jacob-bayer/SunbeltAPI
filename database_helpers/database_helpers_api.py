# -*- coding: utf-8 -*-


import pandas as pd
from os import environ
from sqlalchemy import create_engine
import logging

log = logging.getLogger("ZEN-HELPER")
engine = create_engine(environ['MAIN_MEDIA_DATABASE'])


def most_recent_details(schema):
    QUERY = f"SELECT * FROM {schema}.most_recent_details;"
    log.debug(" QUERY:" + QUERY)
    return pd.read_sql(QUERY, engine)

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
