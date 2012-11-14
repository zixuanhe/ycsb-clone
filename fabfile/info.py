from fabric.api import run, roles
from conf import hosts

@roles('server')
def df():
    """Shows the free disk space on servers"""
    run('df -h')
