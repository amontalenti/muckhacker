from flask import Flask, render_template
from flask.ext.script import Manager
from flask_frozen import Freezer
from flask.ext.assets import Environment, Bundle, ManageAssets
from lib.flatpages import FlatPages
from lib.mdjinja import MarkdownJinja

#
# Config
#

DEBUG = True

# Use Markdown for simple pages/content
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

# FREEZER_BASE_URL = "http://localhost/"
FREEZER_RELATIVE_URLS = False

ASSETS_DEBUG = DEBUG

app = Flask(__name__, static_folder="assets")
app.config.from_object(__name__)

#
# Jinja, CSS, LESS, and JS Assets
#
WATCH_PATTERNS = (
    "README.md",
    "/templates/**",
    "/pages/**",
    "/assets/**"
)

assets = Environment(app)

css_files = ['home.less']
css_all = Bundle(*['less/' + file for file in css_files],
                 filters=['less', 'cleancss'], output='gen/css_all.css')
assets.register("css_all", css_all)

js_files = ['home.js']
js_all = Bundle(*['js/' + file for file in js_files],
                filters='rjsmin', output='gen/js_all.js')
assets.register("js_all", js_all)

css_lib_files = ['bootstrap.css', 'bootstrap-theme.css']
css_lib = Bundle(*['lib/css/' + file for file in css_lib_files],
                 filters='cleancss', output='gen/css_lib.css')
assets.register("css_lib", css_lib)

js_lib_files = ['jquery.js', 'underscore.js', 'bootstrap.js', 'd3.js']
js_lib = Bundle(*['lib/js/' + file for file in js_lib_files],
                filters='rjsmin', output='gen/js_lib.js')
assets.register("js_lib", js_lib)

#
# Plugins
#

freezer = Freezer(app)
pages = FlatPages(app)
md = MarkdownJinja(app)
manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))

#
# Routes
#


@app.route('/')
def index():
    page = pages.get("index")
    return render_template("page.jinja", page=page)


@app.route('/list/')
def list():
    return render_template("allpages.jinja", pages=pages)


@app.route('/pages/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    return render_template('page.jinja', page=page)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('alltags.jinja', pages=tagged, tag=tag)


#
# livereload infra
#


from livereload import Server, shell
from formic import FileSet
from os import getcwd, path


def make_livereload_server(wsgi_app):
    server = Server(wsgi_app)

    # XXX: build step could be useful, e.g.
    # making it `python app.py build`, but
    # in this use case not really necessary
    build_cmd = "true"

    print "Files being monitored:"

    cwd = getcwd()

    for pattern in WATCH_PATTERNS:
        print "Pattern: ", pattern
        for filepath in FileSet(include=pattern):
            print "=>", path.relpath(filepath, cwd)
            server.watch(filepath, build_cmd)
        print

    return server


#
# Commands
#


@manager.command
def build():
    """Creates a static version of site in ./build."""
    freezer.freeze()


@manager.command
def livereload():
    """Runs the Flask development server under livereload."""
    # wire livereload to Flask via wsgi
    flask_wsgi_app = app.wsgi_app
    server = make_livereload_server(flask_wsgi_app)
    # serve application
    server.serve(host='127.0.0.1', port=5000)


if __name__ == "__main__":
    manager.run()
