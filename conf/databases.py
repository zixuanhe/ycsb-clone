import hosts

databases = {

    'aerospike' : {
        'name': 'aerospike',
        'home': '/run/shm',
        'command': 'aerospike',
        'properties': {
            'host': 'e1.citrusleaf.local',
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

    'cassandra' : {
        'name': 'cassandra',
        'home': '/run/shm',
        'command': 'cassandra-10',
        'properties': {
            'hosts': 'e1.citrusleaf.local,e2.citrusleaf.local,e3.citrusleaf.local,e4.citrusleaf.local',
        }
    },

    'mongodb' : {
        'name': 'mongodb',
        'home': '/run/shm',
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
        'home': '/run/shm',
        'command': 'basic',
        'properties': {
            'basicdb.verbose': 'true',
        }
    },

}
