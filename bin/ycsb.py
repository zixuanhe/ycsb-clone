from fabric.api import run, roles, env

import sys, os
sys.path.append(os.path.dirname(__file__) + '/../conf/')
import hosts, workloads

totalclients = len(env.roledefs['client'])
clientno = 0

def _ycsbloadcmd(database, clientno):
    cmd = workloads.root + '/bin/ycsb load ' + database + ' -s '
    insertcount = workloads.data['recordcount'] / totalclients
    insertstart = insertcount * clientno
    cmd += '-p insertstart=%s ' % insertstart
    cmd += '-p insertcount=%s ' % insertcount
    return cmd

@roles('client')
def load(database):
    global clientno
    run('echo %s' % _ycsbloadcmd(database, clientno))
    clientno += 1
