import os
import sys
import timeseries_draw
import timeseries_merge

if __name__ == "__main__":
    # this script goes over all dirs and subdirs under
    # prefix and selects all paths that do 'failover_ram'
    # tests. For each path under the condition the graph is built
    prefix = "/home/nick/buffer/Aerospike"
    paths = []
    for path in os.walk(prefix):
        # if this path is for failover_ram and has no chils, e.g.
        # '/home/nick/buffer/Aerospike/Aerospike/failover_ram/async/50_percent_max_throughput'
        if 'failover' in path[0] and len(path[1]) == 0:
            paths.append(path[0])
    # now the list of dirs formed, generate the pictures
    for path in paths:
        os.chdir(path)
        sys.argv = ["", "series.txt"]
        timeseries_merge.merge()
        timeseries_draw.draw()
        print "done with %s" % path

    # ts_merge = "/home/nick/ycsb/bin/timeseries_merge.py"
    # ts_draw  = "/home/nick/ycsb/bin/timeseries_draw.py"
    # os.system("cd %s; %s | %s" % (path, ts_merge, ts_draw))
    print "all walking done!"
