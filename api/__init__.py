# -*- coding: utf-8 -*-

import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


#from celery import Celery, Task

from flask_jwt_extended import JWTManager, create_access_token


from ariadne import QueryType

app = Flask(__name__)

# FLASK_ENV variable is depreciated and FLASK_DEBUG is used instead.
# Debug = True means development mode.

if app.debug:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['LOCAL_SUNBELT_DB_URL'] #'sqlite:///app.db'
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['HEROKU_SUNBELT_DB_URL']


# def celery_init_app(app: Flask) -> Celery:
#     class FlaskTask(Task):
#         def __call__(self, *args: object, **kwargs: object) -> object:
#             with app.app_context():
#                 return self.run(*args, **kwargs)

#     celery_app = Celery(app.name, task_cls=FlaskTask)
#     celery_app.config_from_object(app.config["CELERY"])
#     celery_app.set_default()
#     app.extensions["celery"] = celery_app
#     return celery_app

# app.config.from_mapping(
#     CELERY=dict(
#         broker_url="redis://localhost",
#         result_backend="redis://localhost",
#         task_ignore_result=True,
#     ),
# )

app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
jwt = JWTManager(app)

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
    return jsonify(access_token=access_token), 200



@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
    
