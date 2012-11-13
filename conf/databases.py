databases = {

    'aerospike' : {
        'name': 'aerospike',
        'home': '/home/aerospike',
        'command': 'aerospike',
        'properties': {
            'host': 'r1.citrusleaf.local',
            'port': 3000,
            'ns': 'test',
            'set': 'YCSB',
        }
    },

    'couchbase' : {
        'name': 'couchbase',
        'home': '/home/couchbase',
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
        'home': '/home/cassandra',
        'command': 'cassandra-10',
        'properties': {
            'hosts': 'r1.citrusleaf.local,r2.citrusleaf.local,r3.citrusleaf.local,r4.citrusleaf.local',
        }
    },

    'mongodb' : {
        'name': 'mongodb',
        'home': '/home/mongo',
        'command': 'mongodb',
        'properties': {
            'mongodb.url': 'mongodb://localhost:27017',
            'mongodb.database': 'ycsb',
            'mongodb.writeConcern': 'normal',
            'mongodb.readPreference': 'primaryPreferred',
        }
    },

}
