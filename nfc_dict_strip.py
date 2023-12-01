#!/usr/bin/env python3

"""
    nfc_dict_strip.py : strip duplicate dict keys
    Written By: Peter Shipley github.com/evilpete

    From pkg https://github.com/evilpete/flipper_toolbox
"""

# Quick script to comment out or strip duplicate dict keys

#
# nfc_dict_strip.py mf_classic_dict.nfc mf_classic_dict_user.nfc > mf_classic_dict_user_unique.nfc
#

import sys
import time

file1 = file2 = del_dups = None
_debug = 0

gen_str = "# Generated with https://github.com/evilpete/flipper_toolbox"


def dict_strip(file_1, file_2):

    with open(file_1, 'r', encoding="utf-8") as fd:
        list_A = [line.strip().upper() for line in fd if line[0] != '#' and len(line) > 4]
    # print("list_A", len(list_A), file_1)
    set_A = set(list_A)

    with open(file_2, 'r', encoding="utf-8") as fd:
        for line in fd:
            if _debug:
                print(f">>> {line}", end="", file=sys.stderr)
            if line[0] == '#':
                if not line.startswith("# Generated "):
                    print(line, end="")
                continue
            dat = line[:12].upper()
            if _debug:
                print("line len =", len(line), file=sys.stderr)
                print("DAT len =", len(dat), file=sys.stderr)
            if dat in set_A:
                if del_dups is None:
                    print(f"#- {line}", end="")
            else:
                print(dat)
                # print(line, end="")

    print(gen_str)
    print(f"# Generated {time.ctime()}")


if __name__ == '__main__':

    av = sys.argv[1:]

    if av and av[0] == '-h':
        print("Usage:\n\tnfc_dict_strip.py [-d ] dict_file_A dict_file_B > dict_nodups\n")
        print("\tremoves duplicate keys, outputing only keys unique to dict_file_B")
        sys.exit(0)

    if av and av[0] == '-d':
        av.pop(0)
        del_dups = True

    if av:
        file1 = av.pop(0)
    if av:
        file2 = av.pop(0)

    if not (file1 and file2):
        print("Two filesnames required", file=sys.stderr)
        sys.exit(0)

    dict_strip(file1, file2)
