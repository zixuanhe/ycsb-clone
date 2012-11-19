import re, time, os
from datetime import datetime, timedelta
from pdb import set_trace

from fabric.api import *
from fabric.colors import green, blue
from fabric.contrib.console import confirm

from conf import hosts, workloads, databases

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
        if key == 'operationcount':
            cmd += ' -p %s=%s' % (key, value / totalclients)
        else:
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
        if key == 'operationcount':
            cmd += ' -p %s=%s' % (key, int(value) / totalclients)
        else:
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

@roles('client')
def getlog(db, regex='.*', do=False):
    """ Show *.err and *.out logs satisfying the regex to be transferred """
    with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
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
                fbz2err_full = '%s/%s' % (database['home'], fbz2err)
                get(fbz2err_full, fbz2err)
                fbz2out_full = '%s/%s' % (database['home'], fbz2out)
                get(fbz2out_full, fbz2out)
                # the files are here, remove remote bz2
                run('rm -f %s' % fbz2err)
                run('rm -f %s' % fbz2out)
                # unpacking to custom name
                print blue('c%s unpacking ...' % cn)
                local('tar -xvf %s' % fbz2err)
                local('tar -xvf %s' % fbz2out)
                # unpacked ok, remove remote bz2
                local('rm -f %s' % fbz2err)
                local('rm -f %s' % fbz2out)
                # print blue('c%s renaming to short names ...' % cn)
                # local('mv %s.err c%s.err' % (f0, cn))
                # local('mv %s.out c%s.out' % (f0, cn))
                print blue('c%s renaming ...' % cn)
                local('mv %s.err %s-c%s.err' % (f0, f0, cn))
                local('mv %s.out %s-c%s.out' % (f0, f0, cn))

@roles('client')
def kill():
    """Kills YCSB processes"""
    with settings(warn_only=True):
        run('ps -f -C java')
        if confirm("Do you want to kill Java on the client?"):
            run('killall java')

@runs_once
def _build_and_upload():
    local('mvn clean package')
    put('distribution/target/ycsb-0.1.4.tar.gz', '~/ycsb.tar.gz')

@roles('client')
def deploy():
    """Builds and deploys YCSB to the clients"""
    _build_and_upload()
    client1 = env.roledefs['client'][0]
    run('scp %s:ycsb.tar.gz .' % client1)
    with cd('/opt'):
        run('rm -r ycsb-0.1.4')
        run('tar xzvf ~/ycsb.tar.gz')

@roles('client')
@parallel
def test(db):
    """ test parallel of fabric 1.3.2"""
    with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
        run('cd /tmp')
        ls = run('ls -al')
        print ls
