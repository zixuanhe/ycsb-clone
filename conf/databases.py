import hosts

databases = {

    'aerospike' : {
        'name': 'aerospike',
        'home': '/dev/shm',
        'command': 'aerospike',
        'properties': {
            'host': 'r1.citrusleaf.local',
            'port': 3000,
            'ns': 'test',
            'set': 'YCSB',
        },
        'status': {
            'hosts': hosts.env.roledefs['server'][0:1],
            'command': '/opt/citrusleaf/bin/clmonitor -e info'
        }
    },

    'couchbase' : {
        'name': 'couchbase',
        'home': '/dev/shm',
        'command': 'couchbase',
        'properties': {
            'couchbase.hosts': 'r1.citrusleaf.local,r2.citrusleaf.local,r3.citrusleaf.local,r4.citrusleaf.local',
            'couchbase.bucket': 'test',
            'couchbase.user': '',
            'couchbase.password': '',
            'couchbase.opTimeout': 60000,
            #'couchbase.failureMode': 'Retry',
            'couchbase.checkOperationStatus': 'true',
        }
    },

    'cassandra' : {
        'name': 'cassandra',
        'home': '/dev/shm',
        'command': 'cassandra-10',
        'properties': {
            'hosts': 'r1.citrusleaf.local,r2.citrusleaf.local,r3.citrusleaf.local,r4.citrusleaf.local',
        }
    },

    'mongodb' : {
        'name': 'mongodb',
        'home': '/dev/shm',
        'command': 'mongodb',
        'properties': {
            'mongodb.url': 'mongodb://localhost:27017',
            'mongodb.database': 'ycsb',
            'mongodb.writeConcern': 'normal',
            'mongodb.readPreference': 'primaryPreferred',
        }
    },

    'basic' : {
        'name': 'basic',
        'home': '/dev/shm',
        'command': 'basic',
        'properties': {
            'basicdb.verbose': 'false',
        }
    },

}
