#!/usr/bin/python

# Extracts statistics data from the workload report

import sys,re

pattern = re.compile(r'\[([^,]*)\],\s*([^\(,\d]{3,})[^,]*,\s*([0-9\.]+)')

results = {}

for line in sys.stdin:
    match = pattern.match(line)
    if match != None:
	#print '%s\t%s\t%s' % (match.group(1), match.group(2), match.group(3))
	results[match.group(2)] = match.group(3)

print results

def toMillis(value):
	return str(float(value)/1000.0)

out = []
out.append(results['RunTime'])
out.append(results['Throughput'])
out.append('')
out.append(results['Operations'])
out.append(toMillis(results['AverageLatency']))
out.append(toMillis(results['MinLatency']))
out.append(toMillis(results['MaxLatency']))
if results.has_key('95thPercentileLatency'):
	out.append(toMillis(results['95thPercentileLatency']))
else:
	out.append('')
if results.has_key('99thPercentileLatency'):
	out.append(toMillis(results['99thPercentileLatency']))
else:
	out.append('')	

print '\t'.join(out)
