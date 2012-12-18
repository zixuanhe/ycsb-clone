import sys, os
sys.path.insert(0, os.path.abspath('..')) # hack

from fabric import tasks
from fabric.network import disconnect_all
from fabric.operations import run, put
from conf import hosts
from conf import workloads
from fabfile.helpers import almost_nothing
from datetime import timedelta
from re import search, compile
from fabric.context_managers import cd
from fabric.operations import run, put, sudo
from pytz import timezone
from fabfile.helpers import get_db, get_workload, _at, base_time, almost_nothing, get_outfilename, get_properties

# remote citrusleaf machines
tz = hosts.timezone
clients = hosts.env.roledefs['client']
# benchmark file name, it bothers the CPU and consumes time and energy
benchmark_script = 'execute.sh'

LOCAL = False
#LOCAL = True
if LOCAL:
    # local virtual machines
    hosts.env.user = 'vagrant'
    hosts.env.password = 'vagrant'
    tz = timezone('CET')
    clients = ['192.168.0.11', '192.168.0.12', '192.168.0.13', '192.168.0.14']
#    clients = ['192.168.8.108', '192.168.9.213', '192.168.8.41', '192.168.8.118']
#clients = [clients[0]]

def fo_base_time():
    base_time(tz = tz)

class AnAction:
    """ It is something to execute on the remote servers"""
    def __init__(self, hosts = clients, **kv):
        # remote hosts to be executed on
        self.hosts = clients
        # action to be executed
        self.action = kv['action'] or RemoteActionIdle(10)
        # remote hosts timezone
        self.timezone = kv['timezone'] or tz
        # delay AFTER submission
        self.delay = self.action.delay()

class RemoteAction:
    def delay_after(self):
        pass

class RemoteRun(RemoteAction):
    def __init__(self, db, wl, target = None):
        self.db = db
        self.wl = wl
        self.target = target
    def delay_after(self):
        """ Returns estimated delay (run time) for the test with parameter t.
        In seconds """
        opc = workloads.data['operationcount']
        # redefine operation count if the workload hath
        workload = get_workload(self.wl)
        if 'properties' in workload:
            if 'operationcount' in workload['properties']:
                opc = long(workload['properties']['operationcount'])
        t = opc if self.target is None else self.target
        d = int((opc / t) * 1.1)
        return timedelta(seconds = d)

class RemoteIdle(RemoteAction):
    def __init__(self, d):
        self.d = d
    def delay_after(self):
        return timedelta(seconds = self.d)

def prepare_ycsbruncmd(the_hosts, dir_name, database, workload, the_time, target):
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
            par += ' -p %s=%s' % (key, int(value) / len(the_hosts))
        else:
            par += ' -p %s=%s' % (key, value)
    if target is not None:
        par += ' -target %s' % str(target)
        # parameters are constructed
    outfile = get_outfilename(database['name'], workload['name'], 'out', the_time, target)
    errfile = get_outfilename(database['name'], workload['name'], 'err', the_time, target)
    cmd = './%s %s' % (benchmark_script, par)
    cmd += ' > %s/%s' % (dir_name, outfile)
    cmd += ' 2> %s/%s' % (dir_name, errfile)
    return cmd

