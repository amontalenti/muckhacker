import textwrap
import tempfile

from fabric.api import *
from fabric.contrib.files import exists, contains, append, comment, uncomment, upload_template
from fabric.contrib.console import confirm
from fabric.contrib.project import rsync_project
from fabric.colors import *

import cuisine

env.forward_agent = True
env.use_ssh_config = True

# must have machine set up as an SSH configuration entry 'muckhacker'
# look inside ~/.ssh/config for details
env.hosts = ["muckhacker"]

# project path; would like to factor out :/
PATH = "/home/ubuntu/muckhacker" # sensitive to trailing slash

@task
def list_home():
    run("ls ~/")

def add_apt_repository(repo):
    sudo("add-apt-repository -y {}".format(repo))

def setup_aptfast():
    add_apt_repository("ppa:apt-fast/stable")
    sudo("apt-get -q update")
    sudo("apt-get -q -y install axel")
    with prefix('export DEBIAN_FRONTEND=noninteractive'):
        sudo("apt-get -q -y --force-yes install apt-fast")

def setup_mongodb():
    sudo("apt-fast -q -y install mongodb-server")

def setup_python():
    cuisine.package_ensure("python2.7")
    sudo("apt-fast -q -y install python-pip")
    sudo("apt-fast -q -y install python-dev")

def setup_nodejs():
    add_apt_repository('ppa:chris-lea/node.js')
    sudo("apt-fast -q update")
    sudo("apt-fast -q -y install nodejs")
    sudo("apt-fast -q -y install npm")

def setup_ghost():
    run("mkdir -p ~/data/apps/")
    run("git clone git@github.com:TryGhost/Ghost.git ~/data/apps/ghost")
    with cd("~/data/apps/ghost"):
        run("npm install")

def setup_ghost_dev():
    cuisine.package_ensure("ruby")
    cuisine.package_ensure("rubygems")
    sudo("gem install bundler")
    sudo("gem install sass")
    sudo("gem install bourbon")
    sudo("npm install -g grunt-cli")
    with cd("~/data/apps/ghost"):
        run("grunt init")
        run("grunt prod")

def setup_supervisor():
    cuisine.package_ensure("supervisor")
    supervisor_cfg = """
    [program:ghost]
    command = node index.js
    directory = /home/ubuntu/data/apps/ghost
    user = ubuntu
    autostart = true
    autorestart = true
    stdout_logfile = /var/log/supervisor/ghost.log
    stderr_logfile = /var/log/supervisor/ghost_err.log
    environment = NODE_ENV="production"
    """
    supervisor_cfg = textwrap.dedent(supervisor_cfg.strip())
    fd, filename = tempfile.mkstemp()
    with open(filename, "w") as openfile:
        openfile.write(supervisor_cfg)
    upload_template(filename, "/etc/supervisor/conf.d/ghost.conf", use_sudo=True)
    sudo("supervisorctl start ghost")

def install_requirements():
    cuisine.package_ensure("python-pip")
    with cd(PATH):
        sudo("pip install -r requirements.txt")

def update_src():
    if cuisine.dir_exists(PATH) is False:
        parent_dir = "/".join(PATH.split("/")[:-1])
        with cd(parent_dir): # path above dir
            sudo("git clone https://github.com/amontalenti/muckhacker")
    else:
        with cd(PATH):
            sudo("git pull origin master")

@task
def provision():
    if cuisine.command_check("apt-fast") is False:
        setup_aptfast()
    if cuisine.command_check("mongo") is False:
        setup_mongodb()
    if cuisine.command_check("python-dev") is False:
        setup_python()
    update_src()
    install_requirements()

@task
def restart_ghost():
    sudo("supervisorctl restart ghost")
