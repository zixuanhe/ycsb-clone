#!/usr/bin/python
import csv

import sys

# import pkg_resources
# pkg_resources.require("matplotlib==1.3.x")

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


def f(x, dict_to_draw):
    dict_to_draw.get(x, 0)
    # for p in x_range:
    #     yield dict_to_draw.get(p, 0)


def load_series(fin):
    # all series is sorted, there is no need to use dictionaries
    drlt = [[],[]] # x and y for read latency
    dult = [[],[]] # x and y for update latency
    dthr = [[],[]] # x and y for throughput
    # the block number, 0 - read, 1 - update, 2 - throughput
    # see /timeseries_merge.py:70
    block = 0
    reader = csv.reader(fin, dialect='excel-tab')
    for items in reader:
        if len(items) < 2:
            block += 1
        else:
            if block == 0:
                drlt[0].append(int(items[0]))
                drlt[1].append(float(items[1]))
            elif block == 1:
                dult[0].append(int(items[0]))
                dult[1].append(float(items[1]))
            else:
                dthr[0].append(int(items[0]))
                dthr[1].append(float(items[1]))
    # dead birds falling from the sky...
    # maybe use dict?
    return (drlt, dult, dthr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # filename passed
        with open(sys.argv[1]) as fin:
            (drlt, dult, dthr) = load_series(fin)
    else:
        # from stdin
        (drlt, dult, dthr) = load_series(sys.stdin)

    min_x = min(min(drlt[0]), min(dult[0]), min(dthr[0]))
    max_x = max(max(drlt[0]), max(dult[0]), max(dthr[0]))

    plt.subplot(211)
    plt.grid(True)
    plt.plot(dthr[0], dthr[1], 'r')
    plt.xlim([min_x, max_x])
    plt.xlabel('Execution time (ms)')
    plt.ylabel('Throughput (msgs/sec)')

    ax = plt.subplot(212)
    plt.grid(True)
    p1, = plt.plot(drlt[0], drlt[1], 'b', label = 'Read latency')
    p2, = plt.plot(dult[0], dult[1], 'g', label = 'Update latency')
    plt.xlim([min_x, max_x])
    plt.ylim([0, 5])
    plt.xlabel('Execution time (ms)')
    plt.ylabel('Latency (ms)')
    fontP = FontProperties()
    fontP.set_size('small')
    ax.legend(prop = fontP)

    # plt.show()
    plt.savefig("series.svg")