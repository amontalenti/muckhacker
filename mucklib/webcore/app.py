import json

from flask import Flask, Response, session
from flask import abort, url_for, render_template, request, redirect
from flask.ext.pymongo import PyMongo
from flask.ext.pymongo import ObjectId
from flask.ext.login import LoginManager, login_user, login_required, current_user
from markdown2 import Markdown

import config
from models import Post, User
from forms import LoginForm, PostEditForm
from utils import generate_csrf_token

# flask configs/helper functions! #
app = Flask(__name__)
app.config.from_object(config)
# we are going to delay passing app to pymongo
mongo = PyMongo()
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'
markdowner = Markdown()

app.jinja_env.globals['csrf_token'] = generate_csrf_token
app.jinja_env.globals['render_markdown'] = markdowner.convert

# Because we need mongo in our api view functions we have
# dependency issues, be aware!
from api import api
mongo.init_app(app)
# The api routes live in api.py
app.register_blueprint(api)

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

# ROUTES #

@app.route('/')
def home():
    """A simple view of all the content"""
    posts = [Post(bson=d) for d in mongo.db.posts.find()]
    return render_template('home.html', posts=posts)

# ADMIN #

@app.route('/admin/')
@login_required
def admin():
    posts = map(lambda d: Post(bson=d), mongo.db.posts.find())
    return render_template('admin/index.html', 
                            posts=posts,
                            user=current_user)

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
            return redirect(url_for('admin'))
        else:
            error = 'Incorrect username or password.'
    return render_template('login.html', form=form, error=error)

# EDITOR #

@app.route('/edit/<ObjectId:post_id>/')
@login_required
def show_editor(post_id):
    d = mongo.db.posts.find_one(post_id)
    post = Post(bson=d)
    form = PostEditForm()
    return render_template('editor.html', post=post, form=form)

if __name__ == "__main__":
    app.run()
