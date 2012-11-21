root = '/opt/ycsb'

data = {
    #'recordcount': 500000000,  #SSD
    'recordcount': 50000000,    #RAM
    'fieldcount': 10,
    'fieldlength': 10,
    'fieldnameprefix': 'f',
    'operationcount': 10000000,
    'threadcount': 32,
    'workload': 'com.yahoo.ycsb.workloads.CoreWorkload',
    'exportmeasurementsinterval': 30000,
    #'readretrycount': 1,
    #'updateretrycount': 1,
    #'readallfields': 'false',
    #'writeallfields': 'false',
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
