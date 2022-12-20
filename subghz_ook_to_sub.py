#!/usr/bin/env python3

#
# Peter Shipley github.com/evilpete
#
# From pkg https://github.com/evilpete/flipper_toolbox
#
#     convert .ook files produced by rtl_433 to the Flipper .sub format

#
# Usage:
#        subghz_ook_to_sub.py FILENAME [freq]")
#
#  default freq 433920000 [433.92Mhz]
#
#


#  to convert unsigned 8-bit sdr data do the following:
#
#   convert rtl-sdr raw data file into .ook file with rtl_sdr
#   (this will partially demodulate the data)
#
#      rtl_443 -r rtl_sample.cu8 -w rf_sample.ook
#
#   convert the .ook file into a Flipper .sub file
#
#      subghz_ook_to_sub.py rf_sample.ook
#
#   this will generate the file rf_sample.sub
#
#   Note: you may have to manually set the frequancy on the
#         command line or by editing the file

#
#  With multiple packets per ook file:
#  currently only reads first header and assumes all
#  following packets use same modulation


# To do:
#   parse header
#   split samples into multiple files (opton)
#   data validation
#   .fsk file format ?
#   insert breaks between pkts


import sys
import os
import pprint
import argparse

MIN_PULSES = 25

filen = None
rf_freq = 0


rf_freq_default = 433920000

verbose = 0

_debug = 0

# ;pulse data
# ;version 1
# ;timescale 1us
# ;created 2022-11-14 13:59:15-0800
# ;ook 21 pulses
# ;freq1 -75324
# ;centerfreq 0 Hz
# ;samplerate 250000 Hz
# ;sampledepth 8 bits
# ;range 42.1 dB
# ;rssi -0.1 dB
# ;snr 8.0 dB
# ;noise -8.1 dB
# 532 1492


def arg_opts():

    parser = argparse.ArgumentParser(add_help=True, allow_abbrev=True,  # noqa
                        description="Convert rtl_443 .ook format files into .sub format",  # noqa
                        formatter_class=argparse.RawDescriptionHelpFormatter
                        )
    # argument_default=argparse.SUPPRESS,

    parser.add_argument("-m", "-min", metavar='pulses',  dest="min_pulses",
                        default=None,
                        help="minimum number of signal pulses")

    parser.add_argument('-v', '--verbose', dest="verb",
                        default=0,
                        help='Increase debug verbosity', action='count')

    parser.add_argument("-f", "--freq", metavar='frequency', dest="freq",
                        default=None,
                        help="use frequency instead")

    parser.add_argument("-F", "--Freq", metavar='frequency',
                        dest="default_freq",
                        default=None,
                        help=f"default frequency: {rf_freq_default}")

    parser.add_argument("-o", "--out", metavar='output_filename',
                        dest="outfname",
                        default=None,
                        help="output filename")

    # parser.add_argument("-p", "--preface", metavar='preface_duration',
    #                     dest="preface_time",
    #                     default=None,
    #                     type=int,
    #                     help="insert a preface signal (in μs)")

    parser.add_argument("input_file", metavar='input-file', nargs='?',
                        default=None,
                        help="file file in .ook format")

    ar, gs = parser.parse_known_args()

    return ar, gs


def chunks(lst, n=500):
    """Yield successive 500-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


RF_PRESETS = {
    'ook': "FuriHalSubGhzPresetOok650Async",
    'fsk': "FuriHalSubGhzPreset2FSKDev476Async",
}
# Preset: FuriHalSubGhzPreset2FSKDev238Async
# Preset: FuriHalSubGhzPreset2FSKDev476Async
# Preset: FuriHalSubGhzPresetOok270Async
# Preset: FuriHalSubGhzPresetOok650Async


def gen_sub(freq, rf_samples):

    if _debug:
        print("\n\n\nrf_samples", rf_samples)

    dat = rf_samples[0].get('header')

    if _debug:
        print(f"header {dat}")

    comment_text = "generated with ook_to_sub.py"

    rf_Preset = None
    # Preset: FuriHalSubGhzPreset2FSKDev238Async
    # Preset: FuriHalSubGhzPreset2FSKDev476Async
    # Preset: FuriHalSubGhzPresetOok270Async
    # Preset: FuriHalSubGhzPresetOok650Async

    rf_Preset = RF_PRESETS.get(dat['modulation'], None)

    if rf_Preset is None:
        print("Can't determine modulation type from header")
        print(dat)
        sys.exit(1)

    try:
        if rf_freq:
            freq = rf_freq
        else:
            fhz = dat.get('centerfreq', '0 Hz').split()[0]
            fhz = int(fhz)
            if fhz:
                freq = fhz
            else:
                freq = rf_freq_default
                print(f"Using default frequency {rf_freq_default}")
    except ValueError:
        freq = rf_freq_default

    res = f"""Filetype: Flipper SubGhz RAW File
