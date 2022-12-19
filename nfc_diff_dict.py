#!/usr/bin/env python3

# Quick script to diff two Flipper NFC dict lists

#
# nfc_diff_dict.py mf_classic_dict_user.nfc new-mf_classic_dict_user.nfc
#

import sys

file1 = sys.argv[1]
file2 = sys.argv[2]

COL = 6

print(file1, file2)

with open(file1, 'r', encoding="utf-8") as fd:
    list_A = [line.strip() for line in fd if line[0] != '#' and len(line) > 4]
print("list_A", len(list_A), file1)
set_A = set(list_A)

with open(file2, 'r', encoding="utf-8") as fd:
    list_B = [line.strip() for line in fd if line[0] != '#' and len(line) > 4]
print("list_B", len(list_B), file2)
set_B = set(list_B)

diff_AB = set_A.difference(set_B)
# print("diff_AB", diff_AB)
print("-------")
print("diff list_A - list_B =", len(diff_AB))


print(f"Unique to {file1}")
len_AB = len(diff_AB)
list_AB = sorted(list(diff_AB))
for X in range(1, len_AB, COL):
    print(" ".join(list_AB[X:X + COL]))

diff_BA = set_B.difference(set_A)
# print("diff_BA", diff_BA)
print("-------")
print("diff list_B - list_A =", len(diff_BA))


print(f"Unique to {file2}")
len_BA = len(diff_BA)
list_BA = sorted(list(diff_BA))
for X in range(1, len_BA, COL):
    print(" ".join(list_BA[X:X + COL]))
