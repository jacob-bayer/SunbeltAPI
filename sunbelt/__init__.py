# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['MAIN_MEDIA_DATABASE']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route('/')
def hello():
    return 'Hello!'


from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify
from sunbelt.api.queries import *
from sunbelt.api.mutations import *
from sunbelt import app

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

mutation = ObjectType("Mutation")
mutation.set_field("createComment", resolve_create_comment)

type_defs = load_schema_from_path("api/schema.graphql")
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers
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


