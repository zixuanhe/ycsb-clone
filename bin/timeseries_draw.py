#!/usr/bin/python
import csv

import sys

from matplotlib.offsetbox import TextArea, Bbox

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


def draw():
    if len(sys.argv) > 1:
        # filename passed
        with open(sys.argv[1]) as fin:
            (drlt, dult, dthr) = load_series(fin)
    else:
        # from stdin
        (drlt, dult, dthr) = load_series(sys.stdin)
    min_x = min(min(drlt[0]), min(dult[0]), min(dthr[0]))
    max_x = max(max(drlt[0]), max(dult[0]), max(dthr[0]))
    xndown = 600000 # the time for node down
    xnup = 1200000   # the time for node up
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    plt.grid(True)
    plt.plot(dthr[0], dthr[1], 'r')
    plt.xlim([min_x, max_x])
    plt.xlabel('Execution time (ms)')
    plt.ylabel('Throughput (ops/sec)')
    (ymin, ymax) = plt.ylim()
    ax1.axvline(x=xndown, ymin=ymin, ymax=ymax, linestyle='--')
    ax1.axvline(x=xnup, ymin=ymin, ymax=ymax, linestyle='--')
    ax1.annotate('node down', xy=(xndown, ymax), xytext=(xndown - 300000, ymax * 1.03333),
                 ha='center', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                 color='red'))
    ax1.annotate('node up', xy=(xnup, ymax), xytext=(xnup + 300000, ymax * 1.03333),
                 ha='center', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',
                                 color='red'))
    # ax1.text(600000, ymax, 'node down')
    # ax1.text(650000, ymax, 'node up')
    ax2 = fig.add_subplot(212)
    plt.grid(True)
    plt.plot(drlt[0], drlt[1], 'b', label='Read latency')
    plt.plot(dult[0], dult[1], 'g', label='Update latency')
    plt.xlim([min_x, max_x])
    plt.ylim([0, 15])
    plt.xlabel('Execution time (ms)')
    plt.ylabel('Latency (ms)')
    fontP = FontProperties()
    fontP.set_size('small')
    ax2.legend(prop=fontP)
    # fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    fig.savefig('series.png', dpi=80)
    # plt.show()

if __name__ == "__main__":
    draw()
