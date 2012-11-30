#!/usr/bin/python
import re
from fabric import tasks
from time import sleep
from fabric.context_managers import hide, settings, cd
from fabric.network import disconnect_all
from fabric.operations import run, put
from conf.hosts import env
from fabfile.helpers import get_db, get_workload, _at, base_time, almost_nothing, get_outfilename

env.user = 'vagrant'
env.password = 'vagrant'
#servers = env.roledefs['server']
#clients = ['192.168.0.11', '192.168.0.12', '192.168.0.13', '192.168.0.14']
clients = ['192.168.8.108', '192.168.9.213', '192.168.8.41', '192.168.8.118']
# lock file name, it shows that the test is still running
lock = 'run_workload.lock'
# benchmark file name, it loads the CPU to consume time
benchmark = 'n-body.py'

def prepare_ycsbruncmd(database, workload, the_time, param):
#    cmd = 'touch %s && chmod 444 %s' % (lock, lock)
#    cmd += workloads.root + '/bin/ycsb run %s -s' % database['command']
#    for file in workload['propertyfiles']:
#        cmd += ' -P %s' % file
#    for (key, value) in database['properties'].items():
#        cmd += ' -p %s=%s' % (key, value)
#    for (key, value) in workloads.data.items():
#        if key == 'operationcount':
#            cmd += ' -p %s=%s' % (key, int(value) / totalclients)
#        else:
#            cmd += ' -p %s=%s' % (key, value)
#    if target is not None:
#        cmd += ' -target %s' % str(target)
    cmd = 'touch %s && chmod 444 %s' % (lock, lock)
    cmd += ' && ./%s %s' % (benchmark, param)
    outfile = get_outfilename(database['name'], workload['name'], 'out', the_time, param)
    errfile = get_outfilename(database['name'], workload['name'], 'err', the_time, param)
    cmd += ' > %s/%s' % (database['home'], outfile)
    cmd += ' 2> %s/%s' % (database['home'], errfile)
    # remove lock in any case
    cmd += ' ; rm -f %s' % lock
    return cmd

def initialize(hosts, db):
    """
    Prepares hosts to run the series
    """
    database = get_db(db)
    def inner_initialize():
        with cd(database['home']):
            # if the file do exist, then the host is NOT ready => False
            # returns a map from hosts to True or False
            run('rm -rf ./*')
            put(benchmark, benchmark, mode=0744)
            print 'host %s initialized ' % env.host
    with almost_nothing():
        tasks.execute(inner_initialize, hosts=hosts)

def poll_hosts(hosts, db):
    """
    Returns a map from host to pairs (no_file, no_jobs), each pair
    is the pair of booleans means that is there the lock file and
    are there any jobs scheduled.
    """
    database = get_db(db)
    rs = dict()
    def inner_poll_hosts():
        with cd(database['home']):
            # if the file do exist, then the host is NOT ready => False
            no_file = bool(run('[ -f %s ]' % lock).return_code)
            # if are there jobs scheduled, then the host is NOT ready
            pj = re.compile('\d+\s+.*')
            no_jobs = not pj.match(run('atq'))
            rs[env.host] = (no_file, no_jobs)
    with almost_nothing():
        tasks.execute(inner_poll_hosts, hosts=hosts)
    return rs

def infinite_wait(hosts, db, delay = 10):
    """
    Waits until all the servers become ready, delay in seconds
    """
    while True:
        rs = poll_hosts(hosts, db)
        locked    = [it[0] for it in rs.items() if it[1][0] == False]
        scheduled = [it[0] for it in rs.items() if it[1][1] == False]
        if not locked and not scheduled:
            break
        print "Awaiting: locked %s; sheduled %s" % (locked, scheduled)
        sleep(delay)

def run_workload(hosts, db, workload, target = None):
    """
    Starts running of the workload.
    Note: we cannot use ycsb.workload, because it is decorated
    """
    database = get_db(db)
    load = get_workload(workload)
    the_time = base_time()
    def inner_run_workload():
        with cd(database['home']):
            param = int(target) / len(hosts) if target is not None else None
            # command = prepare_ycsbruncmd(database, load, the_time, param)
            command = _at(prepare_ycsbruncmd(database, load, the_time, param), the_time)
            run(command)
    with almost_nothing():
        tasks.execute(inner_run_workload, hosts=hosts)
    return the_time

def run_test_series(db, workload, seq):
    """ This script takes a sequence of threshold values and executes tests """
    initialize(clients, db)
    for t in seq:
        t = None if t == 0 else t
        # wait until all the servers be ready
        infinite_wait(clients, db)
        # fab ycsb_run:db=aerospike,workload=A,target=200000
        the_time = run_workload(clients, db, workload, t)
        print "submit tests with threshold = %s on %s" % (t, the_time)
        # end of all
    disconnect_all()

if __name__ == "__main__":
    db = 'couchbase'
    workload = 'A'
    seq = map(lambda t: t * 1000, [1, 2, 4, 6, 8, 10, 15, 20, 25, 50, 75, 100, 125, 150, 175, 200, 0])
    run_test_series(db, workload, seq)