def initialize(the_hosts, db):
    """
    Prepares hosts to run the series
    """
    database = get_db(db)
    db_home = database['home']
    pf = compile('^%s' % database['name'])
    pn = compile('(\d+)/$')
    nos = [0]
    def inner_initialize_0():
    #    sudo('yum -y install at')
    #    sudo('service atd start')
    #    sudo('sudo yum install -y java-1.7.0-openjdk-devel')
    #    with cd('/opt'):
    #        put('../distribution/target/ycsb-0.1.4.tar.gz', '/run/shm/ycsb.tar.gz')
    #        sudo('rm -r ycsb-0.1.4')
    #        sudo('tar xzvf /run/shm/ycsb.tar.gz')
    #        sudo('ln -s /opt/ycsb-0.1.4 /opt/ycsb')
    #        print 'ycsb deployed'
        sudo('mkdir -p %s ; chmod 1777 %s' % (db_home, db_home))
        with cd(db_home):
            ls = run('ls --format=single-column --sort=t -d -- */').split('\r\n')
            # the most recent file satisfying pattern
            file_names = [f for f in ls if pf.search(f)]
            for file_name in file_names:
                mn = pn.search(file_name)
                if mn:
                    nos.append(int(mn.group(1)) + 1)
        # find the maximum number for all of the hosts
    with almost_nothing():
        tasks.execute(inner_initialize_0, hosts=the_hosts)
        # now form the dir name
    dir_name = os.path.join(database['home'], '%s_%02d' % (database['name'], max(nos)))
    def inner_initialize_1():
        run('mkdir %s ' % dir_name)
        series_dir = os.path.dirname(__file__)
        local_benchmark_script = os.path.join(series_dir, benchmark_script)
        if LOCAL:
            with cd(dir_name):
                run('rm -rf ./*')
                put(local_benchmark_script, benchmark_script, mode=0744)
            #                run('sed -i "s/\/opt\/ycsb\/bin\/ycsb \$\*/python nbody.py \$\*/g" %s' % benchmark_script)
        else:
            # if not LOCAL
            with cd(dir_name):
                put(local_benchmark_script, benchmark_script, mode=0744)

        # continue init
        # clear all the tasks that submitted so far
        with cd(dir_name):
            tasks = run('atq').split('\r\n')
            tid = []
            for task in tasks:
                m = search('^(\d+)\t', task)
                if m:
                    tid.append(m.group(1))
            run('atrm %s' % ' '.join(tid))
            print 'host %s initialized ' % hosts.env.host
    with almost_nothing():
        tasks.execute(inner_initialize_1, hosts=the_hosts)
    return dir_name

def submit_workload(the_hosts, dir_name, db, workload, the_time, target = None):
    """
    Schedules the workload.
    Note: we cannot use ycsb.workload, because it is decorated
    """
    database = get_db(db)
    load = get_workload(workload)
    def inner_submit_workload():
        with cd(dir_name):
            param = int(target) / len(the_hosts) if target is not None else None
            # command = prepare_ycsbruncmd(database, load, the_time, param)
            command = _at(prepare_ycsbruncmd(the_hosts, dir_name, database, load, the_time, param), the_time)
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
    dir_name = initialize(clients, db)
    the_time = base_time(tz = tz)
    for (wl, t) in seq:
        t = t if t > 0 else None
        # submit the task
        submit_workload(clients, dir_name, db, wl, the_time, t)
        print "submitted on %s with threshold = %s" % (the_time, t)
        if LOCAL:
            the_time += timedelta(minutes = 1)
        else:
            the_time += delay(wl, t)
            the_time = base_time(the_time, tz = tz) # round the time up
        # end of all
    disconnect_all()


def init(*srv):
    def inner_init():
        put('at_test.sh', 'at_test.sh', mode=0755)
    with almost_nothing():
        tasks.execute(inner_init, hosts=map(lambda x: x.ip, srv))

def finit():
    disconnect_all()

def ip(s):
    return s.ip

def global_start(*srv):
    def inner():
        run('echo start')
    with almost_nothing():
        tasks.execute(inner, hosts=map(ip, list(srv)))
def global_stop(*srv):
    def inner():
        run('echo stop')
    with almost_nothing():
        tasks.execute(inner, hosts=map(ip, list(srv)))
def global_latency(delay, *srv):
    def inner():
        run('echo latency %s' % delay)
    with almost_nothing():
        tasks.execute(inner, delay, hosts=map(ip, list(srv)))
def global_block(*srv):
    def inner():
        run('echo start')
    with almost_nothing():
        tasks.execute(inner, hosts=map(ip, list(srv)))
def global_unblock(*srv):
    def inner():
        run('echo unblock')
    with almost_nothing():
        tasks.execute(inner, hosts=map(ip, list(srv)))

class Server:
    def __init__(self, ip):
        self.ip = ip
    def start(self):
        global_start(self)
    def stop(self):
        global_stop(self)
    def latency(self, delay):
        global_latency(delay, self)
    def block(self):
        global_block(self)
    def unblock(self):
        global_unblock(self)

#t0 = datetime(2012,11,28,2,22,29,1234)
#t1 = datetime(2012,11,28,2,22,31,1234)
#print base_time(t0)
#print base_time(t1)
(s1,s2,s3,s4) = map(Server, hosts.env.roledefs['client'])

init(s1, s2, s3, s4)

#_begin(s1, s2)

s1.start()
s2.start()
s1.latency(1000)
s1.latency(0)
s1.stop()
s2.stop()

finit()

