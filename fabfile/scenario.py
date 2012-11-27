from fabric import tasks
from datetime import datetime, timedelta
from fabric.colors import green
from fabric.context_managers import settings, hide
from fabric.network import disconnect_all
from fabric.operations import run, put
from conf import hosts
from conf.hosts import env

# the scenario to execute and stop servers remotely
# and control network on those machines to simulate splits,
# delays and packet losses
env.user = 'vagrant'
env.password = 'vagrant'
servers = hosts.env.roledefs['server']

def base_time(time=None, round_sec=60, tz = hosts.timezone):
    """
    Get the next timestamp rounded to round_sec seconds
    the function returns some future time rounded accordingly
    to round_sec parameter.
    Examples: 2:22:29 -> 2:23:00
              2:22:31 -> 2:24:00
    """
    if time is None: time = datetime.now(tz)
    seconds = (time - time.min).seconds
    rounding = (seconds + round_sec * 1.5) // round_sec * round_sec
    return time + timedelta(0, rounding-seconds, -time.microsecond)

def init(*srv):
    def inner_init():
        with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
            put('at_test.sh', 'at_test.sh', mode=0755)
    tasks.execute(inner_init, hosts=servers)

def finit(*srv):
    disconnect_all()


def start(*srv):
    with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
        run('echo start')
def stop(*srv):
    with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
        run('echo stop')
def latency(delay, *srv):
    with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
        run('echo latency %s' % delay)
        print green(delay)
def block(*srv):
    with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
        run('echo start')
def unblock(*srv):
    with settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True):
        run('echo start')

class Server:
    def __init__(self, ip):
        self.ip = ip
    def start(self):
        tasks.execute(start, hosts=[self.ip])
    def stop(self):
        tasks.execute(stop, hosts=[self.ip])
    def latency(self, delay):
        tasks.execute(latency, delay, hosts=[self.ip])
    def block(self):
        tasks.execute(block, hosts=[self.ip])
    def unblock(self):
        tasks.execute(unblock, hosts=[self.ip])

#t0 = datetime(2012,11,28,2,22,29,1234)
#t1 = datetime(2012,11,28,2,22,31,1234)
#print base_time(t0)
#print base_time(t1)
(s1,s2) = map(Server, servers)

init(s1, s2)

#_begin(s1, s2)

s1.start()
s2.start()
s1.latency(1000)
s1.latency(0)
s1.stop()
s2.stop()

finit(s1, s2)

