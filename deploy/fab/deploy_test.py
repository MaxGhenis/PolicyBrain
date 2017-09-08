from __future__ import print_function
from functools import partial
import os
import sys
import boto.exception
import boto.ec2
import datetime
import time
import subprocess

from fabric.api import (
    env,
    settings,
    sudo,
    prefix,
    put,
    cd,
    run,
)

from fabric.tasks import execute

from fabric.contrib.files import (
    comment,
    uncomment,
    exists,
    append,
    sed
)

import logging
from copy_deploy_repo import copy_deploy_repo, check_unmodified
from redeploy import cli as deploy_versions_cli, main as reset_server_main

def test_ssh2():
    '''log.info('Key file: %s' % (key_file))
    log.debug('Trying to connect...')
    for ip in ips:
        env.host = 'ubuntu@' + ip
        env.password = ''
        '''
    run('pwd')

def fix_sshd_config():
    '''root needs an actual shell, so fix the sshd_config.'''
    config_file = '/etc/ssh/sshd_config'
    uncomment(config_file, r'^.*PermitRootLogin yes', use_sudo=True)
    comment(config_file, r'^PermitRootLogin forced-commands-only', use_sudo=True)

def apt_installs():
    run("apt-get install software-properties -common python-software-properties")
    run("add-apt-repository -y ppa:saltstack/salt")
    run("apt-get update -y")
    packages = ['salt-master', 'salt-minion', 'salt-syndic', 'git', 'tig',
                'silversearcher-ag', 'python-qt4']
    run("apt-get install -y {}".format(' '.join(packages)))


def install_deploy_repo():
    run('rm -rf ~/deploy')
    run('mkdir ~/deploy')
    copy_deploy_repo(sudo, put, run)


def install_ogusa_repo():
    url = 'https://github.com/open-source-economics/OG-USA'
    run('rm -rf ~/OG-USA')
    if os.environ.get('OGUSA_GIT_BRANCH'):
        run("git clone {} --branch {}".format(url, os.environ.get('OGUSA_GIT_BRANCH')))
    else:
        run("git clone {}".format(url))


def write_ospc_anaconda_token():
    token = os.environ['OSPC_ANACONDA_TOKEN']
    run('echo {token} &> /home/ubuntu/.ospc_anaconda_token'.format(token=token))


def convenience_aliases():
    run('echo "alias supervisorctl=\'supervisorctl -c /home/ubuntu/deploy/fab/supervisord.conf\'" >> ~/.bashrc')
    run('echo "alias ss=\'sudo /usr/bin/salt-call state.highstate --retcode-passthrough --log-level=debug --config-dir=/home/ubuntu/deploy/fab/salt\'" >> ~/.bashrc')


def run_salt():
    run("ln -s ~/deploy/fab/salt ~/salt")
    run('/usr/bin/salt-call state.highstate --retcode-passthrough --log-level=debug --config-dir="$HOME/deploy/fab/salt"')


def reset_server():
    e = _env_str(DEPLOYMENT_VERSIONS_ARGS)
    command = "{} source /home/ubuntu/reset_server.sh".format(e)
    print('Running', command)
    run(command, shell=True, shell_escape=False)


execute(test_ssh2)
execute(apt_installs)
execute(install_deploy_repo)
execute(install_ogusa_repo)
execute(convenience_aliases)
execute(write_ospc_anaconda_token)
execute(run_salt)
execute(reset_server)
