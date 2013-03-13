#!/usr/bin/python

import csv

class Interval:

    def __init__(self, begin, end, threshold = 0):
        self.begin = begin
        self.end = end
        self.threshold = threshold
        self.sum = 0
        self.count = 0
        self.completed = False

    def add(self, time, value):
        self._completed(time)
        if self._in(time) and self._above(value):
            self.sum += value
            self.count += 1

    def _in(self, time):
        return time >= self.begin and time <= self.end

    def _above(self, value):
        return value > self.threshold

    def _completed(self, time):
        if time > self.end:
            self.completed = True

    def average(self):
        if self.count == 0:
            return 0
        return self.sum / self.count

join_time = 600000

try:
    with open('stats.conf') as csvfile:
        stats_reader = csv.reader(csvfile, delimiter='=')
        for row in stats_reader:
            if row[0] == 'join to cluster':
                join_time = int(row[1])
except:
    pass

print "join time: %i" % (join_time)

intervals = [
    [
        Interval(1000, 500000),     #initial read
        Interval(500000, 700000),   #read on node down
        Interval(join_time - 100000, join_time + 100000),   #read on node join
    ],
    [
        Interval(1000, 500000),     #initial write
        Interval(500000, 700000),   #write on node down
        Interval(join_time - 100000, join_time + 100000),   #write on node join
    ]
]

print "between %i and %i" % (begin, end)

print "averaging over %f" % (threshold)

results = []
index = 0
results.append([])

with open('series.txt') as csvfile:
    series_reader = csv.reader(csvfile, delimiter="\t")
    for values in series_reader:
        if len(values) == 2:
            if not values[0].isdigit():
                continue
            time = int(values[0])
            value = float(values[1])



print "\t".join(map(lambda (values): str(avg_peak(values)), results[:-1]))
