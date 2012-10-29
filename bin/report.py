#!/usr/bin/python

# Extracts statistics data from the workload report

import sys,re

pattern = re.compile(r'\[([^,]*)\],\s*(\d*[^\(,\d=]{3,}(=\-?\d+)?)[^,]*,\s*([0-9\.Ee]+)')

results = {}
out = []

for line in sys.stdin:
    match = pattern.match(line)
    if match != None:
	#print '%s\t%s\t%s' % (match.group(1), match.group(2), match.group(3))
	key = match.group(2)
	while (results.has_key(key)):
		key += '_'
	results[key] = match.group(4)

#print results

def toMillis(value):
	return str(float(value)/1000.0)
	
def appendString(key):
	if results.has_key(key):
		out.append(results[key])
	else:
		out.append('')
		
def appendMicros(key):
	if results.has_key(key):
		out.append(toMillis(results[key]))
	else:
		out.append('')
		
def appendSum(*keys):
	s = 0
	for key in keys:
		if results.has_key(key):
			s += int(results[key])
	out.append(str(s))

appendString('RunTime')
appendString('Throughput')
out.append('')
appendString('Operations')
appendSum('Return=-1', 'Return=1')
appendMicros('AverageLatency')
appendMicros('MinLatency')
appendMicros('MaxLatency')
appendString('95thPercentileLatency')
appendString('99thPercentileLatency')
appendString('Operations_')
appendSum('Return=-1_', 'Return=1_')
appendMicros('AverageLatency_')
appendMicros('MinLatency_')
appendMicros('MaxLatency_')
appendString('95thPercentileLatency_')
appendString('99thPercentileLatency_')

print '\t'.join(out)
