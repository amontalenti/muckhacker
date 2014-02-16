import json

from flask import Flask
from flask import abort, jsonify, url_for, render_template, request, Response
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps

import config
from models import Post, PostEncoder
from forms import PostEditForm

app = Flask(__name__, static_url_path="/static", static_folder="../../vendor")
app.config.from_object(config)

mongo = PyMongo(app)


@app.route('/')
def home():
    """The home page of your install"""
    posts = [Post(bson=d) for d in mongo.db.posts.find()]
    return render_template('home.html', posts=posts)

@app.route('/edit/<ObjectId:post_id>/')
def show_editor(post_id):
    query = {'_id' : post_id}
    d = mongo.db.posts.find_one(query)
    post = Post(bson=d)
    form = PostEditForm()
    return render_template('posts/edit.html', post=post, form=form)

@app.route('/api/') # defaults to only serve GET
def api_root():
    """The root url of our restful json api"""
    below = dict()
    below['posts'] = Post.api()
    below['meta'] = {'url': url_for('meta', _external=True)}
    return jsonify(**below)

@app.route('/api/meta/')
def meta():
    """Meta information about the api itself"""
    return jsonify(version=config.API_VERSION)

@app.route('/api/posts/')
def all_posts():
    """Returns potentially paginated list of posts in 'list' attr"""
    cursor = mongo.db.posts.find().limit(10)
    posts = map(lambda bs: Post(bson=bs), cursor)
    out_json = json.dumps({'list' : posts}, cls=PostEncoder, indent=2)
    resp = Response(out_json, mimetype='application/json')
    return resp

@app.route('/api/posts/', methods=['POST'])
def create_post():
    """Creates a new post with a new id"""
    if not request.json: # or not validate(request.json):
        abort(400)
    post = Post(json=request.json)
    objId = mongo.db.posts.insert(post.to_bson())
    post.id = str(objId)
    return jsonify(**post.to_dict()), 201

@app.route('/api/posts/<ObjectId:post_id>/')
def single_post(post_id):
    """Returns everything in a post as json"""
    post_d = mongo.db.posts.find_one({'_id': post_id})
    post = Post(bson=post_d)
    if post_d is None:
        abort(404)
    return jsonify(**post.to_dict())

@app.route('/api/posts/<ObjectId:post_id>/', methods=['PUT'])
def edit_post(post_id):
    """Replaces post behind id with submitted one"""
    query = {'_id' : post_id}
    post_d = mongo.db.posts.find_one(query)
    if post_d is None:
        abort(404) 
    form = PostEditForm.from_json(request.json, skip_unknown_keys=False)
    if form.validate():
        post = Post(bson=post_d)
        post.update(form.data)
        mongo.db.posts.update(query, post.to_bson())
        return jsonify(**post.to_dict())
    else:
        print form.errors
        abort(403)

if __name__ == "__main__":
    app.run()
