#!/usr/local/bin/python3
"""
    Adds int and hex to RFID HEX dump
    [a 2 min script]

    rnfc.py file.nfc

    Written By: Peter Shipley github.com/evilpete
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

with open(sys.argv[1]) as fd:
    for l in fd:
        a = l.split()
        if a[0] in ["Page", "Block"]:
            b = [int(x, 16) for x in a[2:]]
            # b = [int(a[2], 16), int(a[3], 16), int(a[4], 16), int(a[5], 16)]
            c = [ "-" if x < 32 or x > 126 else chr(x) for x in b]
            d = " ".join(c)
            e = [f"{x:3d}" for x in b]
            f = " ".join(e)
            # e =  "{:3d} {:3d} {:3d} {:3d}".format( *b)
            print(l.rstrip(), '#  ', d, '\t', f)
            # print(e)
            # A.extend(e)
        else:
            print(l, end='')

# print("".join(A))
