root = '/opt/ycsb'

data = {
    'recordcount': 500000000,
    'fieldcount': 10,
    'fieldlength': 10,
    'fieldnameprefix': 'f',
    'operationcount': 10000000,
    'threadcount': 32,
    'workload': 'com.yahoo.ycsb.workloads.CoreWorkload',
    'exportmeasurementsinterval': 30000,
    #'readretrycount': 2,
    #'updateretrycount': 2,
}

workloads = {
    'A': {
        'name': 'workloada',
        'propertyfiles': [ root + '/workloads/workloada' ],
    },
    'B': {
        'name': 'workloadb',
        'propertyfiles': [ root + '/workloads/workloadb' ],
    }
}
