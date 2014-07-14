import fabric
from fabric.api import *
from fabric.colors import *
import shutil

# environments
# ~~~~~~~~~~~~

@task
def dev():
    """env: divshot 'development' environment."""
    env.deploy_cmd = "divshot push development"
    env.base_url = "http://development.XXX-your-divshot-app-name-XXX.divshot.io/"
    env.prod_mode = False

@task
def prod():
    """env: divshot 'production' environment."""
    env.deploy_cmd = "divshot push production"
    env.base_url = "http://XXX-your-divshot-app-name-XXX.divshot.io/"
    env.prod_mode = True

# deploy & test
# ~~~~~~~~~~~~~

@task
def deploy():
    puts(blue("Patching deploy settings..."))
    shutil.copyfile("app.py", "tmp.py")
    local("sed -i -e's/# FREEZER_BASE_URL/FREEZER_BASE_URL/' tmp.py")
    local("sed -i -e's,= \"http://localhost/\",= \"{}\",' tmp.py".format(env.base_url))
    if env.prod_mode:
        local("sed -i -e's/^DEBUG = True/DEBUG = False/' tmp.py")
    puts(blue("Building static site into ./build/..."))
    local("python tmp.py build")
    puts(blue("Cleaning asset cache..."))
    local("rm -Rf build/assets/.webassets-cache")
    puts(blue("Deploying with '{}'".format(env.deploy_cmd)))
    local(env.deploy_cmd)
    puts(blue("Cleaning up..."))
    # cleanup
    local("rm tmp.py")
    puts(green("Done!"))


# custom tasks
# ~~~~~~~~~~~~


@task
def build():
    """Build the static website in ./build/ with Frozen-Flask."""
    local("python app.py build")


@task
def runserver():
    """Serve Flask app normally."""
    local("python app.py runserver")


@task
def livereload():
    """Serve Flask app via livereload."""
    local("python app.py livereload")
