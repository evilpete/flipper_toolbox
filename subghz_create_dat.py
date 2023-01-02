#!/usr/bin/env python3

# Based heavily on jinschoi/create_sub.py
# https://gist.github.com/jinschoi/f39dbd82e4e3d99d32ab6a9b8dfc2f55
#
# Peter Shipley github.com/evilpete
# From pkg https://github.com/evilpete/flipper_toolbox
#
# Added:
#    Fan Control + Brute force pin
#    FSK support
#

import sys
import os
from typing import Iterable, Union, Any

# pylint: disable=unspecified-encoding,too-many-arguments,too-many-locals,unused-argument

# freq: frequency in Hz
# zerolen: length of space bit in us
# onelen: length of mark bit in us
# repeats: number of times to repeat sequence
# pause: time to wait in us between sequences
# bits: string of ones and zeros to represent sequence

_verbose = 0

# listed in Firmware but not avalible (yet)
# FuriHalSubGhzPresetMSK99_97KbAsync
# FuriHalSubGhzPresetGFSK9_99KbAsync

# Preset: FuriHalSubGhzPreset2FSKDev238Async
# Preset: FuriHalSubGhzPreset2FSKDev476Async
# Preset: FuriHalSubGhzPresetOok270Async
# Preset: FuriHalSubGhzPresetOok650Async        <Default>

CommentText = "generated with flipper_toolbox"


def gen_sub(freq, zerolen, onelen, repeats, pause, bits, modu='Ook', srate=650, comment_text=CommentText):

    res = f"""Filetype: Flipper SubGhz RAW File
Version: 1
# {comment_text}
# generated with flipper_toolbox
Frequency: {freq}
Preset: FuriHalSubGhzPreset{modu}{srate}Async
Protocol: RAW
"""

    zerolen_off = zerolen % 1
    onelen_off = onelen % 1
    delta_off = 0.0

    zerolen = int(zerolen)
    onelen = int(onelen)

    if pause == 0:
        # Pause must be non-zero.
        pause = zerolen

    data = []
    prevbit = None
    prevbitlen = 0
    for bit in bits:
        if prevbit and prevbit != bit:
            data.append(prevbitlen)
            prevbitlen = 0

        if bit == '1':
            delta_off += onelen_off
            prevbitlen += onelen
            if delta_off > 1:
                prevbitlen += 1
                delta_off -= 1
        else:
            delta_off += zerolen_off
            prevbitlen -= zerolen
            if delta_off > 1:
                prevbitlen -= 1
                delta_off -= 1

        prevbit = bit

    if prevbit == '1':
        data.append(prevbitlen)
        data.append(-pause)
    else:
        data.append(prevbitlen - pause)

    # data = (data * repeats)[:-1] # Drop the last pause.
    datalines = []
    for i in range(0, len(data), 512):
        batch = [str(n) for n in data[i:i + 512]]
        datalines.append(f'RAW_Data: {" ".join(batch)}')
    res += '\n'.join(datalines)

    return res


# From Wikipedia
def de_bruijn(k: Union[Iterable[Any], int], n: int) -> str:
    """de Bruijn sequence for alphabet k
    and subsequences of length n.
    """
    # Two kinds of alphabet input: an integer expands
    # to a list of integers as the alphabet..
    if isinstance(k, int):
        alphabet = list(map(str, range(k)))
    else:
        # While any sort of list becomes used as it is
        alphabet = k
        k = len(k)

    a = [0] * k * n
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return "".join(alphabet[i] for i in sequence)


def debruijn(freq, zerolen, onelen, encoding, bitlen, alphabet=2):
    def encode(bit):
        return encoding[bit]
    return gen_sub(freq, zerolen, onelen, 1, 0, ''.join(encode(b) for b in de_bruijn(alphabet, bitlen)))


