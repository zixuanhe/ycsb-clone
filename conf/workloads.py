root = '/opt/ycsb'

data = {
    'recordcount': 2000000000,
    'fieldcount': 10,
    'fieldlength': 10,
    'operationscount': 10000000,
    'threadcount': 16,
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
