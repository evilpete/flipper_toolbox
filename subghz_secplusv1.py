#!/usr/bin/env python3

# **WORK IN PROGRESS**

#
#  Display and/or edit Flipper SubGhz Security+ 1.0 Key Files
#
# Peter Shipley github.com/evilpete
#
# From pkg https://github.com/evilpete/flipper_toolbox
#


import sys
# import os
# from typing import Iterable, Union, Any
import random
import argparse

_debug = 0

MAX_FIXED = 3**20 - 1
MAX_ID = 3**17 - 1
TX_FREQ = 315000000

BUTTON_NAMES = ["Middle", "Left", "Right"]


# https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-to-a-string-in-any-base
def numToBase(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]


def numToBase_str(n, b):
    a = numToBase(n, b)
    rstr = map(str, a)
    return "".join(rstr)


def arg_opts():

    parser = argparse.ArgumentParser(add_help=True, allow_abbrev=True,  # noqa
                        description="display and/or edit Flipper SubGhz Security+ 1.0 Key Files",
                        formatter_class=argparse.RawDescriptionHelpFormatter
                        )
    # argument_default=argparse.SUPPRESS,

    parser.add_argument("-r", "-rolling", metavar='rolling_code',  dest="rolling",
                        default=None,
                        help="Rolling Count")

    parser.add_argument("-b", "--button", metavar='button_id',  dest="button",
                        # type=int,
                        default=None,
                        help="Button: 0=Middle 1=Left 2=Right")

    fixed_grp = parser.add_mutually_exclusive_group()

    fixed_grp.add_argument("-f", "--fixed", metavar='fixed_code', dest="fixed",
                           default=0,
                           help="fixed code value")

    fixed_grp.add_argument("-i", "--id", metavar='remote_id', dest="id",
                           default=None,
                           help="Remote-ID")

    parser.add_argument("-q", "--quiet", dest="quiet",
                        default=None,
                        action='store_true',
                        help="run quietly")

    parser.add_argument("-o", "--out", metavar='output_filename', dest="outfname",
                        default=None,
                        help="output filename, use '-' for stdout")

    parser.add_argument("input_file", metavar='input-file', nargs='?',
                        #  "-F", "--File", dest="input_file",
                        # type=argparse.FileType('r', encoding='UTF-8'),
                        default=None,
                        help="Flipper Subghz File")

#    parser.add_argument("-h", "--freq", "--hz", dest="send_freq",
#                        type=int,
#                        default=315000000,
#                        help="Transmit frequency")

    ar, gs = parser.parse_known_args()

    ar.rolling = conv_int(ar.rolling)
    ar.fixed = conv_int(ar.fixed)
    ar.id = conv_int(ar.id)

    if ar.rolling and int(ar.rolling) >= 2**32:
        raise ValueError("Rolling code must be less than 2^32")

    if ar.fixed and int(ar.fixed) >= MAX_FIXED:
        raise ValueError(f"Fixed code must be less than 3^20 ({MAX_FIXED})")

    if ar.id and int(ar.id) > MAX_ID:
        raise ValueError(f"Remote ID must be less than 3^17 ({MAX_ID})")

    # ar.button.isdigit() and int(ar.button) <= 2:
    if ar.button and ar.button not in ['0', '1', '2']:
        raise ValueError(f"Button value must be between 0 -> 2 ({ar.button})")

    return ar, gs


SUBGHZ_KEY_FILE_TYPE = "Flipper SubGhz Key File"


def read_file(fd):

    key_dat = None
    header = fd.readline().strip()

    a = header.split(':', 1)
    if not (a[0].startswith("Filetype")
            and a[1].strip() == SUBGHZ_KEY_FILE_TYPE):
        print("invalid filetype")
        sys.exit(0)

    for line in fd:
        a = line.split(':', 1)

        if a[0].startswith("Protocol"):
            if a[1].strip() != "Security+ 1.0":
                sys.exit(0)

        if a[0].startswith("Key"):
            key_dat = a[1].strip().split()

    if _debug:
        print("read_file", key_dat)

    if key_dat:
        # return "".join(key_dat), "".join(pkt_dat)
        return key_dat

    return None


def write_file(rol, fix, fname=None, quiet=False):

    hf = f"{fix:08X}"
    hr = f"{rol:08X}"
    #  print(f"1: {ha}")
    # print(f"2: {hb}")
    hval = hf + hr

    key_str = " ".join([hval[i:i + 2] for i in range(0, 16, 2)])

    comment_str = pretty_print(rol, fix)

# Id:{fix // 27:08X} ({fix // 27}) Rolling:{rol:02X} ({rol})
    ret = f"""Filetype: Flipper SubGhz Key File
Version: 1
# Generated with https://github.com/evilpete/flipper_toolbox
# {comment_str}
Frequency: {TX_FREQ}
Preset: FuriHalSubGhzPresetOok650Async
Protocol: Security+ 1.0
Bit: 42
Key: {key_str}
"""  # noqa

    if _debug:
        print(ret)
    print(ret)

    if fname is None:
        fname = f"secv1-{fix:010X}.sub"

    if fname == '-':
        sys.stdout.write(ret)
    else:
        if not fname.endswith('.sub'):
            fname += '.sub'

        if not quiet:
            print(f"writting: {fname}")

        with open(fname, "w", encoding="utf-8") as fd:
            fd.write(ret)


