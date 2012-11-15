import fabric
from fabric.api import *
from fabric.colors import green, blue
from fabric.contrib.console import confirm

from datetime import datetime, timedelta

import sys, os, re, time
sys.path.append(os.path.dirname(__file__) + '/../conf/')
import hosts, workloads, databases
from pdb import set_trace

totalclients = len(env.roledefs['client'])
# clientno = 0 # obsolete
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

def _outfilename(databasename, workloadname, extension, target=None):
    global timestamp
    timestampstr = timestamp.strftime('%Y-%m-%d_%H-%M')
    if target == None:
        return '%s_%s_%s.%s' % (timestampstr, databasename, workloadname, extension)
    else:
        return '%s_%s_%s_%s.%s' % (timestampstr, databasename, workloadname, str(target), extension)

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
    outfile = _outfilename(database['name'], workload['name'], 'out', target)
    errfile = _outfilename(database['name'], workload['name'], 'err', target)
    cmd += ' > %s/%s' % (database['home'], outfile)
    cmd += ' 2> %s/%s' % (database['home'], errfile)
    return cmd

def _client_no():
    return env.all_hosts.index(env.host)

@roles('client')
def load(db):
    """Starts loading of data to the database"""
    clientno = _client_no()
    database = _getdb(db)
    with cd(database['home']):
        run(_at(_ycsbloadcmd(database, clientno)))

@roles('client')
def workload(db, workload, target=None):
    """Starts running of the workload"""
    clientno = _client_no()
    database = _getdb(db)
    load = _getworkload(workload)
    with cd(database['home']):
        if target != None:
            run(_at(_ycsbruncmd(database, load, int(target) / totalclients)))
        else:
            run(_at(_ycsbruncmd(database, load)))

@roles('client')
def status(db):
    """ Shows status of the currently running YCSBs """
    with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
        print blue('Scheduled:', bold = True)
        print run('tail -n 2 /var/spool/cron/atjobs/*')
        print
        print blue('Running:', bold = True)
        print run('ps -f -C java')
        print
        database = _getdb(db)
        with(cd(database['home'])):
            # sort the output of ls by date, the first entry should be the *.err needed
            ls = run('ls --format=single-column --sort=t *.err').split("\r\n")
            logfile = ls[0]
            tail = run('tail %s' % logfile)
            print blue('Log:', bold = True), green(logfile, bold = True)
            print tail
            print  # skip the line for convenience

@parallel
@roles('client')
@with_settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True)
def get(db, regex='.*', do=False):
    """ Show *.err and *.out logs satisfying the regex to be transferred """
    p = re.compile(regex)
    database = _getdb(db)
    cn = _client_no() + 1
    with cd(database['home']):
        ls = run('ls --format=single-column --sort=t *.err *.out').split("\r\n")
        file_name = [f for f in ls if p.search(f)][0] # the most recent file satisfying pattern
        f0 = os.path.splitext(file_name)[0]           # strip off extension
    # now we have the map {'host' -> 'xxx'}
    # perform self-check and maybe continue
    print blue('Filename at c%s: ' % cn, bold = True), green(f0, bold = True)
    # now do the processing, if enabled
    if do:
        with cd(database['home']):
            fbz2err = '%s-c%s-err.bz2' % (f0, cn)
            fbz2out = '%s-c%s-out.bz2' % (f0, cn)
            # packing
            print blue('c%s packing ...' % cn)
            run('tar -jcvf %s %s.err' % (fbz2err, f0))
            run('tar -jcvf %s %s.out' % (fbz2out, f0))
            # donwload them
            print blue('c%s transferring ...' % cn)
            remote_cmd_err = 'root@%s:%s/%s' % (env.host, database['home'], fbz2err)
            local('scp %s .' % remote_cmd_err)
            remote_cmd_out = 'root@%s:%s/%s' % (env.host, database['home'], fbz2out)
            local('scp %s .' % remote_cmd_out)
            # unpacking to custom name
            print blue('c%s unpacking ...' % cn)
            #local('tar -xvf %s %s-%s.err' % (fbz2err, f0, cn))
            #local('tar -xvf %s %s-%s.out' % (fbz2err, f0, cn))
    

@roles('client')
def kill():
    """Kills YCSB processes"""
    with settings(warn_only=True):
        run('ps -f -C java')
        if confirm("Do you want to kill Java on the client?"):
            run('killall java')
