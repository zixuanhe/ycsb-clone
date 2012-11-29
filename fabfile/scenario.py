from fabric import tasks
from fabric.network import disconnect_all
from fabric.operations import run, put
from conf import hosts
from conf.hosts import env

# the scenario to execute and stop servers remotely
# and control network on those machines to simulate splits,
# delays and packet losses
from fabfile.helpers import almost_nothing

env.user = 'vagrant'
env.password = 'vagrant'

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

