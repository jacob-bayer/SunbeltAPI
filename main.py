# -*- coding: utf-8 -*-

# This is its own file because it is a circular import
# where these routes need to import the resolvers which depend on 
# the app being initialized already.
from api import app, db



from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify

from api.queries import *
from api.mutations import *

query = ObjectType("Query")

query.set_field("post", resolve_post)
query.set_field("posts", resolve_posts)
query.set_field("postdetail", resolve_post_detail)
query.set_field("postdetails", resolve_post_details)

query.set_field("comment", resolve_comment)
query.set_field("comments", resolve_comments)
query.set_field("commentdetail", resolve_comment_detail)
query.set_field("commentdetails", resolve_comment_details)

query.set_field("account", resolve_account)
query.set_field("accounts", resolve_accounts)
query.set_field("accountdetail", resolve_account_detail)
query.set_field("accountdetails", resolve_account_details)

query.set_field("subreddit", resolve_subreddit)
query.set_field("subreddits", resolve_subreddits)
query.set_field("subredditdetail", resolve_subreddit_detail)
query.set_field("subredditdetails", resolve_subreddit_details)

# mutation = ObjectType("Mutation")
# mutation.set_field("createComment", resolve_create_comment)
# mutation.set_field("createPost", resolve_create_post)
# mutation.set_field("createAccount", resolve_create_account)
# mutation.set_field("createSubreddit", resolve_create_subreddit)
# mutation.set_field("createSunobjects", resolve_create_sun_objects)

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


# The purpose of this is to try to run the app and get package dependency errors
if __name__ == '__main__':
    app.run(debug=True)


from rq import Queue
from redis_worker import conn

from flask_jwt_extended import (jwt_required,
                                get_jwt_identity)

from api.batch_add import batch_create_from_json

# works with is_async=False
redis_q = Queue('SunbeltInsertQueue', connection=conn, is_async=True)

@app.route("/add_batch_data", methods=["POST"])
@jwt_required()
def queue_mutation():
    current_user = get_jwt_identity()
    if current_user != 'admin':
        return jsonify({"msg": "Not authorized"}), 401
    try:
        redis_q.enqueue(batch_create_from_json, request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": e}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8000)