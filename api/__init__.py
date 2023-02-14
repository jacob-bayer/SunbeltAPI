# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from ariadne import QueryType

app = Flask(__name__)

# FLASK_ENV variable is depreciated and FLASK_DEBUG is used instead.
# Debug = True means development mode.

if app.debug:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['LOCAL_SUNBELT_DB_URL'] #'sqlite:///app.db'
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['HEROKU_SUNBELT_DB_URL']


db = SQLAlchemy(app)
migrate = Migrate(app, db)

query = QueryType()

@app.route('/')
def hello():
    return 'Hello!'

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
    
