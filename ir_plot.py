#!/usr/bin/env python3
"""

    ir_plot.py

    plot data from flipper IR raw data save files

    Warning:   this is 5 min hack code, use at own risk

    Written By: Peter Shipley github.com/evilpete

    From pkg https://github.com/evilpete/flipper_toolbox

"""

import sys
from statistics import mean
import pprint
import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt

debug = 0
PRINT_BITS = True       # this is a hack


def get_cmd_data_str(filename, targ_cmd):
    name = None
    data_str = None

    with open(filename, 'r', encoding="utf-8") as fd:
        header = fd.readline().strip()
        if header != 'Filetype: IR signals file':
            print(f"Error: {filename} is not a 'Flipper IR signals file'")
            sys.exit(1)
        for line in fd:
            if line.startswith('name:'):
                try:
                    n = line.split(':')[1].strip()
                except IndexError:
                    continue
                else:
                    if targ_cmd is None or n == targ_cmd:
                        name = n
                        break

        if name is None:
            print("name not found")
            return None

        # print("Found name", n)

        for line in fd:
            if line.startswith('data:'):
                try:
                    data_str = line.split(':')[1].strip()
                    return data_str
                except IndexError:
                    continue

    print("data not found")
    return data_str


def split_data(dat, max_val=20000):

    dat_list = dat.split()
    ret = []
    cur_dat = []

    # print(f"dat_list: {len(dat_list)}")

    for x in dat_list:
        i = int(x)
        if i > max_val:
            ret.append(cur_dat)
            # print(f"cur_dat: {len(cur_dat)}")
            cur_dat = []
        else:
            cur_dat.append(i)

    ret.append(cur_dat)

    return ret


LOW_PLOT_VAL = 1
HIGH_PLOT_VAL = 5


def convert_dat(dat_list, normalize=0):

    if len(dat_list) % 2 != 0:
        dat_list.append(0)

    dat_len = len(dat_list)

    if debug > 1:
        print(f"dat_len {dat_len}")

    i_min = 15
    # o_min = 23
    if normalize:
        e = dat_list[2::2]
        i_min = min(e) // 10
        if debug > 2:
            o = dat_list[3::2]
            print(min(dat_list), mean(dat_list), max(dat_list), "\n", dat_list, "\n")
            print(min(e), mean(e), max(e), "\n", e, "\n")
            print(min(o), mean(o), max(o), "\n", o, "\n")
            print("\n\n")

    res = []
    for x in range(0, dat_len, 2):

        i = dat_list[x] // 10
        if normalize:
            i = (i // i_min) * i_min

        j = int(dat_list[x + 1]) // 10
        if normalize:
            j = (j // 23) * 26

        # print(f"{x}: {i} {j} -> {i2} {j2}")
        res += [LOW_PLOT_VAL] * i
        res += [HIGH_PLOT_VAL] * j
        res.append(1)

    # print("\n")
    return res


def main():

    filen = None
    cmd_name = None

    av = sys.argv[1:]
    if av:
        filen = av.pop(0)

    if av:
        cmd_name = av.pop(0)

    if filen is None:
        print('Usage:\n\tir_plot.py <flipper_ir_file.ir> <ir_command_name>')
        sys.exit(0)

    # plot_data = []
    cmd_data_str = get_cmd_data_str(filen, cmd_name)
    if cmd_data_str is None:
        print(f'was not able to find raw data for "{cmd_name}"')
        sys.exit(0)

    if debug > 1:
        print(cmd_data_str)

    dat_lists = split_data(cmd_data_str)

    if debug > 1:
        pprint.pprint(dat_lists, indent=4, compact=True)

    list_lenghts = []
    conv_dat_lists = []
    for d in dat_lists:

        if debug or PRINT_BITS:  # this method is total hack
            # Print Bits
            o = d[3::2]
            avg_val = mean(o)
            bits = ['0' if b < avg_val else '1' for b in o]
            # print(o)
            print(bits)

        n_dat = convert_dat(d, normalize=True)
        conv_dat_lists.append(n_dat)
        list_lenghts.append(len(n_dat))

    # print(list_lenghts)
    max_len = max(list_lenghts)
    # print(max_len)
    xp = np.arange(max_len)

    ax = plt.gca()
    ax.axes.yaxis.set_visible(False)
    plt.title(f"IR Signal: {cmd_name}")

    y_off = 0
    for d in conv_dat_lists:
        d_len = len(d)
        if d_len < max_len:
            l = max_len - d_len
            d += [1] * l

        py = np.array(d) + (y_off * (HIGH_PLOT_VAL + 1))

        plt.plot(xp, py)

        # y_off += HIGH_PLOT_VAL + 1
        y_off += 1

    plt.gcf().set_size_inches(6, 1 + (.5 * y_off))
    plt.show()


if __name__ == '__main__':
    main()
