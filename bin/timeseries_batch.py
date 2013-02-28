from __future__ import print_function
import csv
import os
import sys
import timeseries_draw
import timeseries_merge

if __name__ == "__main__":
    # this script goes over all dirs and subdirs under
    # prefix and selects all paths that do 'failover_ram'
    # tests. For each path under the condition the graph is built
    prefix = "/home/nick/buffer/Aerospike"
    # postfix - where the new graphs will be put
    postfix = "/home/nick/buffer/Aerospike/XGraphs/"
    # if file paths.txt exists, then load paths from it
    # otherwise walk over prefix dir

    paths = []
    for path in os.walk(prefix):
        # if this path is for failover_ram and has no chils, e.g.
        # '/home/nick/buffer/Aerospike/Aerospike/failover_ram/async/50_percent_max_throughput'
        if 'failover' in path[0] and len(path[1]) == 0:
            paths.append(path[0])
    # paths = filter(lambda s: "Aerospike26" in s, paths)
    # now the list of dirs formed, generate the pictures
    collect = []
    for path in paths:
        os.chdir(path)
        sys.argv = ["", "series.txt"]
        timeseries_merge.merge(collect)
        name = timeseries_draw.draw()
        # move this new wonderful file to XGraphs
        src_name = "%s.png" % name
        tgt_name = postfix + "%s.png" % name
        try:
            os.rename(src_name, tgt_name)
        except OSError as e:
            print(e)
        print("done with %s" % path)

    with open("/home/nick/buffer/collect.txt", "w") as f:
        cw = csv.writer(f, dialect='excel-tab')
        collect.sort(key = lambda c: c[0])
        for c in collect:
            lt_nd = c[1]['_lt_nd']
            lt_nu = c[1]['_lt_nu']
            row = [c[0], lt_nd, lt_nu]
            cw.writerow(row)

    # ts_merge = "/home/nick/ycsb/bin/timeseries_merge.py"
    # ts_draw  = "/home/nick/ycsb/bin/timeseries_draw.py"
    # os.system("cd %s; %s | %s" % (path, ts_merge, ts_draw))
    print("all walking done!")
