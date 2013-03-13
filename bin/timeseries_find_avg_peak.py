#!/usr/bin/python

import sys

PEAK_BOTTOM = 10

def avg_peak(values):
    sum = 0
    count = 0
    #print '---'
    for value in values:
        if value > PEAK_BOTTOM:
            #print value
            sum += value
            count += 1
    if count == 0:
        return 0
    return sum / count

begin = int(sys.argv[1])
end = int(sys.argv[2])
print "between %i and %i" % (begin, end)

results = []
index = 0
results.append([])

for line in sys.stdin:
    values = line.split()
    if len(values) == 2:
        if not values[0].isdigit():
            continue
        time = int(values[0])
        if time >= begin and time <= end:
            value = float(values[1])
            results[index].append(value)
        if time > end and len(results[index]) != 0:
            #print time
            index = index + 1
            results.append([])

print "\t".join(map(lambda (values): str(avg_peak(values)), results[:-1]))
