#!/usr/bin/env python3

# **WORK IN PROGRESS**

#
#  Display and/or edit Flipper SubGhz Security+ 2.0 Key Files
#
# Peter Shipley github.com/evilpete
#
# From pkg https://github.com/evilpete/flipper_toolbox
#

import sys
import os
# from typing import Iterable, Union, Any
import random
import json
import argparse
import pprint

try:
    import secplus.secplus as Secplus
except ImportError as e:
    print("Failed to import secplus")
    print("https://github.com/argilo/secplus/blob/master/secplus.py")
    sys.exit(0)

_debug = 0

TX_FREQ = 315000000


def arg_opts():

    parser = argparse.ArgumentParser(add_help=True, allow_abbrev=True,  # noqa
                        description="display and/or edit Flipper SubGhz Security+ 2.0 Key Files",  # noqa
                        formatter_class=argparse.RawDescriptionHelpFormatter
                        )
    # argument_default=argparse.SUPPRESS,

    parser.add_argument("-r", "-rolling", metavar='rolling_code',
                        dest="rolling",
                        default=None,
                        help="Rolling Count")

    parser.add_argument("-b", "--button", metavar='button_id',
                        dest="button",
                        default=0,
                        help="Button")

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

    parser.add_argument("-J", "--Json", metavar='rtl_log.json',
                        dest="json_log",
                        default=None,
                        help="Read rtl_433 json log")

    parser.add_argument("-o", "--out", metavar='output_filename',
                        dest="outfname",
                        default=None,
                        help="output filename, use '-' for stdout")

    parser.add_argument("input_file", metavar='input-file', nargs='?',
                        default=None,
                        help="Flipper Subghz File")

#    parser.add_argument("-h", "--freq", "--hz", dest="send_freq",
#                        type=int,
#                        default=315000000,
#                        help="Transmit frequency")

    ar, gs = parser.parse_known_args()

    ar.rolling = conv_int(ar.rolling)
    ar.id = conv_int(ar.id)
    ar.fixed = conv_int(ar.fixed)
    ar.button = conv_int(ar.button)

    return ar, gs


# Filetype: Flipper SubGhz Key File
# Version: 1
# Frequency: 315000000
# Preset: FuriHalSubGhzPresetOok650Async
# Protocol: Security+ 2.0
# Bit: 62
# Key: 00 00 3D 10 02 09 FA F6
# Secplus_packet_1: 00 00 3C 29 37 7F 38 F3

SUBGHZ_KEY_FILE_TYPE = "Flipper SubGhz Key File"


def read_file(fd):

    key_dat = pkt_dat = None
    header = fd.readline().strip()

    a = header.split(':', 1)
    if not (a[0].startswith("Filetype")
            and a[1].strip() == SUBGHZ_KEY_FILE_TYPE):
        print("invalid filetype")
        sys.exit(0)

    for line in fd:
        a = line.split(':', 1)

        if a[0].startswith("Protocol"):
            if a[1].strip() != "Security+ 2.0":
                print("invalid Protocol")
                sys.exit(0)

        if a[0].startswith("Key"):
            key_dat = a[1].strip().split()

        if a[0].startswith("Secplus_packet_1"):
            pkt_dat = a[1].strip().split()
            # replace(" ", "")

    if _debug:
        print("read_file", key_dat, pkt_dat)

    if key_dat and pkt_dat:
        return "".join(key_dat), "".join(pkt_dat)
        # return key_dat, pkt_dat

    return None, None


def print_file(rol, fix, fname=None, quiet=False, rf_freq=None):

    seq_v2 = Secplus.encode_v2(rol, fix)
    seq_v2_str = "".join(map(str, seq_v2))
    if _debug:
        print(seq_v2_str[:40], "---",  seq_v2_str[40:])

    ia = int("00000000001111" + "00" + seq_v2_str[:40], 2)
    ib = int("00000000001111" + "01" + seq_v2_str[40:], 2)

    ha = f"{ia:016X}"
    hb = f"{ib:016X}"
    # print(f"1: {ha}")
    # print(f"2: {hb}")

    p1_str = " ".join([ha[i:i + 2] for i in range(0, 16, 2)])
    p2_str = " ".join([hb[i:i + 2] for i in range(0, 16, 2)])

    tx_freq = rf_freq or TX_FREQ

    ret = f"""Filetype: Flipper SubGhz Key File
Version: 1
# Button:{fix>>32:02X} ({fix>>32}) Id:{fix&0xffffffff:08X} ({fix&0xffffffff}) Rolling:{rol:02X} ({rol})
# Generated with https://github.com/evilpete/flipper_toolbox
Frequency: {tx_freq}
Preset: FuriHalSubGhzPresetOok650Async
Protocol: Security+ 2.0
Bit: 62
Key: {p2_str}
Secplus_packet_1: {p1_str}
"""  # noqa

    if _debug:
        print(ret)

    if fname is None:
        fname = f"secv2-{fix:010X}.sub"
    elif os.path.isdir(fname):
        fname = f"{fname}/secv2-{fix:010X}.sub"

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

