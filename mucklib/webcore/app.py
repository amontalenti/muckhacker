import json, os, binascii

from flask import Flask, Response, session
from flask import abort, jsonify, url_for, render_template, request, redirect
from flask.ext.pymongo import PyMongo
from flask.ext.pymongo import ObjectId
from flask.ext.login import LoginManager, login_user, login_required, current_user
from bson.json_util import dumps

import config
from models import Post, User, PostEncoder
from forms import PostEditForm, LoginForm

app = Flask(__name__, static_url_path='/static', static_folder='../../vendor')
app.config.from_object(config)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = binascii.b2a_hex(os.urandom(20))
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(_id):
    """Flask-login hook into mongo"""
    r_dict = mongo.db.users.find_one(ObjectId(_id))
    if r_dict is None:
        return None
    user = User(r_dict['username'], 
                r_dict['password'],
                r_dict['_id'])
    return user

@app.route('/')
def home():
    """The home page of your install"""
    posts = [Post(bson=d) for d in mongo.db.posts.find()]
    return render_template('home.html', posts=posts)

@app.before_request
def crsf_protect():
    if request.method in ['POST', 'PUT']:
        token = session.pop('_csrf_token', None)
        if request.headers.get('Content-Type') == "application/json":
            json = request.get_json()
            # check for csrf in json
            if not token or token != json.pop('_csrf_token', None):
                abort(403)
        else:
            # else check in the form
            if not token or token != request.form.get('_csrf_token'):
                abort(403)

@app.route('/admin/')
@login_required
def admin():
    return Response("You are logged in brotha! %s" % str(current_user))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        uname = form.username.data
        pw = form.password.data
        user, authenticated = User.authenticate(mongo.db, uname, pw)
        if authenticated:
            login_user(user)
            print user
            return redirect(url_for('home'))
        else:
            error = 'Incorrect username or password.'
    return render_template('login.html', form=form, error=error)

@app.route('/edit/<ObjectId:post_id>/')
@login_required
def show_editor(post_id):
    d = mongo.db.posts.find_one(post_id)
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
    return jsonify(version=config.API_VERSION, author="nskelsey")

@app.route('/api/posts/')
def all_posts():
    """Returns potentially paginated list of posts in 'list' attr"""
    cursor = mongo.db.posts.find().limit(10)
    posts = map(lambda bs: Post(bson=bs), cursor)
    out_json = json.dumps({'list' : posts}, cls=PostEncoder, indent=2)
    resp = Response(out_json, mimetype='application/json')
    return resp

@app.route('/api/posts/', methods=['POST'])
@login_required
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
    post_d = mongo.db.posts.find_one(post_id)
    if post_d is None:
        abort(404)
    post = Post(bson=post_d)
    return jsonify(**post.to_dict())

@app.route('/api/posts/<ObjectId:post_id>/', methods=['PUT'])
@login_required
def edit_post(post_id):
    """Replaces post behind id with submitted one"""
    query = {'_id': post_id}
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
        print form.errors #TODO
        abort(403)

if __name__ == "__main__":
    app.run()
