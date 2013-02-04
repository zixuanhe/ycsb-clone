#!/usr/bin/python
from datetime import timedelta
import sys, os
import pytz

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) # ugly hack to allow import from the root
from fabfile.failover import clients, servers, AT


#########################
db = 'couchbase2'
wl = 'A'
e2 = servers[1]

at = AT(clients, db)
# start workload
#at[0].client_run(clients, db, wl, 250000)
# kill server
#at[600].server_kill([e1], db)
at[60].server_kill([e2], db)
#TODO do the manual node failover for the same time for Couchbase
# the server is up back
#at[1200].server_start([e1], db)
at[120].server_start([e2], db)

at.fire()
