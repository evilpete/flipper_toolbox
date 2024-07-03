#!/usr/bin/env python3
"""
    Adds int and hex to RFID HEX dump
    [a 2 min script]

    nfc_hexdump.py file.nfc

    Written By: Peter Shipley github.com/evilpete

    From pkg https://github.com/evilpete/flipper_toolbox
"""
# In
#    Page 4: 03 29 91 01
#    Page 5: 15 55 04 79
#    Page 6: 6F 75 74 75
#    Page 7: 2E 62 65 2F

# Out
#    Page 4: 03 29 91 01 #   - ) - -         3  41 145   1
#    Page 5: 15 55 04 79 #   - U - y        21  85   4 121
#    Page 6: 6F 75 74 75 #   o u t u       111 117 116 117
#    Page 7: 2E 62 65 2F #   . b e /        46  98 101  47

import sys

A = []

Chr = True      # print as ascii char
Dec = False     # print as decimal
Bin = True      # print as binary
Rev = False     # reverse bit order

av = sys.argv[1:]

if av[0][0] == '-':
    Chr = Dec = Bin = Rev = False

while av[0][0] == '-':
    arg = av.pop(0)

    if arg == '-r':
        Rev = True
    elif arg == '-b':
        Bin = True
    elif arg == '-d':
        Dec = True
    elif arg == '-c':
        Chr = True


filename = av.pop(0)
with open(filename, encoding="utf-8") as fd:
    header = fd.readline().strip()
    if header != 'Filetype: Flipper NFC device':
        print(f"Error: {filename} is not a 'Flipper NFC' sample file'")
        # sys.exit(1)
    for line in fd:
        a = line.split()
        if a[0] in ["Page", "Block"]:
            out_list = []
            # b = [int(x, 16) for x in a[2:]]
            if Rev:
                b = [00 if x == '??' else int(f"{int(x, 16):08b}"[::-1], 2) for x in a[2:]]
            else:
                b = [00 if x == '??' else int(x, 16) for x in a[2:]]

            if Chr:
                # b = [int(a[2], 16), int(a[3], 16), int(a[4], 16), int(a[5], 16)]
                c = ["-" if x < 32 or x > 126 else chr(x) for x in b]
                d = " ".join(c)
                out_list.append(d)

            if Dec:
                e = [f"{x:3d}" for x in b]
                f = " ".join(e) + ' '
                out_list.append(f)

            if Bin:
                # e =  "{:3d} {:3d} {:3d} {:3d}".format(*b)
                g = " ".join([f"{x:08b}" for x in b])
                out_list.append(g)

            # print(line.rstrip(), '#  ', d, '\t', f, '\t', g)
            print(line.rstrip(), '#\t', '    '.join(out_list))
            # print(e)
            # A.extend(e)
        else:
            print(line, end='')

# print("".join(A))
