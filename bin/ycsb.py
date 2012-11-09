from fabric.api import run, roles, env

import sys, os
sys.path.append(os.path.dirname(__file__) + '/../conf/')
import hosts, workloads, databases

totalclients = len(env.roledefs['client'])
clientno = 0

def _outfilename():
    pass

def _ycsbloadcmd(database, clientno):
    cmd = workloads.root + '/bin/ycsb load -s'
    if not databases.databases.has_key(database):
        raise Exception("unconfigured database '%s'" % database)
    for (key, value) in databases.databases[database]['properties'].items():
        cmd += ' -p %s=%s' % (key, value)
    for (key, value) in workloads.data.items():
        cmd += ' -p %s=%s' % (key, value)
    insertcount = workloads.data['recordcount'] / totalclients
    insertstart = insertcount * clientno
    cmd += ' -p insertstart=%s' % insertstart
    cmd += ' -p insertcount=%s' % insertcount
    return cmd

@roles('client')
def load(database):
    global clientno
    run('echo %s' % _ycsbloadcmd(database, clientno))
    clientno += 1
