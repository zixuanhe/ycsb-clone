import hosts

databases = {

    'aerospike' : {
        'name': 'aerospike',    #name of the database (used to form the logfile name)
        'home': '/run/shm',     #database home, to put logs there
        'command': 'aerospike', #database name to pass to ycsb command
        'properties': {         #properties to pass to ycsb command as -p name=value
            'host': 'e1.citrusleaf.local',  #database connection params
            'port': 3000,
            'ns': 'test',
            'set': 'YCSB',
        },
        'status': {
            'hosts': hosts.env.roledefs['server'][0:1],     #hosts on which to run the status command
            'command': '/opt/citrusleaf/bin/clmonitor -e info'  #the status command
        }
    },

    'couchbase' : {
        'name': 'couchbase',
        'home': '/run/shm',
        'command': 'couchbase',
        'properties': {
            'couchbase.hosts': 'e1.citrusleaf.local,e2.citrusleaf.local,e3.citrusleaf.local,e4.citrusleaf.local',
            'couchbase.bucket': 'test',
            'couchbase.user': '',
            'couchbase.password': '',
            'couchbase.opTimeout': 60000,
            #'couchbase.failureMode': 'Retry',
            'couchbase.checkOperationStatus': 'true',
        }
    },

    'couchbase2' : {
        'name': 'couchbase',
        'home': '/run/shm',
        'command': 'couchbase2',
        'properties': {
            'couchbase.hosts': 'e2.citrusleaf.local',#,e1.citrusleaf.local,e3.citrusleaf.local,e4.citrusleaf.local',
            'couchbase.bucket': 'test',
            'couchbase.ddocs': '',
            'couchbase.views': '',
            'couchbase.user': '',
            'couchbase.password': '',
            'couchbase.opTimeout': 60000,
            #'couchbase.failureMode': 'Retry',
            #'couchbase.persistTo': 'ONE',
            #'couchbase.replicateTo': 'ONE',
            'couchbase.checkOperationStatus': 'true',
            },
        'failover': {
            'files': ['couchbase_kill.sh', 'couchbase_start.sh'],
            'kill_command': '''\
echo 'ssh e1 ~/couchbase_kill.sh' >> /run/shm/at.log; \
ssh e1 ~/couchbase_kill.sh >> /run/shm/at.log; \
sleep 1; \
echo '/opt/couchbase/bin/couchbase-cli failover' >> /run/shm/at.log; \
/opt/couchbase/bin/couchbase-cli failover -c localhost:8091 -u admin -p 123123 --server-failover=192.168.109.168 >> /run/shm/at.log; \
sleep 2; \
echo '/opt/couchbase/bin/couchbase-cli rebalance' >> /run/shm/at.log; \
/opt/couchbase/bin/couchbase-cli rebalance -c localhost:8091 -u admin -p 123123 >> /run/shm/at.log;''',

            'start_command': '''\
echo 'ssh e1 ~/couchbase_start.sh' >> /run/shm/at.log; \
ssh e1 ~/couchbase_start.sh >> /run/shm/at.log; \
sleep 7; \
echo '/opt/couchbase/bin/couchbase-cli server-add' >> /run/shm/at.log; \
/opt/couchbase/bin/couchbase-cli server-add -c localhost:8091 -u admin -p 123123 --server-add=192.168.109.168 --server-add-username=admin --server-add-password=123123 >> /run/shm/at.log; \
sleep 3; \
echo '/opt/couchbase/bin/couchbase-cli rebalance' >> /run/shm/at.log; \
/opt/couchbase/bin/couchbase-cli rebalance -c localhost:8091 -u admin -p 123123 >> /run/shm/at.log;''',
        }
    },

    'cassandra' : {
        'name': 'cassandra',
        'home': '/run/shm',
        'command': 'cassandra-10',
        'properties': {
            'hosts': 'e1.citrusleaf.local,e2.citrusleaf.local,e3.citrusleaf.local,e4.citrusleaf.local',
            'cassandra.readconsistencylevel': 'ONE',
            'cassandra.writeconsistencylevel': 'ONE',
        }
    },

    'mongodb' : {
        'name': 'mongodb',
        'home': '/run/shm',
        'command': 'mongodb',
        'properties': {
            'mongodb.url': 'mongodb://localhost:27018',
            'mongodb.database': 'ycsb',
            'mongodb.writeConcern': 'normal',
            #'mongodb.writeConcern': 'replicas_safe',
            'mongodb.readPreference': 'primaryPreferred',
        },
        'configdb': 'r5.citrusleaf.local',
    },

    'basic' : { #fake database
        'name': 'basic',
        'home': '/run/shm',
        'command': 'basic',
        'properties': {
            'basicdb.verbose': 'false',
        }
    },

}