# SUBGHZ_KEY_FILE_TYPE "Flipper SubGhz Key File"

hex_set = set('abcdefABCDEF0123456789')


def is_hex_str(s):
    return set(s).issubset(hex_set)


def conv_int(arg):

    if arg == 0:
        return 0

    if not arg:
        return None

    if arg[:2].lower() in ['0b', '0x']:
        return int(arg, 0)

    if arg.isdigit():
        return int(arg)

    if is_hex_str(arg):
        return int(arg, 16)

    return None


def pretty_print(rolling, fixed):

    ret_str = f"Rolling={rolling},"
    ret_str += f" Fixed={fixed},"

    fixed_b3 = numToBase_str(fixed, 3)

    b_id = fixed_b3[-1]  # a_base3.pop(0)
    id0 = fixed_b3[-2]
    id1 = fixed_b3[-3]

    if id1 == "1":
        remote_id3 = fixed_b3[:-3]
        remote_id = int(remote_id3, 3)

        button_id = BUTTON_NAMES[int(b_id)]

        ret_str += f" id0={id0}, id1={id1},"
        ret_str += f" Remote_id={remote_id} ({remote_id:08X}),"
        ret_str += f" Button_id={button_id} ({b_id})"

    elif id1 == "0":
        pad_id3 = fixed_b3[-10:-3]
        pad_id = int(pad_id3, 3)
        pin3 = fixed_b3[-19:-10]
        pin = int(pin3, 3)

        ret_str += f" pad_id={pad_id}"
        if pin <= 9999:
            ret_str += f" pin={0:04}"
        elif pin <= 11029:
            ret_str += f" pin=Enter ({pin})"

        pin_suffix = fixed_b3[0]
        if pin_suffix == "1":
            ret_str += " #"
        elif pin_suffix == "2":
            ret_str += " *"

    return ret_str


def main():

    rolling_dat = fixed_dat = 0

    args, _extra = arg_opts()

    if _debug:
        print("args", args)
        print("_extra", _extra)

    if args.input_file:
        with open(args.input_file, 'r', encoding='UTF-8') as fd:
            xx = read_file(fd)

        if xx:
            s_key = "".join(xx)
            i_key = int(s_key, 16)
            b_key = f"{i_key:08b}"

        if _debug:
            print(s_key)
            print(i_key)
            print(b_key[6:])

        fixed_dat = (i_key >> 32) & 0xFFFFFFFF

        rolling_dat = (i_key & 0xFFFFFFFF)

    if _debug:  # and (fixed_out or rolling_out):
        print(f">> fixed_dat  {fixed_dat:12d} "
              f"{fixed_dat:010X} {fixed_dat:016b} "
              + numToBase_str(fixed_dat, 3))
        print(f">> rolling_dat    {rolling_dat:12d} "
              f"{rolling_dat:010X} {rolling_dat:040b} "
              + numToBase_str(rolling_dat, 3))

    a_fixed = args.fixed or fixed_dat

    a_id0 = a_id1 = a_remote_id = a_but = None

    if a_fixed:
        a_base3 = numToBase_str(a_fixed, 3)
        a_but = a_base3[-1]  # a_base3.pop(0)
        a_id0 = a_base3[-2]
        a_id1 = a_base3[-3]
        a_remote_id3 = a_base3[:-3]
        a_remote_id = int(a_remote_id3, 3)

    r_but = args.button or a_but or 1

    # 129140162
    r_id = args.id or a_remote_id or random.randint(2**22, MAX_ID - 1)

    r_rolling = (args.rolling or rolling_dat or 1) & 0xFFFFFFFF  # 32 bits max

    # fixed_code = (r_id & 0xffffffff) | (r_button << 32)

    # button_code = random.randint(3, 172) | 0x01

    if _debug:
        print(f"r_button   {r_but}")
        print(f"r_id       {r_id:12d} {r_id:010X} {r_id:016b}", numToBase_str(r_id, 3))
        print(f"r_rolling  {r_rolling:12d} {r_rolling:010X} {r_rolling:016b}", numToBase_str(r_rolling, 3))
        # print(f"fixed_code {fixed_code:12d} {fixed_code:010X} {fixed_code:040b}")  # noqa

    r_id3 = numToBase_str(r_id, 3)
    r_id0 = a_id0 or "0"
    r_id1 = a_id1 or "1"

    r_fixed3 = r_id3 + r_id1 + r_id0 + str(r_but)

    r_fixed = int(r_fixed3, 3)
    # print(f"r_fixed  {r_fixed:12d} {r_rolling:010X} {r_fixed:016b} {r_fixed3}")

    if not args.quiet:
        pretty_out = pretty_print(r_rolling, r_fixed)
        print(f"\nSecurity+ V1: {pretty_out}\n")

    # only save to file if new of changed
    if (args.fixed or args.button or args.id or args.rolling) or not fixed_dat:
        write_file(r_rolling, r_fixed, args.outfname, args.quiet)


if __name__ == '__main__':
    main()
