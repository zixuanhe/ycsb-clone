from fabric.api import run, roles, env, settings
from fabric.contrib.console import confirm

from datetime import datetime

import sys, os
sys.path.append(os.path.dirname(__file__) + '/../conf/')
import hosts, workloads, databases

totalclients = len(env.roledefs['client'])
clientno = 0

timestamp = datetime.now(hosts.timezone)
timestampstr = timestamp.strftime('%Y-%m-%d_%H-%M')

def _getdb(database):
    if not databases.databases.has_key(database):
        raise Exception("unconfigured database '%s'" % database)
    return databases.databases[database]

def _getworkload(workload):
    if not workloads.workloads.has_key(workload):
        raise Exception("unconfigured workload '%s'" % workload)
    return workloads.workloads[workload]

def _outfilename(databasename, workloadname, extension):
    global timestampstr
    return '%s_%s_%s.%s' % (timestampstr, databasename, workloadname, extension)

def _ycsbloadcmd(database, clientno):
    cmd = workloads.root + '/bin/ycsb load -s'
    db = _getdb(database)
    for (key, value) in db['properties'].items():
        cmd += ' -p %s=%s' % (key, value)
    for (key, value) in workloads.data.items():
        cmd += ' -p %s=%s' % (key, value)
    insertcount = workloads.data['recordcount'] / totalclients
    insertstart = insertcount * clientno
    cmd += ' -p insertstart=%s' % insertstart
    cmd += ' -p insertcount=%s' % insertcount
    outfile = _outfilename(db['name'], 'load', 'out')
    errfile = _outfilename(db['name'], 'load', 'err')
    cmd += ' > %s' % outfile
    cmd += ' 2> %s' % errfile
    cmd += ' &'
    return cmd

@roles('client')
def load(database):
    global clientno
    run('echo %s' % _ycsbloadcmd(database, clientno))
    clientno += 1

@roles('client')
def kill():
    if confirm("Do you want to kill Java on the client?"):
        with settings(warn_only=True):
            run('killall java')
