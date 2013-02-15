#!/usr/bin/python

from __future__ import print_function
import os
import re

import sys

def avg(seq):
    return sum(seq) / float(len(seq))

def same(x): return x

def scale1k(x) : return x / 1000.0

def merge():
    """grab all *.out, extract statistics from there and merge into TSV file """
    throughput = {}
    update_latency = {}
    read_latency = {}
    items = filter(lambda x: str(x).endswith('.out'), os.listdir('.'))
    # gather stats from all files=items
    for item in items:
        with open(item) as f:
            for line in f:
                if line.startswith('[UPDATE]') or line.startswith('[READ]'):
                    items = line.split(',')
                    if len(items) == 4:
                        (op, timestamp, lat, thr) = items
                        timestamp = int(timestamp)
                        #if timestamp == 0:
                        #   print items
                        lat = float(lat) / 1000.0
                        thr = thr.strip().split(' ', 1)[0]
                        try:
                            thr = float(thr)
                        except ValueError:
                            #For "[UPDATE], 1575400, 16432.262857142858, 5250.0Reconnecting to the DB..." line
                            thr = float(re.search('\d+\.\d+', thr).group(0))
                        thr_stats = throughput.get(timestamp, 0)
                        thr_stats += thr
                        throughput[timestamp] = thr_stats
                        # default latensy 0 will not work properly
                        # hence this statement is totally wrong:
                        if (op == '[READ]'):
                            stats1 = read_latency.get(timestamp, [])
                            stats1.append(lat)
                            read_latency[timestamp] = stats1
                        elif (op == '[UPDATE]'):
                            stats2 = update_latency.get(timestamp, [])
                            stats2.append(lat)
                            update_latency[timestamp] = stats2
    #for (timestamp, thr) in OrderedDict(sorted(throughput.items(), key=lambda t: t[0])).items():
    if len(sys.argv) > 1:
        # filename passed, to filename
        with open(sys.argv[1], 'w') as f:
            flush_series(f, read_latency, update_latency, throughput)
    else:
        # to stdout
        flush_series(sys.stdout, read_latency, update_latency, throughput)

def avg_convert(the_dict):
    # post-processing for latencies goes here
    list1 = the_dict.items()
    list2 = [(x, avg(y)) for (x, y) in list1 if len(y) > 0]
    # remove empty elements
    list2.sort(key=lambda (x, y): x)
    # convert each (sub)list to average
    return list2


def flush_series(f, read_latency, update_latency, throughput):
    for t in avg_convert(read_latency):
        print(tab_str(t), file=f)
        # skip line to mark the end of the block
    print('', file=f)
    for t in avg_convert(update_latency):
        print(tab_str(t), file=f)
        # skip line to mark the end of the block
    print('', file=f)
    # sort for timeseries.draw
    thr_list = throughput.items()
    thr_list.sort(key=lambda (x, y): x)
    for t in thr_list:
        print(tab_str(t), file=f)

def tab_str(seq):
    return '\t'.join(map(str, seq))

if __name__=='__main__':
    merge()
