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
            'couchbase.hosts': 'e1.citrusleaf.local,e2.citrusleaf.local,e3.citrusleaf.local,e4.citrusleaf.local',
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
            'kill_command': '/etc/init.d/couchbase-server stop',
            'start_command': '/etc/init.d/couchbase-server start',
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
