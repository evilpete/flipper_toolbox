#!/bin/bash

dest='IR/All-Codes'

test ${PWD##*/} == 'IR' && dest='All-Codes'
test -t 1 && echo "dest dir: ${dest}"

mkdir -p ${dest}
pushd ${dest}

../../ir_gen_all_codes.py  NEC 00 00
../../ir_gen_all_codes.py  NEC 02 00
../../ir_gen_all_codes.py  NEC 04 00
../../ir_gen_all_codes.py  NEC 40 00
../../ir_gen_all_codes.py  NEC 50 00
../../ir_gen_all_codes.py  NECext 00 00
../../ir_gen_all_codes.py  NECext 00 7F
../../ir_gen_all_codes.py  NECext 02 00
../../ir_gen_all_codes.py  NECext 84 00
../../ir_gen_all_codes.py  NECext 85 00
../../ir_gen_all_codes.py  NECext 86 00
../../ir_gen_all_codes.py  NECext EA 00
../../ir_gen_all_codes.py  RC5 00 00
../../ir_gen_all_codes.py  RC5 03 00
../../ir_gen_all_codes.py  RC5 30 00
../../ir_gen_all_codes.py  RC6 00 00
../../ir_gen_all_codes.py  SIRC 01 00 00 00
../../ir_gen_all_codes.py  SIRC 10 00 00 00
../../ir_gen_all_codes.py  SIRC15 1A 00 00 00
../../ir_gen_all_codes.py  SIRC15 77 00 00 00
../../ir_gen_all_codes.py  SIRC15 97 00 00 00
../../ir_gen_all_codes.py  SIRC15 A4 00 00 00
../../ir_gen_all_codes.py  Samsung32 00 00 00 00
../../ir_gen_all_codes.py  Samsung32 06 00 00 00
../../ir_gen_all_codes.py  Samsung32 07 00 00 00
../../ir_gen_all_codes.py  Samsung32 08 00 00 00
../../ir_gen_all_codes.py  Samsung32 0B 00 00 00
../../ir_gen_all_codes.py  Samsung32 0E 00 00 00
../../ir_gen_all_codes.py  Samsung32 37 07 00 00
popd
