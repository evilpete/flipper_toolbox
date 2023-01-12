#!/usr/bin/env python3
"""

    ir_plot.py

    plot data from flipper subghz raw data save files

    Warning:   this is 5 min hack code, use at own risk

    Written By: Peter Shipley github.com/evilpete

    From pkg https://github.com/evilpete/flipper_toolbox

"""


import sys
import os
# from statistics import mean
import argparse
import statistics
# from pprint import pprint
import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt

verbose = 0

PRINT_BITS = True       # this is a hack

LOW_PLOT_VAL = 1
HIGH_PLOT_VAL = 5

MIN_BIT_LEN = 1000
DATA_SCALE = 10


def arg_opts():

    parser = argparse.ArgumentParser(add_help=True,  # noqa
                        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--verbose', dest="verbose",
                        default=0,
                        help='Increase debug verbosity', action='count')

    parser.add_argument("-s", "--split", dest="split_sig",
                        action='store_true',
                        help="try to split and (sub)plot signals separately")

    parser.add_argument("-p", "--preamble", dest="preamble",
                        type=int,
                        default=0,
                        help="split signal break length")

    parser.add_argument("-n", "--numplots", dest="numplots",
                        type=int,
                        default=0,
                        help="maximum number of subplots")

    parser.add_argument("-l", "--length", dest="length",
                        type=int,
                        default=0,
                        help="minimum signal bits")

    parser.add_argument("--seek", dest='seek',
                        type=int,
                        default=0,
                        help="number of samples to skip")

    # parser.add_argument("-m", "--minpulse", dest="minbitlen",
    #                     type=int,
    #                     default=0,
    #                     help="minimum pause length")

    parser.add_argument("-f", "--file", dest="filename",
                        default=None,
                        help="Subghz Filename")

    parser.add_argument("-i", "--invert", dest="invert",
                        default=False,
                        action='store_true',
                        help="Invert Wave plot")

    # parser.add_argument("-d", "--dir", dest="destdir",
    #                     default=None,
    #                     help="Destination")

    # parser.add_argument("-o", "--output", dest="out_format",
    #                     choices=['png', 'pdf', 'svg'],
    #                     default="None",
    #                     help="Output Format")

    # parser.add_argument("-s", "--screen", dest="screen",
    #                     default=False, action='store_true',
    #                     help="Display on Screen")

    # data_grp = parser.add_mutually_exclusive_group()

    return parser.parse_known_args()


def split_data_str(dat, max_val=8000):

    ret = []
    cur_dat = []

    for x in dat:
        i = abs(x)
        if i > max_val:
            if cur_dat:
                ret.append(cur_dat)
            # print(f"cur_dat: {len(cur_dat)}")
            cur_dat = []
        else:
            cur_dat.append(x)

    ret.append(cur_dat)

    return ret


def load_cmd_data(filename):

    ret = []
    with open(filename, 'r', encoding="utf-8") as fd:

        header = fd.readline().strip()
        if header != 'Filetype: Flipper SubGhz RAW File':
            print(f"Error: {filename} is not a Flipper SubGhz RAW file")
            sys.exit(1)

        for line in fd:

            line = line.strip()

            if not line or line[0] == '#':        # skip blank lines
                continue

            if line.startswith("RAW_Data: "):
                a = line[10:].split()
                ret.extend(map(int, a))

    return ret


def convert_dat(dat_list, invert=False, divider=0):  # normalize=0,

    high_val = HIGH_PLOT_VAL
    low_val = LOW_PLOT_VAL

    if len(dat_list) % 2 != 0:
        dat_list.append(0)

    dat_len = len(dat_list)

    if verbose > 1:
        print(f"dat_len {dat_len}")

    if invert:
        high_val = LOW_PLOT_VAL
        low_val = HIGH_PLOT_VAL

    res = [low_val]
    for i in dat_list:

        if divider:
            i //= divider

        if i > 0:
            res += [high_val] * i
        else:
            res += [low_val] * abs(i)

        res.append(1)

    # print("\n")
    return res


def main(arg, av):

    # disp = False

    # get input filename from argparse or fist arg
    if arg.filename:
        fname = arg.filename
    elif av:
        fname = av.pop(0)

    raw_dat = load_cmd_data(fname)

    if arg.seek:
        raw_dat = raw_dat[:arg.seek]

    # max_sig = max(raw_dat)
    # print(f"min {min_sig}")
    # print(f"max {max_sig}")
    # max_pause = int(statistics.mean(a_dat))

    a_dat = list(map(abs, raw_dat))

    # print(f"max_pause max//2  {max_pause}")
    # max_pause = int(statistics.mean(a_dat)) * 3
    max_pause = int(statistics.stdev(a_dat)) * 2

    max_pause = (arg.preamble or max_pause)
    # max(min_sig, max_sig) // 2)

    if verbose:
        print(f"max_pause {max_pause}")

    if arg.preamble or arg.split_sig:
        # print(f"using max_val {max_pause}")
        dat_list = split_data_str(raw_dat, max_val=max_pause)
    else:
        dat_list = [raw_dat]

    if verbose:
        print(f"dat_list {len(dat_list)}")

    min_length = (arg.length or MIN_BIT_LEN)
    plot_list = []
    for x in dat_list:
        y = convert_dat(x, divider=DATA_SCALE)
        if len(y) >= min_length:
            plot_list.append(convert_dat(x, divider=10))

    # print(f"plot_list {len(plot_list)}")

    # plot_list = plot_list[:8]

    if arg.numplots:
        plot_list = plot_list[:arg.numplots]

    list_lenghts = [len(x) for x in plot_list]

    max_len = max(list_lenghts)

    if verbose:
        print(f"max_len {max_len}")

    plot_x = np.arange(max_len*DATA_SCALE, step=DATA_SCALE)

    plt.style.use("dark_background")
    p = plt.figure()  # facecolor='yellow')
    ax = p.gca()
    ax.get_yaxis().set_visible(False)
    plt.xlabel('μs')

    plt.title("SubGhz Raw Signal")

    height = 6
    pn = len(plot_list)
    if pn < 8:
        height = 2 + pn * .5
    plt.gcf().set_size_inches(6, height)
    # plt.figure(facecolor='yellow')

    y_off = 0
    for d in plot_list:
        d_len = len(d)
        # if d_len < max_len:
        #    ln = max_len - d_len
        #    d += [1] * ln

        plot_y = np.array(d) + (y_off * int(HIGH_PLOT_VAL * 1.3))

        plt.plot(plot_x[:d_len], plot_y)

        y_off += 1

    # if arg.out_format == 'png':
    #    if arg.verbose:
    #        print(f'{destdir}/{ii}_{cmd_name}.png  y_off={y_off}')
    outfile = os.path.basename(fname)
    outfile = os.path.splitext(outfile)[0] + ".png"
    print(f"saving plot as {outfile}")

    plt.savefig(outfile, pad_inches=0.3)

    # if disp:
    plt.show()


if __name__ == '__main__':
    ag, agv = arg_opts()
    # print("arg", arg, "av=", av)

    if ag.verbose:
        verbose = ag.verbose

    main(ag, agv)