def gen_opensesame():
    # https://github.com/samyk/opensesame/blob/48b7d25c9d7aa3e2ac5cadfdcb2db1c78e001565/garages.h
    # 300000000, 310000000, 315000000, 318000000, 390000000, 433920000

    for hz in [300000000, 310000000]:
        with open(f'10bit-{hz//1000000}mhz.sub', 'w') as f:
            print(debruijn(hz, 500, 500, {'0': '1000', '1': '1110'}, 10), file=f)

    for hz in [315000000, 390000000]:
        with open(f'9bit-{hz//1000000}mhz.sub', 'w') as f:
            print(debruijn(hz, 500, 500, {'0': '1000', '1': '1110'}, 9), file=f)

    for hz in [318000000, 433920000]:
        with open(f'nscd-{hz//1000000}.sub', 'w') as f:
            print(debruijn(hz, 500, 500, {'0': '100000000100000000',
                                          '1': '111111110100000000',
                                          '2': '111111110111111110'}, 9, alphabet=3), file=f)


# pylint: disable=line-too-long
def gen_tesla():
    # https://github.com/jimilinuxguy/Tesla-Charging-Port-Opener
    with open('tesla.sub', 'w') as f:
        print(gen_sub(315000000, 400, 400, 10, 25562, '101010101010101010101010100010101100101100110010110011001100110011001011010011010010110101001010110100110100110010101011010010110001010110010110011001011001100110011001100101101001101001011010100101011010011010011001010101101001011000101011001011001100101100110011001100110010110100110100101101010010101101001101001100101010110100101'), file=f)


# see Also https://github.com/merbanan/rtl_433/blob/master/conf/fan-11t.conf

#  01 + 4 bit ID + 0 + 6 bit command
fan_comm = {
    'High': '100000',
    'Med':  '010000',
    'Low':  '001000',
    # '???':  '000100',   # not used ?
    'Off':  '000010',
    'Lit':  '000001',
}
fan_end = '000000'
fan_freq = 302500000

# DRATE 3015
# (1/3015) * 1000000 = ~333us
fan_bit_len = 333


def gen_fan_cmd(pin="1010"):
    """
    FAN-11T Remote Control of Harbor Breeze Fan
    """

    # Fan used PWM, to transmit as OOK we pad out the 1's and 0's
    # PWM into OOK
    # 1 = 011
    # 0 = 001
    fan_comm_end = ''.join(['011' if b == '1' else '001' for b in f"01{pin}0{fan_end}"])
    fan_space = '0' * 39

    if _verbose:
        print('end', fan_end)
        print('fan_end cmd_pwm', fan_comm_end)

    for k, v in fan_comm.items():

        f_cmd = ''.join(['011' if b == '1' else '001' for b in f"01{pin}0{v}"])

        # freq, zerolen, onelen, repeats, pause, bits
        # cmd_pwm = f'{fan_space}{f_cmd}'
        # full_pwm = (cmd_pwm * 5 + fan_space + fan_comm_end  + fan_space) * 2
        cmd_pwm = f'{f_cmd}{fan_space}'
        full_pwm = (cmd_pwm * 5 + fan_comm_end + fan_space) * 2
        # print('fan_{}.sub'.format(k), fan_comm[k])
        if _verbose:
            print(k, v)
            print(f'fan_{k} cmd_pwm', cmd_pwm)
            # print("xmit us:", len(full_pwm) * fan_bit_len)
            # print(f'fan_{k} full_pwm', full_pwm)

        with open(f'fan_{k}-{pin}.sub', 'w') as f:
            # gen_sub(freq, zerolen, onelen, repeats, pause, bits)
            print(gen_sub(fan_freq, fan_bit_len, fan_bit_len, 1, 0, full_pwm), file=f)


def gen_fan_brute():
    """
    FAN-11T Remote Control of Harbor Breeze Fan

    Brute Force 4 bit pin code
    """

    fan_space = "0" * 39

    # Fan used PWM, to transmit as OOK we pad out the 1's and 0's
    # PWM into OOK
    # 1 = 011
    # 0 = 001

    # if _verbose:
    #    print('end', fan_end)
    #    print('fan_end cmd_pwm', fan_comm_end)

    for k, v in fan_comm.items():

        pwm_dat = []

        for p in range(16):

            pin = f"{p:04b}"

            f_cmd = ''.join(['011' if b == '1' else '001' for b in f"01{pin}0{v}"])
            fan_cmd_end = ''.join(['011' if b == '1' else '001' for b in f"01{pin}0{fan_end}"])

            cmd_pwm = f'{f_cmd}{fan_space}'
            full_pwm = (cmd_pwm * 4 + fan_cmd_end + fan_space) * 2

            pwm_dat.append(full_pwm)

            if _verbose:
                print(k, pin, v)
                print(f'fan_{k} cmd_pwm', cmd_pwm)
                # print(f'fan_{k} full_pwm', full_pwm)

        if _verbose:
            print(k, "xmit us:", len("".join(pwm_dat)) * fan_bit_len)

        with open(f'fan_brute-{k}.sub', 'w') as f:
            # gen_sub(freq, zerolen, onelen, repeats, pause, bits)
            print(gen_sub(fan_freq, fan_bit_len, fan_bit_len, 1, 0, "".join(pwm_dat), comment_text=f"FAN-11T Remote Control {k}"), file=f)


