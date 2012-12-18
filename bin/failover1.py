#!/usr/bin/python
import sys, os
sys.path.insert(0, os.path.abspath('..')) # ugly hack to allow import from the root
from fabfile.failover import run_test_series, clients, RemoteRun, RemoteIdle
from fabfile.helpers import base_time

class Seq:
    def __init__(self, host):
        self.host = host
        self.seq = []
        self.t = base_time()
    def append(self, e):
        self.seq.append(e)
        self.t += e.delay_after()
        return self

db = 'basic'
wl = 'C'
def run(target):
    return RemoteRun(db, wl, target * 1000)
def idle(prev):
    return RemoteIdle(prev.delay_after())

server1 = Seq(clients[0])
server1.append(run(10))
#server1.append(idle(???))




class RunParams():
    def __init__(self, db_name, home_path, wl_name):
        self.db_name = db_name
        self.wl_name = wl_name
        self.home_path = home_path
