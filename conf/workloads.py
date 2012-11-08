root = '/opt/ycsb'

data = {
    'recordcount': 2000000000,
    'operationscount': 10000000,
}

workloads = {
    'A': {
        'propertyfiles': [ root + '/workloads/workloada' ],
        'resultprefix': 'workloada'
    },
    'B': {
        'propertyfiles': [ root + '/workloads/workloadb' ],
        'resultprefix': 'workloada'
    }
}
