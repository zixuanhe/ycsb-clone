#!/usr/bin/python
from fabric import tasks
from time import sleep
from fabric.context_managers import hide, settings, cd
from fabric.network import disconnect_all
from fabric.operations import run, put
from conf.hosts import env
from fabfile.helpers import get_db, get_workload, _at, base_time, almost_nothing, get_outfilename
from fabfile.ycsb import totalclients

env.user = 'vagrant'
env.password = 'vagrant'
#servers = env.roledefs['server']
#clients = ['192.168.0.11', '192.168.0.12', '192.168.0.13', '192.168.0.14']
clients = ['192.168.8.108', '192.168.9.213', '192.168.8.41', '192.168.8.118']
# lock file name, it shows that the test is still running
lock = 'run_workload.lock'
# benchmark file name, it loads the CPU to consume time
benchmark = 'n-body.py'

def prepare_ycsbruncmd(database, workload, the_time, target=None):
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
    cmd += ' && ./' + benchmark
    outfile = get_outfilename(database['name'], workload['name'], 'out', the_time, target)
    errfile = get_outfilename(database['name'], workload['name'], 'err', the_time, target)
    cmd += ' > %s/%s' % (database['home'], outfile)
    cmd += ' 2> %s/%s' % (database['home'], errfile)
    cmd += ' && rm -f %s' % lock
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
    database = get_db(db)
    rs = dict()
    def inner_poll_hosts():
        with cd(database['home']):
            # if the file do exist, then the host is NOT ready => False
            # returns a map from hosts to True or False
            rs[env.host] = bool(run('[ -f %s ]' % lock).return_code)
    with almost_nothing():
        tasks.execute(inner_poll_hosts, hosts=hosts)
    return rs

def infinite_wait(hosts, db, delay = 10):
    """
    Waits until all the servers become ready, delay in seconds
    """
    while True:
        # test if all servers srv are ready to run new test
        # True means the server is ready
        rs = poll_hosts(hosts, db)
        if all(rs.values()):
            break
        ns = [x[0] for x in rs.items() if x[1] == False]
        print "Awaiting for %s" % ns
        sleep(delay)

def run_workload(hosts, db, workload, target=None):
    """
    Starts running of the workload.
    Note: we cannot use ycsb.workload, because it is decorated
    """
    database = get_db(db)
    load = get_workload(workload)
    the_time = base_time()
    def inner_run_workload():
        with cd(database['home']):
            param = int(target) / totalclients if target is not None else None
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
        # wait until all the servers be ready
        infinite_wait(clients, db)
        # fab ycsb_run:db=aerospike,workload=A,target=200000
        the_time = run_workload(clients, db, workload, t)
        print "submit tests with threshold = %s on %s" % (t, the_time)
        # end of all
    disconnect_all()

if __name__ == "__main__":
    db = 'couchbase'
    workload='A'
    seq = map(lambda x: x*1000, [1, 2, 4, 6, 8, 10, 15, 20, 25, 50, 75, 100, 125, 150, 175, 200, 10e6])
    run_test_series(db, workload, seq)
