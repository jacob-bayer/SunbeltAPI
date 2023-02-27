# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from datetime import timedelta

from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, 
                                get_jwt_identity, jwt_required)


from ariadne import QueryType

app = Flask(__name__)

# FLASK_ENV variable is depreciated and FLASK_DEBUG is used instead.
# Debug = True means development mode.

if app.debug:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('LOCAL_SUNBELT_DB_URL') #'sqlite:///app.db'
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['HEROKU_SUNBELT_DB_URL']


app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)

app.config['SQLALCHEMY_POOL_SIZE'] = 100
db = SQLAlchemy(app)

migrate = Migrate(app, db)
#celery_app = celery_init_app(app)

query = QueryType()

@app.route('/')
def hello():
    return 'Hello!'

@app.route('/auth', methods=['POST'])
def auth():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'admin' or password != os.environ['ADMIN_PASSWORD']:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    refresh_token = request.json.get('refresh_token', None)
    if not refresh_token:
        return jsonify({"msg": "Missing refresh token"}), 401
    try:
        identity = get_jwt_identity()
    except:
        return jsonify({"msg": "Invalid refresh token"}), 401
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=username)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


    
