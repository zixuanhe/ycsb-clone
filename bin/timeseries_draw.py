#!/usr/bin/python
import csv

import sys

# import pkg_resources
# pkg_resources.require("matplotlib==1.3.x")

import matplotlib.pyplot as plt
import numpy as np

# TEST_TIME = 40 * 60 * 1000 #40 Mins in ms
from numpy import arange


def f(x, dict_to_draw):
    dict_to_draw.get(x, 0)
    # for p in x_range:
    #     yield dict_to_draw.get(p, 0)


def load_series(fin):
    # all series is sorted, there is no need to use dictionaries
    draw_rlat = [[],[]] # x and y for read latency
    draw_ulat = [[],[]] # x and y for update latency
    draw_thr  = [[],[]] # x and y for throughput
    # the block number, 0 - read, 1 - update, 2 - throughput
    # see /timeseries_merge.py:70
    block = 0
    reader = csv.reader(fin, dialect='excel-tab')
    for items in reader:
        if len(items) < 2:
            block += 1
        else:
            if block == 0:
                draw_rlat[0].append(int(items[0]))
                draw_rlat[1].append(float(items[1]))
            elif block == 1:
                draw_ulat[0].append(int(items[0]))
                draw_ulat[1].append(float(items[1]))
            else:
                draw_thr[0].append(int(items[0]))
                draw_thr[1].append(float(items[1]))
    # dead birds falling from the sky...
    # maybe use dict?
    return (draw_rlat, draw_ulat, draw_thr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # filename passed
        with open(sys.argv[1]) as fin:
            (draw_rlat, draw_ulat, draw_thr) = load_series(fin)
    else:
        # from stdin
        (draw_rlat, draw_ulat, draw_thr) = load_series(sys.stdin)

    min_x = min(min(draw_rlat[0]), min(draw_ulat[0]), min(draw_thr[0]))
    max_x = max(max(draw_rlat[0]), max(draw_ulat[0]), max(draw_thr[0]))

    plt.subplot(211)
    plt.grid(True)
    plt.plot(draw_rlat[0], draw_rlat[1], 'b', draw_ulat[0], draw_ulat[1], 'g')
    plt.xlim([min_x, max_x])
    plt.ylim([0, 10])
    plt.xlabel('Execution time (ms)')
    plt.ylabel('Latency (ms^(-1))')

    plt.subplot(212)
    plt.grid(True)
    plt.plot(draw_thr[0], draw_thr[1], 'r')
    plt.xlim([min_x, max_x])
    plt.xlabel('Execution time (ms)')
    plt.ylabel('Throughput (messages/sec)')

    # plt.show()
    plt.savefig("series.png")