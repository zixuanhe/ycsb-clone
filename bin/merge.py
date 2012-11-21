#!/usr/bin/python

import os
import re

# special wrapper over dict to get rid of
# silly defensive ifs like
#    oc = ... # operation code
#    if not(oc in stats):
#        stats[oc] = {}
#    if not(mt in stats[oc]):
#        stats[oc][mt] = {}
#        # now it is safe to access
#    stats[oc][mt][cn] = float(m1.group(3))
class NestedDict(dict):
    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, NestedDict())

def avg(seq):
    return sum(seq) / float(len(seq))

def tab_str(seq):
    return '\t'.join(map(str, seq))

def merge():
    """grab all *.out, extract statistics from there and merge into TSV file """
    fold_functions = {
        'Operations'     : sum,
        'RunTime'        : sum,
        'Throughput'     : avg,
        'AverageLatency' : avg,
        'MinLatency'     : min,
        'MaxLatency'     : max,
        '95thPercentileLatency' : max,
        '99thPercentileLatency' : max,
        'Return'         : sum
    };
    metrics = fold_functions.keys()
    cns = []
    stats = NestedDict()
    items = filter(lambda x: str(x).endswith('.out'), os.listdir('.'))
#    items = call(['ls --format=single-column *.out'],  shell=True).split("\n")
    pcn = re.compile(r'.*?-c(\d)\.out')
    pln = re.compile(r'\[(\w+)\], (.*?), (\d+)')
    # gather stats from all files=items
    for item in items:
        with open(item) as file:
            m0 = pcn.search(item)
            if m0:
                cn = m0.group(1)
                cns.append(cn)
                for line in file:
                    for mt in metrics:
                        if mt in line:
                            m1 = pln.search(line)
                            if m1:
                                oc = m1.group(1) # operation code
                                stats[oc][mt][cn] = float(m1.group(3))
    cns.sort()
    # stats is the dictionary like this:
    #OVERALL RunTime {'1': 1500.0, '3': 2295.0, '2': 1558.0, '4': 2279.0}
    # ...
    #UPDATE Return=1 {'1': 477.0, '3': 488.0, '2': 514.0, '4': 522.0}
    headers1 = ['']
    headers2 = ['']
    for oc, ostats in sorted(stats.items()):
        for mt in sorted(ostats.keys()):
            headers1.append(oc)
            headers2.append(mt)
    print(tab_str(headers1))
    print(tab_str(headers2))
    # write the values for each client
    for cn in cns:
        row = [str(cn)]
        for oc, ostats in sorted(stats.items()):
            # oc is the operation code oc = 'OVERALL'
            for mt, cstats in sorted(ostats.items()):
                row.append(cstats[str(cn)])
        print(tab_str(row))
        # now write the totals
    row = ['Total']
    for oc, ostats in sorted(stats.items()):
        # oc is the operation code oc = 'OVERALL'
        for mt, cstats in sorted(ostats.items()):
            row.append(fold_functions[mt](cstats.values()))
    print(tab_str(row))

if __name__=='__main__':
    merge()