# {"time" : "@1.548164s", "model" : "Secplus-v2", "id" : 1959100928,
# "button_id" : 16, "remote_id" : 1959100928, "fixed" : "70678577664",
# "rolling" : "240124739"}
#
# { "time": "@1.198481s", "model": "Secplus-v2", "id": 1082192868,
# "button_id": 161, "remote_id": 1082192868, "fixed": "692571927524",
# "rolling": "24", "packet_1": "018c3492a980", "packet_2": "4804027ebd80",
# "mod": "ASK", "freq": 310.032,
# "rssi": -0.113, "snr": 25.31, "noise": -25.423 }


def grok_json(args):

    id_list = {}
    with open(args.json_log, 'r', encoding='UTF-8') as fd:
        js = {}
        for line in fd:
            try:
                js = json.loads(line)
            except json.JSONDecodeError as _e:
                if _debug:
                    print(_e.msg)
                    print(_e.doc)
                continue

            fid = js.get("fixed", None)
            rol = js.get("rolling", None)

            if fid is None or rol is None:
                continue

            id_list[fid] = js

    if _debug:
        pprint.pprint(id_list)

    for p in id_list.values():
        fr = p.get('freq', None)
        if fr:
            fr = int((fr//1) * 1000000)

        p_rolling = int(p['rolling'])
        p_fixed = int(p['fixed'])
        print_file(p_rolling, p_fixed, fname=args.outfname,
                   quiet=args.quiet, rf_freq=fr)


def main():

    rolling_out = fixed_out = 0

    args, _extra = arg_opts()

    if args.json_log:
        grok_json(args)
        return

    if _debug:
        print("args", args)
        print("_extra", _extra)

    if args.input_file:
        with open(args.input_file, 'r', encoding='UTF-8') as fd:
            xx, yy = read_file(fd)

        if xx:
            f_key = "".join(xx)
            b_key = f"{int(f_key, 16):08b}"

        if yy:
            f_pkt1 = "".join(yy)
            b_pkt1 = f"{int(f_pkt1, 16):08b}"

        if _debug:
            print(f_pkt1, " : ", f_key)
            print(b_pkt1[6:], " : ", b_key[6:])
            print(len(b_pkt1[6:]), len(b_key[6:]))

        full_pkt = b_pkt1[6:] + b_key[6:]

        if _debug:
            print("full =", full_pkt)

        full_pkt_list = list(map(int, list(full_pkt)))
        rolling_out, fixed_out, _data = Secplus.decode_v2(full_pkt_list)

    if _debug:  # and (fixed_out or rolling_out):
        print(f">> rolling_out  {rolling_out:12d} "
              f"{rolling_out:010X} {rolling_out:016b}")
        print(f">> fixed_out    {fixed_out:12d} "
              f"{fixed_out:010X} {fixed_out:040b}")
        pretty_out = Secplus.pretty_v2(rolling_out, fixed_out)
        print(">>", pretty_out)

    a_fixed = args.fixed or fixed_out
    # a_rolling = args.rolling or rolling_out

    r_button = args.button or (a_fixed >> 32) or 91  # 8 bits
    r_button &= 0xFF

    r_id = args.id or a_fixed or random.randint(2**23, 2**31)  # 32 bits id
    r_id &= 0xFFFFFFFF

    r_rolling = (args.rolling or rolling_out or 1) & 0x0FFFFFFF  # 28 bits max

    fixed_code = (r_id & 0xffffffff) | (r_button << 32)

    # button_code = random.randint(3, 172) | 0x01

    if _debug:
        print(f"r_button   {r_button:12d} {r_button:10X} {r_button:>08b}")
        print(f"r_id       {r_id:12d} {r_id:010X} {r_id:016b}")
        print(f"r_rolling  {r_rolling:12d} {r_rolling:010X} {r_rolling:016b}")
        print(f"fixed_code {fixed_code:12d} {fixed_code:010X} {fixed_code:040b}")  # noqa

    if not args.quiet:
        pretty_out = Secplus.pretty_v2(r_rolling, fixed_code)
        print(f"\n{pretty_out}\n")

    # only save to file if new of changed
    if (args.fixed or args.button or args.id or args.rolling) or not fixed_out:
        print_file(r_rolling, fixed_code, args.outfname, args.quiet)


if __name__ == '__main__':
    main()
