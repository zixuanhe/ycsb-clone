#!/usr/bin/python

import sys
import pkg_resources

pkg_resources.require("matplotlib==1.3.x")

import matplotlib.pyplot as plt

TEST_TIME = 40 * 60 * 1000 #40 Mins in ms


def f(x_range, dict_to_draw):
    for p in x_range:
        yield dict_to_draw.get(p, 0) 
    

if __name__ == "__main__":
    to_draw = {}
    for line in sys.stdin.readlines():
        items = line.split('\t')
        to_draw[int(items[0])] = float(items[1])
        
    x = xrange(0, TEST_TIME, 100)
    g = f(x, to_draw)

    plt.plot(x, [y for y in g], 'r')
    plt.savefig('out.svg')#, transparent=True, bbox_inches='tight', pad_inches=0)
    
