#!/usr/bin/python
import sys, os
sys.path.insert(0, os.path.abspath('..')) # ugly hack to allow import from the root
from fabfile.failover import clients, servers, AT, Launcher


#########################
c1, c2, c3, c4 = clients
#e1, e2, e3, e4 = servers
e1 = servers

db = 'basic'
wl = 'C'

at = AT(clients, db)

# run clients bombarding the servers with requests
t0 = at[0].client_run([c1, c2], db, wl)
# in 1 minute (=60 sec) the first server fails
at[60].server_kill([e1])
# in 2 minutes the server is up back
at[120].server_start([e1])

# test again, to verify if the previous failure influenced behavior
t1 = at[t0].client_run([c1, c2], db, wl)

at.fire()
