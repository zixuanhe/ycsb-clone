#!/usr/bin/python
from datetime import timedelta
import re
from fabric import tasks
from fabric.context_managers import cd
from fabric.network import disconnect_all
from fabric.operations import run, put
import pytz
from conf import workloads, hosts
from fabfile.helpers import get_db, get_workload, _at, base_time, almost_nothing, get_outfilename, get_properties

LOCAL = False
#LOCAL = True
if LOCAL:
    # local virtual machines
    hosts.env.user = 'vagrant'
    hosts.env.password = 'vagrant'
    timezone = pytz.timezone('CET')
    clients = ['192.168.8.108', '192.168.9.213', '192.168.8.41', '192.168.8.118']
else:
    # remote citrusleaf machines
    timezone = hosts.timezone
    clients = hosts.env.roledefs['client']

#clients = [clients[0]]

# benchmark file name, it bothers the CPU and consumes time and energy
benchmark = 'execute.sh'

def prepare_ycsbruncmd(thd_hosts, database, workload, the_time, target):
    # /opt/ycsb/bin/ycsb run couchbase ... -target 25000
    # and we assign
    # $1 -> run couchbase -s -P /opt/ycsb/workloads/workloada -p couchbase.user= -p couchbase.bucket=test -p couchbase.opTimeout=60000 -p couchbase.checkOperationStatus=true -p couchbase.password= -p couchbase.hosts=e1.citrusleaf.local,e2.citrusleaf.local,e3.citrusleaf.local,e4.citrusleaf.local -p fieldnameprefix=f -p recordcount=50000000 -p fieldcount=10 -p retrydelay=1 -p threadcount=32 -p readretrycount=1000 -p fieldlength=10 -p exportmeasurementsinterval=30000 -p workload=com.yahoo.ycsb.workloads.CoreWorkload -p updateretrycount=1000 -p insertretrycount=1000000 -p warmupexecutiontime=60000 -p operationcount=2500000
    # $2 -> -target 25000
    # $2 could be empty
    par = '' # /opt/ycsb/bin/ycsb is hardcoded in the benchmark file
    par += ' run %s -s' % database['command']
    for file in workload['propertyfiles']:
        par += ' -P %s' % file
    for (key, value) in get_properties(database, workload).items():
        par += ' -p %s=%s' % (key, value)
    for (key, value) in workloads.data.items():
        if key == 'operationcount':
            par += ' -p %s=%s' % (key, int(value) / len(thd_hosts))
        else:
            par += ' -p %s=%s' % (key, value)
    if target is not None:
        par += ' -target %s' % str(target)
    # parameters are constructed
    outfile = get_outfilename(database['name'], workload['name'], 'out', the_time, target)
    errfile = get_outfilename(database['name'], workload['name'], 'err', the_time, target)
    cmd = './%s %s' % (benchmark, par)
    cmd += ' > %s/%s' % (database['home'], outfile)
    cmd += ' 2> %s/%s' % (database['home'], errfile)
    return cmd

def initialize(the_hosts, db):
    """
    Prepares hosts to run the series
    """
    database = get_db(db)
    def inner_initialize():
        with cd(database['home']):
            if LOCAL:
                run('rm -rf ./*')
                put(benchmark, benchmark, mode=0744)
                put('nbody.py', 'nbody.py')
                run('sed -i "s/\/opt\/ycsb\/bin\/ycsb \$\*/python nbody.py \$\*/g" %s' % benchmark)
                # put('nbody.java', 'nbody.java')
                # run('javac nbody.java')
                # clear all the tasks that submitted so far
            else:
                put(benchmark, benchmark, mode=0744)
            tasks = run('atq').split('\r\n')
            tid = []
            for task in tasks:
                m = re.search('^(\d+)\t', task)
                if m:
                    tid.append(m.group(1))
            run('atrm %s' % ' '.join(tid))
            print 'host %s initialized ' % hosts.env.host
    with almost_nothing():
        tasks.execute(inner_initialize, hosts=the_hosts)

def submit_workload(the_hosts, db, workload, the_time, target = None):
    """
    Schedules the workload.
    Note: we cannot use ycsb.workload, because it is decorated
    """
    database = get_db(db)
    load = get_workload(workload)
    def inner_submit_workload():
        with cd(database['home']):
            param = int(target) / len(the_hosts) if target is not None else None
            # command = prepare_ycsbruncmd(database, load, the_time, param)
            command = _at(prepare_ycsbruncmd(the_hosts, database, load, the_time, param), the_time)
            run(command)

    with almost_nothing():
        tasks.execute(inner_submit_workload, hosts=the_hosts)

def delay(wl, t):
    """ Returns estimated delay (run time) for the test with parameter t.
    In seconds """
    opc = workloads.data['operationcount']
    # redefine operation count if the workload hath
    workload = get_workload(wl)
    if 'properties' in workload:
        if 'operationcount' in workload['properties']:
            opc = long(workload['properties']['operationcount'])
    t = opc if t is None else t
    d = int((opc / t) * 1.1)
    return timedelta(seconds = d)

def run_test_series(db, seq):
    """ This script takes a sequence of threshold values and executes tests """
    initialize(clients, db)
    the_time = base_time(tz = timezone)
    for (wl, t) in seq:
        t = t if t > 0 else None
        # submit the task
        submit_workload(clients, db, wl, the_time, t)
        print "submitted on %s with threshold = %s" % (the_time, t)
        if LOCAL:
            the_time += timedelta(minutes = 1)
        else:
            the_time += delay(wl, t)
            the_time = base_time(the_time, tz = timezone) # round the time up
    # end of all
    disconnect_all()

if __name__ == "__main__":
    db = 'basic'       # hardcoded
    # db = sys.argv[1] # from command line
    times = map(lambda t: t * 1000, [100, 200, 0]) # 0 means infinity
    # alternate 'A' and 'C' workloads, flatten them
    seq = []
    for d in map(lambda t: [('C', t), ('A', t)], times):
        seq.extend(d)
    print ('seq = %s' % seq)
    run_test_series(db, seq)