Version: 1
# {comment_text}
Frequency: {freq}
Preset: {rf_Preset}
Protocol: RAW
"""

    data = []
    raw_data = []

    # if args.preface_time:
    #     raw_data.append(str(args.preface_time * -1))

    for ds in rf_samples:
        data = []
        dat = ds.get('data', [])

        for d in dat:
            a = list(map(int, d.split()))
            a[1] *= -1
            if a[0] == 0:
                del a[0]
            elif a[1] == 0:
                del a[1]
            data += a

        data = list(map(str, data))

        for i in chunks(data):
            raw_data.append(f'RAW_Data: {" ".join(i)}')

    res += '\n'.join(raw_data)

    return res


def skip_to_next(ffd, symb=";end"):
    for line in ffd:
        if line.startswith(symb):
            return


def main():

    # file_header = {}

    ook_Headers = [";pulse data"]
    # samp_mod = ""
    # samp_freq1 = 0
    # samp_freq2 = 0

    pulse_samples = []
    dat_sample = None

    if _debug:
        print(f"open {filen}")

    with open(filen, 'r', encoding="utf-8") as fd:

        header = fd.readline().strip()
        if header not in ook_Headers:
            print(f"Error: {filen} is not a 'rtl_443 ook' data file")
            sys.exit(1)

        for line in fd:

            if line.startswith(';end'):
                if _debug:
                    print("\n\ndat_sample", dat_sample)
                    print("pulse_samples", pulse_samples)

                if verbose:
                    print(f"Adding packet with {file_header['pulses']} pulses")

                dat_sample = None
                continue

            if dat_sample is None:
                dat_sample = {}
                dat_sample['header'] = file_header = {}
                dat_sample['data'] = pulse_data = []
                pulse_samples.append(dat_sample)

            if line.startswith(';ook') or line.startswith(';fsk'):
                a = line[1:].strip().split(None, 2)
                if a[1].isnumeric():
                    if int(a[1]) < MIN_PULSES:
                        if verbose:
                            print(f"skipping packet with {a[1]} pulses")
                        skip_to_next(fd)
                        continue

                    file_header['pulses'] = int(a[1])
                    file_header['modulation'] = a[0]

            if line[0] == ';':
                a = line[1:].strip().split(None, 1)
                file_header[a[0]] = a[1]
                continue

            pulse_data.append(line.strip())

    print("Total packets in file",  len(pulse_samples))

    sub_data = gen_sub(rf_freq, pulse_samples)

    if _debug or verbose > 2:
        # print(f"\n\n{pulse_samples}\n")
        pprint.pprint(pulse_samples)

    if args.outfname:
        outfilen = args.outfname
        if not outfilen.endswith('.sub'):
            outfilen += '.sub'
    else:
        outfilen = os.path.splitext(filen)[0] + ".sub"

    with open(outfilen, 'w', encoding="utf-8") as fd:
        print(sub_data, file=fd)


if __name__ == '__main__':

    args, _extra = arg_opts()
    filen = args.input_file

    if args.freq:
        rf_freq = int(args.freq)

    if args.default_freq:
        rf_freq_default = int(args.default_freq)

    if args.min_pulses:
        MIN_PULSES = int(args.min_pulses)

    if args.verb:
        verbose = args.verb

    main()
