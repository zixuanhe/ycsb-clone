#!/usr/bin/python

import os
import re

from merge import OrderedDict

def avg(seq):
    return sum(seq) / float(len(seq))

def same(x): return x

def scale1k(x) : return x / 1000.0

def merge():
    """grab all *.out, extract statistics from there and merge into TSV file """
    throughput = OrderedDict()
    update_latency = {}
    read_latency = {}
    items = filter(lambda x: str(x).endswith('.out'), os.listdir('.'))
    # gather stats from all files=items
    for item in items:
        with open(item) as file:
            for line in file:
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
                        thr_stats = throughput.get(timestamp)
                            
                        #TODO latency stats
                        if not thr_stats:
                            thr_stats = 0
                        thr_stats += thr
                        throughput[timestamp] = thr_stats
    #for (timestamp, thr) in OrderedDict(sorted(throughput.items(), key=lambda t: t[0])).items():
    for (timestamp, thr) in throughput.items():             
        print(tab_str((timestamp, thr)))

def tab_str(seq):
    return '\t'.join(map(str, seq))

if __name__=='__main__':
    merge()
