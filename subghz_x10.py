#!/usr/bin/env python3

import sys

#
#  Generate X10 RF command in Flipper .sub format
#
# Peter Shipley github.com/evilpete
#
# From pkg https://github.com/evilpete/flipper_toolbox
#

# Usage;
#      ./subghz_x10.py <dst_node_addr><src_node_addr> [On|Off]
#
# Example:
#      ./subghz_x10.py B10 on
#


_debug = 1


houseCodes = {
    "A": 0x60,     #  01100000
    "B": 0x70,     #  01110000
    "C": 0x40,     #  01000000
    "D": 0x50,     #  01010000
    "E": 0x80,     #  10000000
    "F": 0x90,     #  10010000
    "G": 0xA0,     #  10100000
    "H": 0xB0,     #  10110000
    "I": 0xE0,     #  11100000
    "J": 0xF0,     #  11110000
    "K": 0xC0,     #  11000000
    "L": 0xD0,     #  11010000
    "M": 0x00,     #  00000000
    "N": 0x10,     #  00010000
    "O": 0x20,     #  00100000
    "P": 0x30,     #  00110000
}

unit_code = {      #       3    2 01
    "": 0x0000,   #  00000000 00000000
    "1": 0x0000,   #  00000000 00000000
    "2": 0x0010,   #  00000000 00010000
    "3": 0x0008,   #  00000000 00001000
    "4": 0x0018,   #  00000000 00011000
    "5": 0x0040,   #  00000000 01000000
    "6": 0x0050,   #  00000000 01010000
    "7": 0x0048,   #  00000000 01001000
    "8": 0x0058,   #  00000000 01011000
    "9": 0x0400,   #  00000100 00000000
    "10": 0x0410,  #  00000100 00010000
    "11": 0x0408,  #  00000100 00001000
    "12": 0x0400,  #  00000100 00000000
    "13": 0x0440,  #  00000100 01000000
    "14": 0x0450,  #  00000100 01010000
    "15": 0x0448,  #  00000100 01001000
    "16": 0x0458,  #  00000100 01011000
}

cmd_code = {
    "ON": 0x00,          # 00000000
    "OFF": 0x20,         # 00100000
    "BRT": 0x88,         # 10001000
    "DIM": 0x98,         # 10011000
    "ALL-OFF": 0x80      # 10000000
    # "ALL-LTS-ON": 0x80 # 10010000
}


def gen_x10(targ_house, targ_unit, targ_cmd):
    # print("\n\ngen_x10")

    result = [0, 0]

    result[0] = houseCodes[targ_house]
    # print(f"\t{result[0]:08b} {result[1]:08b} house")

    #deviceNumber = deviceNumbers[targ_unit]
    #result[0] |= deviceNumber[0]
    #print(f"\t{result[0]:08b} {result[1]:08b} unit")
    #result[1] = deviceNumber[1]
    #print(f"\t{result[0]:08b} {result[1]:08b} unit")

    if targ_unit and targ_cmd not in ["ALL-OFF"," BRT", "DIM"]:
        result[0] |= (unit_code[targ_unit] >> 8) & 0xff
        result[1] |= unit_code[targ_unit] & 0xff

    result[1] |= cmd_code[targ_cmd] & 0xff

    # print(f"\t{result[0]:08b} {result[1]:08b} cmd")

    return result


def print_subfile(pkt_bits):

    print("print_subfile")

    data = [9000, -4500]

    for bit in pkt_bits:
        data.append(562)
        if bit == '1':
            data.append(-563)
        else:
            data.append(-1688)


    data.append(562)
    data.append(-40000)

    print("data", len(data))
    print(pkt_bits[:5])
    print(data[2:7])

    hdr = """Filetype: Flipper SubGhz RAW File
Version: 1
Frequency: 310000000
Preset: FuriHalSubGhzPresetOok650Async
Protocol: RAW
"""

    res = hdr
    datalines = []
    for i in range(0, len(data), 512):
        # batch = [str(n) for n in data[i:i + 512]]
        batch = map(str, data[i:i + 512])
        datalines.append(f'RAW_Data: {" ".join(batch)}')
    res += '\n'.join(datalines) + '\n'
    res += '\n'.join(datalines) + '\n'
    res += '\n'.join(datalines) + '\n'
    res += '\n'.join(datalines) + '\n'

    return res


if __name__ == '__main__':

    args = sys.argv[1:]

    if len(args) < 2:
        print("requires 2 or more args")
        sys.exit()

    node_targ = args.pop(0).upper()

    node_house = node_targ[0]
    node_unit = node_targ[1:]

    node_cmd = args.pop(0).upper()
    if node_cmd == "BRIGHT":
        node_cmd = "BRT"
    elif node_cmd in ["ALL_OFF", "ALLOFF"]:
        node_cmd = "ALL-OFF"

    if not (node_house and node_house in houseCodes):
        print("Unknown House code:", node_house)
        sys.exit()

    if node_cmd not in cmd_code:
        print("Unknown command code:", node_cmd)
        print("\tValid command are:", " ".join(cmd_code))
        sys.exit()

    rr = gen_x10(node_house, node_unit, node_cmd)

    pkt_data = f"{rr[0]:08b}{rr[0]^0xff:08b}{rr[1]:08b}{rr[1]^0xff:08b}"

    if _debug:
        print("pkt_data", pkt_data)

    fdata = print_subfile(pkt_data)

    filen = f"{node_house}{int(node_unit):02d}_{node_cmd}.sub"

    with open(filen, "w", encoding="utf-8") as fd:
        print(fdata, file=fd)

    sys.exit()
