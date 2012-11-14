import fabric
from fabric.api import *
from fabric.contrib.console import confirm

from datetime import datetime, timedelta

import sys, os
sys.path.append(os.path.dirname(__file__) + '/../conf/')
import hosts, workloads, databases
from pdb import set_trace

totalclients = len(env.roledefs['client'])
clientno = 0

timestamp = datetime.now(hosts.timezone).replace(second=0, microsecond=0) + timedelta(minutes=2)
print timestamp

def _getdb(database):
    if not databases.databases.has_key(database):
        raise Exception("unconfigured database '%s'" % database)
    return databases.databases[database]

def _getworkload(workload):
    if not workloads.workloads.has_key(workload):
        raise Exception("unconfigured workload '%s'" % workload)
    return workloads.workloads[workload]

def _outfilename(databasename, workloadname, extension):    #TODO add target to the file name
    global timestamp
    timestampstr = timestamp.strftime('%Y-%m-%d_%H-%M')
    return '%s_%s_%s.%s' % (timestampstr, databasename, workloadname, extension)

def _at(cmd, time=timestamp):
    return 'echo "%s" | at %s today' % (cmd, time.strftime('%H:%M'))

def _ycsbloadcmd(database, clientno):
    cmd = workloads.root + '/bin/ycsb load %s -s' % database['command']
    for (key, value) in database['properties'].items():
        cmd += ' -p %s=%s' % (key, value)
    for (key, value) in workloads.data.items():
        cmd += ' -p %s=%s' % (key, value)
    insertcount = workloads.data['recordcount'] / totalclients
    insertstart = insertcount * clientno
    cmd += ' -p insertstart=%s' % insertstart
    cmd += ' -p insertcount=%s' % insertcount
    outfile = _outfilename(database['name'], 'load', 'out')
    errfile = _outfilename(database['name'], 'load', 'err')
    cmd += ' > %s/%s' % (database['home'], outfile)
    cmd += ' 2> %s/%s' % (database['home'], errfile)
    return cmd

def _ycsbruncmd(database, workload, target=None):
    cmd = workloads.root + '/bin/ycsb run %s -s' % database['command']
    for file in workload['propertyfiles']:
        cmd += ' -P %s' % file
    for (key, value) in database['properties'].items():
        cmd += ' -p %s=%s' % (key, value)
    for (key, value) in workloads.data.items():
        cmd += ' -p %s=%s' % (key, value)
    if target != None:
        cmd += ' -target %s' % str(target)
    outfile = _outfilename(database['name'], workload['name'], 'out')
    errfile = _outfilename(database['name'], workload['name'], 'err')
    cmd += ' > %s/%s' % (database['home'], outfile)
    cmd += ' 2> %s/%s' % (database['home'], errfile)
    return cmd

@roles('client')
def load(db):
    global clientno
    database = _getdb(db)
    with cd(database['home']):
        run(_at(_ycsbloadcmd(database, clientno)))
    clientno += 1

@roles('client')
def workload(db, workload, target=None):
    global clientno
    
    database = _getdb(db)
    load = _getworkload(workload)
    with cd(database['home']):
        if target != None:
            run(_at(_ycsbruncmd(database, load, int(target) / totalclients)))
        else:
            run(_at(_ycsbruncmd(database, load)))
    clientno += 1


@roles('client')
def status(db):
    """ show tail of the .err output """
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        # fabric.state.output['running'] = False
        # env.output_prefix = False
        database = _getdb(db)
        with(cd(database['home'])):
            #run('tail -n 2 /var/spool/cron/atjobs/*')
            #run('ps -f -C java')
            # sort the ouptput of ls by date, the first entry should be the *.err needed
            ls = run('ls --format single-column --sort=t').split("\r\n")
            tail = run('tail %s' % ls[0])
            print(tail)
            print('') # skip the line for convenience


@roles('client')
def kill():
    with settings(warn_only=True):
        run('ps -f -C java')
        if confirm("Do you want to kill Java on the client?"):
            run('killall java')