TOUCH_TUNES_COMMANDS = {
    'On_Off': 0x78,
    'Pause': 0x32,  # 0xB3,
    'P1': 0x70,  # 0xF1,
    'P2_Edit_Queue': 0x60,
    'P3_Skip': 0xCA,
    'F1_Restart': 0x20,
    'F2_Key': 0xA0,
    'F3_Mic_A_Mute': 0x30,
    'F4_Mic_B_Mute': 0xB0,
    'Mic_Vol_Plus_Up_Arrow': 0xF2,
    'Mic_Vol_Minus_Down_Arrow': 0x80,
    'A_Left_Arrow': 0x84,
    'B_Right_Arrow': 0xC4,
    'OK': 0x44,  # 0xDD,
    'Music_Vol_Zone_1Up': 0xD0,  # 0xF4,
    'Music_Vol_Zone_1Down': 0x50,
    'Music_Vol_Zone_2Up': 0x90,  # 0xF6,
    'Music_Vol_Zone_2Down': 0x10,
    'Music_Vol_Zone_3Up': 0xC0,  # 0xFC,
    'Music_Vol_Zone_3Down': 0x40,
    '1': 0xF0,
    '2': 0x08,
    '3': 0x88,
    '4': 0x48,
    '5': 0xC8,
    '6': 0x28,
    '7': 0xA8,
    '8': 0x68,
    '9': 0xE8,
    '0': 0x98,
    'Music_Karaoke(star)': 0x18,
    'Lock_Queue(#)': 0x58
}


def encode_touchtunes(command, pin=0x00):
    # Syncword
    frame = 0x5D

    # PIN
    for bit in range(8):
        frame <<= 1
        if pin & (1 << bit):
            frame |= 1
    # Insert button code and it's complement
    frame <<= 16
    frame |= (command << 8)
    frame |= (command ^ 0xFF)

    # Convert to raw signal
    # 0 symble == 10 && 1 symble == 1000
    ook = ""
    for _i in range(8 + 8 + 16):
        if frame & 0x80000000:
            ook += "1000"
            frame <<= 1
        else:
            ook += "10"
            frame <<= 1
    return "1" * 16 + "0" * 8 + ook + "1000"


# Touch Tunes jukebox (https://github.com/notpike/The-Fonz/blob/master/The_Fonz.py)
def gen_touch_tunes(pin=0):
    # pin 0->255

    dirname = f"touch_tunes-{pin:03d}"
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    # Touch Tunes jukebox (https://github.com/notpike/The-Fonz/blob/master/The_Fonz.py)
    for cmdname, cmd in TOUCH_TUNES_COMMANDS.items():
        with open(dirname + '/' + cmdname + '.sub', 'w') as f:
            print(gen_sub(433920000, 566, 566, 1, 0, encode_touchtunes(cmd, pin)), file=f)


if __name__ == '__main__':

    targ = "all"
    args = sys.argv[1:]

    if args:
        targ = args.pop(0)

    # Garage Door opener
    if targ in ["all", "opensesame"]:
        gen_opensesame()

    # Tesla-Charging-Port-Opener
    if targ in ["all", "tesla"]:
        gen_tesla()

    # Touch Tunes jukebox
    if targ in ["all", "ttones"]:
        gen_touch_tunes()

    # FAN-11T Remote Control of Harbor Breeze Fan ( with pin )
    # gen_fan_cmd("1010")

    # FAN-11T Remote Control of Harbor Breeze Fan
    # Brute Force Pin
    if targ in ["all", "fan"]:
        gen_fan_brute()

    sys.exit()
