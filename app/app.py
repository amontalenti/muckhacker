from flask import Flask
from flask import abort, jsonify, url_for, render_template, request

import config
from models import Post, datastore
from forms import validate

app = Flask(__name__)

app.config.from_object(config)

@app.route('/')
def home():
    """The home page of your install"""
    posts = datastore.values()
    return render_template('home.html', posts=posts)

@app.route('/api/', methods=['GET'])
def api_root():
    """The root url of our restful json api"""
    below = dict()
    below['posts'] = Post.api()
    below['meta'] = {'url': url_for('meta', _external=True)}
    return jsonify(**below)

@app.route('/api/meta/', methods=['GET'])
def meta():
    """Meta information about the api itself"""
    return jsonify(version=config.API_VERSION)

@app.route('/api/posts/', methods=['GET'])
def all_posts():
    """Returns potentially paginated list of posts in 'list' attr"""
    posts = datastore.values()
    return jsonify(list=map(Post.to_dict, posts))

@app.route('/api/posts/', methods=['POST'])
def create_post():
    """Creates a new post with a new id"""
    if not request.json or not validate(request.json):
        abort(400)
    post = Post(request.json)
    datastore[post.id] = post
    return jsonify(**post.to_dict()), 201

@app.route('/api/posts/<int:post_id>/')
def single_post(post_id):
    """Returns everything in a post as json"""
    post = datastore.get(post_id, None)
    if post is None: # need to do authentication here 
        abort(404)
    return jsonify(**post.to_dict())

@app.route('/api/posts/<int:post_id>/', methods=['PUT'])
def edit_post(post_id):
    """Replaces post behind id with submitted one"""
    post = datastore.get(post_id, None)
    if post is None or not request.json or not validate(request.json):
        abort(400)
    post.update(request.json) 
    datastore[post_id] = post
    return jsonify(**post.to_dict())

if __name__ == "__main__":
    app.run()
