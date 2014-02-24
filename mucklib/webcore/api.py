import json

from flask import Response, Blueprint
from flask import abort, jsonify, url_for, request
from flask.ext.login import login_required

from models import Post, PostEncoder
from forms import PostEditForm
from utils import generate_csrf_token

# Circular dependency! Proceed with caution
api = Blueprint('api', __name__, url_prefix='/api')
# app.py import api first
from app import mongo


# API #

@api.route('/') # defaults to only serve GET
def api_root():
    """The root url of our restful json api"""
    below = dict()
    below['posts'] = Post.api()
    below['meta'] = {'url': url_for('api.meta', _external=True)}
    return jsonify(**below)

@api.route('/meta/')
def meta():
    """Meta information about the api itself"""
    return jsonify(version=config.API_VERSION, author="nskelsey")

@api.route('/posts/')
def all_posts():
    """Returns potentially paginated list of posts in 'list' attr"""
    cursor = mongo.db.posts.find().limit(10)
    posts = map(lambda bs: Post(bson=bs), cursor)
    out_json = json.dumps({'list' : posts}, cls=PostEncoder, indent=2)
    resp = Response(out_json, mimetype='application/json')
    return resp

@api.route('/posts/', methods=['POST'])
@login_required
def create_post():
    """Creates a new post with a new id"""
    if not request.json:
        abort(400)
    form = PostEditForm.from_json(request.json, skip_unkown_keys=False)
    if form.validate():
        post = Post(json=form.data)
        objId = mongo.db.posts.insert(post.to_bson())
        post.id = str(objId)
        return jsonify(**post.to_dict()), 201
    else:
        abort(400)

@api.route('/posts/<ObjectId:post_id>/')
def single_post(post_id):
    """Returns everything in a post as json"""
    post_d = mongo.db.posts.find_one(post_id)
    if post_d is None:
        abort(404)
    post = Post(bson=post_d)
    return jsonify(**post.to_dict())

@api.route('/posts/<ObjectId:post_id>/', methods=['PUT'])
@login_required
def edit_post(post_id):
    """Replaces post behind id with submitted one"""
    post_d = mongo.db.posts.find_one(post_id)
    if post_d is None:
        abort(404) 
    form = PostEditForm.from_json(request.json, skip_unknown_keys=False)
    if form.validate():
        post = Post(bson=post_d)
        post.update(form.data)
        query = {'_id': post_id}
        mongo.db.posts.update(query, post.to_bson())
        # needed for chaining multiple edits together
        token = generate_csrf_token()
        return jsonify(_csrf=token, **post.to_dict())
    else:
        print form.errors #TODO
        abort(400)


# no csrf protection here
@api.route('/delete/<ObjectId:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post_d = mongo.db.posts.find_one(post_id)
    if post_d is None:
        abort(404)
    # in future must check that the user is the owner of the post
    mongo.db.posts.remove(post_id)
    return jsonify(success=True)
