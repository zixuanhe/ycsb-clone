#!/usr/bin/python

import os
import re

from UserDict import DictMixin

class OrderedDict(dict, DictMixin):

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__end
        except AttributeError:
            self.clear()
        self.update(*args, **kwds)

    def clear(self):
        self.__end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.__map = {}                 # key --> [key, prev, next]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            end = self.__end
            curr = end[1]
            curr[2] = end[1] = self.__map[key] = [key, curr, end]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        key, prev, next = self.__map.pop(key)
        prev[2] = next
        next[1] = prev

    def __iter__(self):
        end = self.__end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.__end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        if last:
            key = reversed(self).next()
        else:
            key = iter(self).next()
        value = self.pop(key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__end
        del self.__map, self.__end
        inst_dict = vars(self).copy()
        self.__map, self.__end = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def keys(self):
        return list(self)

    setdefault = DictMixin.setdefault
    update = DictMixin.update
    pop = DictMixin.pop
    values = DictMixin.values
    items = DictMixin.items
    iterkeys = DictMixin.iterkeys
    itervalues = DictMixin.itervalues
    iteritems = DictMixin.iteritems

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            if len(self) != len(other):
                return False
            for p, q in  zip(self.items(), other.items()):
                if p != q:
                    return False
            return True
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other

# special wrapper over dict to get rid of
# silly defensive ifs like
#    oc = ... # operation code
#    if not(oc in stats):
#        stats[oc] = {}
#    if not(mt in stats[oc]):
#        stats[oc][mt] = {}
#    # now it is safe to access
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
    fold_functions = OrderedDict()
    # each string is inherently a regex, and those regexes should be mutually
    # exclusive. The order of putting items in fold_functions defines the order
    # of columns
    fold_functions['RunTime']               = max
    fold_functions['Throughput']            = sum
    fold_functions['Operations']            = sum
    fold_functions['Retries']               = sum
    fold_functions['AverageLatency']        = avg
    fold_functions['MinLatency']            = min
    fold_functions['MaxLatency']            = max
    fold_functions['95thPercentileLatency'] = max
    fold_functions['99thPercentileLatency'] = max
    fold_functions['Return=0']              = sum
    fold_functions['Return=[^0].*']         = sum
    metrics = fold_functions.keys()
    regexps = map(re.compile, metrics)
    cns = []
    # trying each regexp for each line is TERRIBLY slow, therefore
    # we need to obtain searchable prefix to make preprocessing
    prefixes = map(lambda mt: str(re.search('\w+', mt).group(0)), metrics)
    # other stuff
    stats = NestedDict()
    items = filter(lambda x: str(x).endswith('.out'), os.listdir('.'))
    pcn = re.compile(r'.*?-c(\d)\.out')
    pln = re.compile(r'\[(\w+)\], (.*?), (\d+(\.\d+)?)')
    # gather stats from all files=items
    for item in items:
        with open(item) as file:
            m0 = pcn.search(item)
            if m0:
                cn = m0.group(1)
                cns.append(cn)
                for line in file:
                    for i in range(len(prefixes)):
                        pr = prefixes[i]
                        if pr in line:
                            m1 = (regexps[i]).search(line)
                            m2 = pln.search(line)
                            if m1 and m2:
                                oc = m2.group(1) # operation code
                                # cl = m2.group(2) # column
                                mt = metrics[i]
                                if stats[oc][mt][cn]:
                                    stats[oc][mt][cn] += float(m2.group(3))
                                else:
                                    stats[oc][mt][cn] = float(m2.group(3))
    cns.sort()
    # stats is the dictionary like this:
    #OVERALL RunTime {'1': 1500.0, '3': 2295.0, '2': 1558.0, '4': 2279.0}
    # ...
    #UPDATE Return=1 {'1': 477.0, '3': 488.0, '2': 514.0, '4': 522.0}
    headers1 = ['']
    headers2 = ['']
    # operations are sorted in the [OVERALL, READ, UPDATE] order
    for oc, ostats in sorted(stats.items()):
        keys = sorted(ostats.keys(), key=metrics.index)
        for mt in keys:
            headers1.append(oc) # operation code like OVERALL, READ, UPDATE
            headers2.append(mt) # metric name like RunTime, AverageLatency etc
    print(tab_str(headers1))
    print(tab_str(headers2))
    # write the values for each client
    for cn in cns:
        row = [str(cn)]
        for oc, ostats in sorted(stats.items()):
            # oc is the operation code oc = 'OVERALL'
            keys = sorted(ostats.keys(), key=metrics.index)
            for mt in keys:
                row.append(ostats[mt][str(cn)])
        print(tab_str(row))
        # now write the totals
    row = ['Total']
    for oc, ostats in sorted(stats.items()):
        # oc is the operation code oc = 'OVERALL'
        keys = sorted(ostats.keys(), key=metrics.index)
        for mt in keys:
            row.append(fold_functions[mt](ostats[mt].values()))
    print(tab_str(row))

if __name__=='__main__':
    merge()
