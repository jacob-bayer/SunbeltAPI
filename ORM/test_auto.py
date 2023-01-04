#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:02:57 2023

@author: jacob
"""

from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.ext.automap import automap_base
from os import environ
from sqlalchemy import inspect

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine(environ['MAIN_MEDIA_DATABASE'])
# produce our own MetaData object
metadata = MetaData()

# we can reflect it ourselves from a database, using options
# such as 'only' to limit what tables we look at...

metadata.reflect(engine, schema = 'posts')

Base = automap_base(metadata=metadata)
Base.prepare(autoload_with=engine)

post_details = Base.classes.post_details



i = inspect(post_details)

i.relationships
