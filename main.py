# -*- coding: utf-8 -*-

# This is its own file because it is a circular import
# where these routes need to import the resolvers which depend on 
# the app being initialized already.
from api import app, db



from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify

from api.queries import resolve_get, resolve_get_all

from datetime import datetime
from rq import Queue
from redis_worker import conn

from flask_jwt_extended import (jwt_required,
                                get_jwt_identity)

from api.batch_add import batch_create_from_json

query = ObjectType("Query")

kinds = ['post', 'comment', 'account', 'subreddit']
for kind in kinds:
    query.set_field(kind, resolve_get)
    query.set_field(f"{kind}s", resolve_get_all)


type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(
    type_defs, query, snake_case_fallback_resolvers #mutation, 
)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        #debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


redis_q = Queue('SunbeltInsertQueue', connection=conn)

@app.route("/add_batch_data", methods=["POST"])
@jwt_required()
def queue_mutation():
    current_user = get_jwt_identity()
    if current_user != 'admin':
        return jsonify({"msg": "Not authorized"}), 401
    try:

        # This is not going to fail unless redis doesn't work
        # TODO: Figure out a way to handle redis errrors
        redis_q.enqueue(batch_create_from_json, request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": e}), 400

