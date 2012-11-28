#!/usr/bin/python
from fabric import tasks
from fabric.colors import red
import time
from fabric.context_managers import hide, settings
from fabric.network import disconnect_all
from fabric.operations import run
from conf.hosts import env

env.user = 'vagrant'
env.password = 'vagrant'
#env.roledefs['client']\
servers = env.roledefs['server']
clients = ['192.168.8.108', '192.168.9.213', '192.168.8.41', '192.168.8.118']

def almost_nothing():
    return settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True)

def get_ready(srvs):
    # test if all servers srv are ready to run new test
    results = dict()
    def inner_check_ready():
        # if the file do exist, then the host is NOT ready => False
        results[env.host] = bool(run('[ -f at_test.sh ]').return_code)
    with almost_nothing():
        tasks.execute(inner_check_ready, hosts=srvs)
    # returns a map from hosts to True or False
    # True means the server is ready
    return results


def infinite_wait():
    """wait until all the servers be ready"""
    while True:
        rs = get_ready(clients)
        if all(rs.values()):
            break
        ns = [x[0] for x in rs.items() if x[1] == False]
        print "Awaiting for %s" % ns
        time.sleep(10)


def run_test_series(seq):
    """ This script takes a sequence of threshold values and executes tests """
    for e in seq:
        # wait until all the servers be ready
        infinite_wait()
        print "now run the test with threshold = %s" % e

    # end of all
    disconnect_all()

if __name__ == "__main__":
    run_test_series(map(lambda x: x*1000,
        [1, 2, 4, 6, 8, 10, 15, 20, 25, 50, 75, 100, 125, 150, 175, 200, 10e6]))

