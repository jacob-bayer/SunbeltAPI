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
mutation.set_field("createPost", resolve_create_post)
mutation.set_field("createAccount", resolve_create_account)
mutation.set_field("createSubreddit", resolve_create_subreddit)

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



# https://flask-jwt-extended.readthedocs.io/en/stable/


# from flask_jwt_extended import create_access_token
# from flask_jwt_extended import get_jwt_identity
# from flask_jwt_extended import jwt_required
# from flask_jwt_extended import JWTManager

# from dotenv import load_dotenv

# load_dotenv()
# app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
# jwt = JWTManager(app)

# @app.route("/login", methods=["POST"])
# def login():
#     if not request.is_json:
#         return jsonify({"msg": "Missing JSON in request"}), 400

#     username = request.json.get("username", None)
#     password = request.json.get("password", None)
#     if not username:
#         return jsonify({"msg": "Missing username parameter"}), 400
#     if not password:
#         return jsonify({"msg": "Missing password parameter"}), 400

#     if username != "test" or password != "test":
#         return jsonify({"msg": "Bad username or password"}), 401

#     # Identity can be any data that is json serializable
#     access_token = create_access_token(identity=username)
#     return jsonify(access_token=access_token), 200


# # Protect a route with jwt_required, which will kick out requests
# # without a valid JWT present.
# @app.route("/protected", methods=["GET"])
# @jwt_required()
# def protected():
#     breakpoint()
#     # Access the identity of the current user with get_jwt_identity
#     current_user = get_jwt_identity()
#     return jsonify(logged_in_as=current_user), 200
