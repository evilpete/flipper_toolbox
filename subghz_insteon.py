#!/usr/bin/env python3

import sys
# import argparse
# import string
# import pprint

#
#  Generate Insteon command packets in Flipper .sub format
#
# Peter Shipley github.com/evilpete
#
# From pkg https://github.com/evilpete/flipper_toolbox
#

# Usage;
#      ./subghz_insteon.py <dst_node_addr> <src_node_addr> [On|Off]
#
# Example:
#      ./subghz_insteon.py 163FE5 132580 Off > device_off.sub
#


# Note:
#
# an insteon switch needs to be "paired" before it will accept command from
# andother device,  but there is no authenticaion or encryption.
#
# the easiest way to get the insteon node id/address of a pair is to run rtl_433
#
#    rtl_433 -f 914.8M -s 2048k -R 159 -Y classic
#
# rtl_433 output:
# _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
# time      : 2022-11-28 21:36:45
# model     : Insteon      From_Addr : 4C1B63        To_Addr   : 347864        Message_Type: 0
# Message_Str: Direct Message                        Extended  : 0             Hops_Max  : 3
# Hops_Left : 0            Packet    : 03 : 247864 : 4C1B61 : 13 00  BE        Integrity : CRC
# Payload   : 03647824611B4C1300BE00

# the run the command :
#
#     ./subghz_insteon.py 4C1B63 347864 Off > office_light_off.sub
#

# Insteon Packet encoding format :
#
#    Packet encoding example
#
#    The short Packet Fields are
#        Flags     = byte 0
#        To Addr   = byte 1 2 3
#        From Addr = byte 4 5 6
#        Command   = byte 7
#        Cmd Arg   = byte 8
#        Pkt CRC   = byte 9
#        pad 00    = byte 10 11 ( optional )
#        pad AA    = byte 12    ( optional )
#

_debug = 0

lsfr_table = [0x00, 0x30, 0x60, 0x50,  # 0 1 2 3
              0xC0, 0xF0, 0xA0, 0x90,  # 4 5 6 7
              0x80, 0xB0, 0xE0, 0xD0,  # 8 9 A B
              0x40, 0x70, 0x20, 0x10]  # C D E F

cmd_table = {
    "ON": (0x11, 255),
    "FASTON": (0x12, None),
    "OFF": (0x13, None),
    "FASTOFF": (0x14, None),
    'BRIGHTEN': (0x15, None),
    "BRT": (0x15, None),
    "DIM": (0x16, None),
    "FADEDOWN": (0x17, 0),
    "FADEUP": (0x17, 1),
    "STOP": (0x18, 0),
    "FADESTOP": (0x18, 0),
    "BEEP": (0x30, None),
    "PING": (0x0F, None),
}


def pkt_crc(dat):
    """
        calc packet CRC

        takes an instion packet in form of a list of ints
        and returns the CRC for RF packet

        This uses a table lookup to effectivly doing:
            r ^= dat[i] ;
            r ^= (( r ^ ( r << 1 )) & 0x0F) << 4 ;

    """

    r = 0
    for i in dat[:9]:
        r ^= i
        r ^= lsfr_table[r & 0x0F]

    return r


def percent_to_byte(p_str, def_val=255):
    if p_str.isdigit():
        p = int(p_str)
        r = int(p * 255 / 100)
        return min(r, 255)

    return def_val


# takes a list representig a insteon rf command bytes / payload
# and generates a rf binary in the form of a string
def insteon_encode(b_list, repeat=3):
    # l = len(b_list)

    padding = ''.join(['10' if b == '1' else '01' for b in "0101" * 13])

    aa = ''.join(['10' if b == '1' else '01' for b in "01010101"])
    blks = [aa]
    i = 0
    for x in b_list:
        if i == 0:
            ix = 31
        else:
            ix = 12 - i
        i += 1

        d = x

        ibr = f"{ix:05b}"[::-1]
        dbr = f"{d:08b}"[::-1]

        if _debug > 1:
            print("00", ibr, dbr, " : ", ix, f"{x:02X}", file=sys.stderr)

        # ib = f"{ix:05b}"
        # db = f"{d:08b}"
        # print(ix, cmd_hex[x:x+2], ib, db, '->', ibr, dbr)

        md = ''.join(['10' if b == '1' else '01' for b in f"{ibr}{dbr}"])
        if _debug > 1:
            print("md=", md, file=sys.stderr)
        blks.append('00' + md)

    inst_pkt = ''.join(blks)

    ret_list = [inst_pkt]

    for i in range(1, repeat):
        ret_list.extend((padding, inst_pkt))

    # print(ret_list)
    return ret_list


