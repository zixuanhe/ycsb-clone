from fabric.api import run, roles

import sys, os
sys.path.append(os.path.dirname(__file__) + '/../conf/')
import hosts

@roles('server')
def df():
    run('df -h')
