root = '/opt/ycsb'

data = {
    'recordcount': 2000000000,
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