hex_set = set('abcdefABCDEF0123456789')


def is_hex_str(s):
    return set(s).issubset(hex_set)


# takes a list representig a insteon rf command bytes
def gen_insteon_pkt():

    pkt_list = [0x0F]

    args = sys.argv[1:]

    if _debug > 1:
        print("args", args, file=sys.stderr)

    if len(args) < 3:
        print("requires three or more args")
        sys.exit()

    # dest addr
    addr = args.pop(0)

    a = [addr[4:6], addr[2:4], addr[0:2]]
    # pkt_list.extend([int(x, 16) for x in a])
    pkt_list.extend(map(lambda x: int(x, 16), a))

    # src addr
    addr = args.pop(0)

    if addr.startswith('0000'):
        pkt_list[0] = 0xCF

    a = [addr[4:6], addr[2:4], addr[0:2]]
    pkt_list.extend(map(lambda x: int(x, 16), a))
    # pkt_list.extend([int(x, 16) for x in a])

    cmd = args.pop(0)
    cmd_arg = None

    if cmd.upper() in cmd_table:
        c1, cmd_arg = cmd_table[cmd.upper()]
        pkt_list.append(c1)
    elif is_hex_str(cmd):
        pkt_list.append(int(cmd, 16) & 0xff)
    else:
        print(f"unknown cmd value '{cmd}'")
        print("valid commands are:'")
        print("\t", " ".join(cmd_table.keys()))
        sys.exit()

    if args:
        arg = args.pop(0)
        if is_hex_str(arg):
            val = int(arg, 16)
            pkt_list.append(val)
            #     val = percent_to_byte(arg[1:])
        else:
            print(f"unknown arg value '{arg}'")
            sys.exit()
    elif cmd_arg is not None:
        pkt_list.append(cmd_arg)
    else:
        pkt_list.append(0)

    p_crc = pkt_crc(pkt_list)

    pkt_list.extend([p_crc, 0, 0, 0xAA])

    if _debug > 1:
        print("pkt_list", pkt_list, file=sys.stderr)
        # hex_str_list = [f"{x:02X}" for x in pkt_list]
        hex_str_list = list(map(lambda x: f"{x:02X}", pkt_list))
        print(hex_str_list, file=sys.stderr)
        print("".join(hex_str_list), file=sys.stderr)

    return pkt_list


# takes a rf binary in the form of a string
# and generates a Flipper SubGhz encoded file
def print_subfile(pkt_list, note="Insteon Command"):

    pkt_bit_len = 109.2

    bit_len = int(pkt_bit_len)
    bit_len_off = pkt_bit_len % 1
    delta_off = 0.0

    data_list = []
    for pkt_bits in pkt_list:

        data = []
        prevbit = None
        prevbitlen = 0

        for bit in pkt_bits:
            if prevbit and prevbit != bit:
                data.append(prevbitlen)
                prevbitlen = 0

            if bit == '1':
                delta_off += bit_len_off
                prevbitlen += bit_len
                if delta_off > 1:
                    prevbitlen += 1
                    delta_off -= 1
            else:
                delta_off += bit_len_off
                prevbitlen -= bit_len
                if delta_off > 1:
                    prevbitlen -= 1
                    delta_off -= 1

            prevbit = bit

        data.append(prevbitlen)

        data_list.append(data)

    hdr = f"""Filetype: Flipper SubGhz RAW File
Version: 1
# {note}
# Generated with subghz_insteon.py https://github.com/evilpete/flipper_toolbox
Frequency: 915000000
Preset: FuriHalSubGhzPreset2FSKDev476Async
Protocol: RAW
"""

    res = hdr
    datalines = []
    for data in data_list:
        for i in range(0, len(data), 512):
            # batch = [str(n) for n in data[i:i + 512]]
            batch = map(str, data[i:i + 512])
            datalines.append(f'RAW_Data: {" ".join(batch)}')

    res += '\n'.join(datalines)

    return res


if __name__ == '__main__':

    p_list = gen_insteon_pkt()

    hexstr = ' '.join([f"{x:02X}" for x in p_list])

    if _debug:
        print("p_list", p_list, file=sys.stderr)
        # print([f"{x:02X}" for x in p_list], file=sys.stderr)
        print(hexstr, file=sys.stderr)

    pkt_data = insteon_encode(p_list)

    if _debug > 1:
        print("pkt_data", pkt_data, file=sys.stderr)

    file_comment = "Insteon command : " + \
                   ' '.join(sys.argv[1:]).upper()  + " : " + hexstr

    fdata = print_subfile(pkt_data, note=file_comment)

    print(fdata)

    sys.exit()
