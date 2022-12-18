#!/usr/bin/env python3
"""
    ir_gen_all_codes.py (was gen_all_ir_codes.py)
    Generates file Flipper IR file will all command codes

    Written By: Peter Shipley github.com/evilpete

    From pkg https://github.com/evilpete/flipper_toolbox
"""

import sys

MAX_BUTTONS = 256

CMD_LEN = {
    'RC5':    63,      # 6 x40
    'RC5X':    127,    # 7 x80
    'RC6':     256,    # 8 x100
    'NEC':     255,    # 8
    # 'NECext':  255,  # 16 x10000
    'NECext':  65536,  # 16 x10000
    'NEC42':   255,    # 8
    # 'NEC42ext': 65536,   # 16
    'Samsung32': 255,  # 8
    'SIRC':   255,     # 8
    'SIRC15': 255,     # 8
    'SIRC20': 255,     # 8
}

hex_set = set('abcdefABCDEF0123456789')


def is_hex_str(s):
    return set(s).issubset(hex_set)


if __name__ == '__main__':

    if len(sys.argv) < 4:
        print(f"""
        Requires 3 args:
            {sys.argv[0]} PROTO ADDR SUBA

            {sys.argv[0]} NEC 40 00

            Valid proto {' '.join(CMD_LEN.keys())}
        """)
        sys.exit(1)

    PROTO = sys.argv[1]
    ADDR = sys.argv[2].upper()
    SUBA = sys.argv[3].upper()

    if PROTO not in CMD_LEN:
        print("Invalid IR Protocal")
        print(f"Valid proto {' '.join(CMD_LEN.keys())}")
        sys.exit(1)

    if ADDR.startswith('0X'):
        ADDR = ADDR[2:]

    if SUBA.startswith('0X'):
        SUBA = SUBA[2:]

    if not (is_hex_str(ADDR) and int(ADDR, 16) < 255  # noqa
            and is_hex_str(SUBA) and int(SUBA, 16) < 255):
        print("Invalid IR address or sub-address")
        print("Valid values hex 00 -> FF")
        sys.exit(1)

    if CMD_LEN[PROTO] > MAX_BUTTONS:
        print(f"limiting commands values to under {MAX_BUTTONS -1}")

    out_filen = f"IR-{PROTO}-{ADDR}-{SUBA}.ir"

    print(f"Creating file: {out_filen}")

    with open(out_filen, "w", encoding="utf-8") as fd:

        fd.write("Filetype: IR signals file\nVersion: 1\n")
        fd.write("# generated with flipper_toolbox\n")

        # 256 button limit ( do you want 65536 buttons? )
        cmd_limit_cnt = min(MAX_BUTTONS, CMD_LEN[PROTO])

        for i in range(cmd_limit_cnt, -1, -1):
            fd.write(f"#\nname: Code_{i:03d}\ntype: parsed\n"
                     f"protocol: {PROTO}\naddress: {ADDR} {SUBA} 00 00\n"
                     f"command: {i & 0xFF:02X} {(i >> 8) & 0xFF:02X} 00 00\n")

    sys.exit(0)
