#!/usr/bin/env python3
"""

    decode_Custom_presets.py

    Decodes CC1101 settings from Flipper setting_user file or saved sameple file

    Warning:   this is total trash code, use at own risk

    Written By: Peter Shipley github.com/evilpete

"""

import sys
import os
import pprint

# pylint: disable=no-member

_DEBUG = 0


# ./lib/drivers/cc1101_regs.h
CC1101_QUARTZ=26000000
mhz = 26

MFMCFG1_NUM_PREAMBLE           = 0x70
MFMCFG1_NUM_PREAMBLE_4         = (0x02 << 4)
DEVIATN_DEVIATION_M            = 0x07
MDMCFG2_MOD_FORMAT             = 0x70
MDMCFG2_MANCHESTER_EN          = 0x08
MDMCFG2_SYNC_MODE              = 0x07
MDMCFG4_DRATE_E                = 0x0F
MDMCFG4_CHANBW_E               = 0xC0
MDMCFG4_CHANBW_M               = 0x30



BSCFG_BS_LIMIT                 = 0x03

PKTCTRL0_LENGTH_CONFIG         = 0x03

MOD_2FSK                        = 0x00
MOD_GFSK                        = 0x10
MOD_ASK_OOK                     = 0x30
MOD_4FSK                        = 0x40
MOD_MSK                         = 0x70

MANCHESTER                      = 0x08



class CC_REG():

    def __init__(self, **kwargs):
        # print("CC_REG __init__")
        self.reg_num ={}
        self._debug = kwargs.get('debug', 0)
        #for i in range(len(self.reg_names)):
        #    self.reg_num[ self.reg_names[i]] = i
        #    self.__setattr__(self.reg_names[i], i)
        for i, n in enumerate(self.reg_names):
            self.reg_num[n] = i
            self.__setattr__(n, i)

        self.mod_names = {}
        for k, v in self.mod_num.items():
            self.mod_names[v] = k
        self.mod_names['ASK'] = self.mod_names['OOK']

    mod_num = {
        MOD_2FSK    : "2FSK",
        MOD_GFSK    : "GFSK",
        MOD_4FSK    : "4FSK",   # note: radio doesn't support Manchester encoding in 4FSK
        MOD_ASK_OOK : "OOK",    # ASK
        MOD_MSK     : "MSK",
    }

    sync_modes = [ 'SYNCM_NONE', 'SYNCM_15_of_16', 'SYNCM_16_of_16', 'SYNCM_30_of_32',
        'SYNCM_CARRIER', 'SYNCM_CARRIER_15_of_16', 'SYNCM_CARRIER_16_of_16', 'SYNCM_CARRIER_30_of_32']

    reg_names = [ 'IOCFG2', 'IOCFG1', 'IOCFG0', 'FIFOTHR', 'SYNC1', 'SYNC0', 'PKTLEN',
        'PKTCTRL1', 'PKTCTRL0', 'ADDR', 'CHANNR', 'FSCTRL1', 'FSCTRL0', 'FREQ2',
        'FREQ1', 'FREQ0', 'MDMCFG4', 'MDMCFG3', 'MDMCFG2', 'MDMCFG1', 'MDMCFG0',
        'DEVIATN', 'MCSM2', 'MCSM1', 'MCSM0', 'FOCCFG', 'BSCFG', 'AGCCTRL2', 'AGCCTRL1',
        'AGCCTRL0', 'WOREVT1', 'WOREVT0', 'WORCTRL', 'FREND1', 'FREND0', 'FSCAL3',
        'FSCAL2', 'FSCAL1', 'FSCAL0', 'RCCTRL1', 'RCCTRL0', 'FSTEST', 'PTEST',
        'AGCTEST', 'TEST2', 'TEST1', 'TEST0']

    num_preamble = [2, 3, 4, 6, 8, 12, 16, 24 ]

class CC_Config(CC_REG):


    def __init__(self, **kwargs):

        # print("CC_Config __init__")

        self._debug = kwargs.get('debug', _DEBUG)
        self.name = kwargs.get('name', 'custom')

        super().__init__()

        # print("len self.reg_num", len(self.reg_num))
        if 'reg_list' in kwargs:
            self.reg_list = kwargs['reg_list']
        else:
            self.reg_list = [None] * 50

        if 'reg_str' in kwargs:
            self.load_str(kwargs['reg_str'], clear_list=False)

        self.name = kwargs.get('name', "Custom_Preset")



    def load_str(self, reg_str, clear_list=True):

        # print("load_str:", reg_str)

        if reg_str.startswith('Custom_preset_data'):
            reg_str = reg_str.split(':')[1].strip()


        if clear_list:
            self.reg_list[:] = [None] * 50


        reg_pairs = reg_str.split()
        rp_len = len(reg_pairs)
        # print("reg_pairs:", reg_pairs)
        # print("rp_len:", rp_len)

        for i in range(0, rp_len, 2):
            n = reg_pairs[i]
            v = reg_pairs[i +1]
            if n == '00' and v == '00':
                break
            nv = int(n, 16)
            self.reg_list[nv] = int(v, 16)

        # print(">>", self.reg_list)


    def as_dict(self):
        return {k: v for k, v in zip(self.reg_names, self.reg_list) if v is not None}
        # return dict(zip(self.reg_names, self.reg_list))

    def as_preset_data(self):
        a = []
        for i, v in enumerate(self.reg_list):
            if v is not None:
                a.append(f"{i:02x} {v:02x}")
        a.append("00 00")
        return " ".join(a)

    def rf_conf(self):
        res = []


        # Frequency Configuration

        x = self.get_Channel()
        if x is not None:
            res.append(('Channel:', '{self.get_Channel()}'))

        x = self.get_FsIF()
        if x is not None:
            res.append(('Intermediate_freq:', f'{x}'))

        x = self.get_FsOffset()
        if x is not None:
            res.append(('Frequency_Offset:', f'{x}'))


        # Modem Configuration

        x = self.get_Modulation()
        res.append(('Modulations:', f'{self.mod_num.get(x, "??")}'))
        # res['Modulations'] = self.mod_names.get(x, '??')

        if self.reg_list[self.MDMCFG4] and self.reg_list[self.MDMCFG3]:
            res.append(('Data_Rate:', f'{self.get_DRate():.2f} Hz'))

        res.append(('Channel_Bandwidth:', f'{self.get_ChanBW():.2f}'))

        x = self.get_Deviatn()
        if x is not None:
            res.append(('Deviation:', f'{self.get_Deviatn():.2f} Hz'))

        x = self.get_SyncMode()
        if x is not None:
            y = self.sync_modes[x]
            res.append(('Sync_Mode:', f'{y}'))

        x = self.get_ChanSpc()
        if x is not None:
            res.append(('Channel_spacing:', f'{x:.2f} Hz'))

        if self.reg_list[self.BSCFG] is not None:
            res.append(('BSLimit:', f'{self.get_BSLimit()}'))

        res.append(('Manchester:', f'{self.get_Manchester()}'))

        #  Packet Config

        if self.reg_list[self.SYNC1]:
            res.append (('SyncWord:', f'{self.get_SyncWord()}'))

        x, y = self.get_pktlen()
        if x is not None:
            res.append(('Packet_Length:', f'{x}'))
            res.append(('Variable_length_packet:', f'{y & 0x03}'))



        if self.reg_list[self.PKTCTRL1]:
            res.append(('Preamble_Quality_Threshold:', f'{self.get_PktPQT()}'))

        if self.reg_list[self.PKTCTRL0]:
            res.append(('DataWhitening', f'{self.get_PktDataWhitening()}'))


        #NUM_PREAMBLE = [2, 3, 4, 6, 8, 12, 16, 24 ]
        # x = (self.get_NumPreamble() >> 4) & 7
        # num_preamble = self.num_preamble[x]
        x = self.get_NumPreamble()
        if x is not None:
            res.append(('Min_TX_Preamble:', f'{self.get_NumPreamble()}'))


        # res['Est_Freq_Offset'] = self.get_FreqEst()


        return res

    def set_ChanBW(self, bw):

        chanbw_e = None
        chanbw_m = None

        for e in range(4):
            m = int(((CC1101_QUARTZ / (bw *pow(2, e) * 8.0)) - 4) + .5)        # rounded evenly
            if m < 4:
                chanbw_e = e
                chanbw_m = m
                break
        if chanbw_e is None:
            raise ValueError("ChanBW does not translate into acceptable parameters")

        xbw = 1000.0*mhz / (8.0*(4+chanbw_m) * pow(2, chanbw_e))
        if self._debug:
            print(f"chanbw_e: {e:x}   chanbw_m: {m:x}   chanbw: {xbw:f} kHz")

        mdmcfg4 = self.reg_list[self.MDMCFG4]
        mdmcfg4 &= ~(MDMCFG4_CHANBW_E | MDMCFG4_CHANBW_M)
        mdmcfg4 |= ((chanbw_e<<6) | (chanbw_m<<4))
        self.reg_list[self.MDMCFG4] = mdmcfg4


        # from http://www.cs.jhu.edu/~carlson/download/datasheets/ask_ook_settings.pdf
        if bw > 102e3:
            self.reg_list[self.FREND1] = 0xb6
        else:
            self.reg_list[self.FREND1] = 0x56

        if bw > 325e3:
            self.reg_list[self.TEST2] = 0x88
            self.reg_list[self.TEST1] = 0x31
        else:
            self.reg_list[self.TEST2] = 0x81
            self.reg_list[self.TEST1] = 0x35



    def get_ChanBW(self):

        mdmcfg4 = self.reg_list[self.MDMCFG4]
        chanbw_e = (mdmcfg4 >> 6) & 0x3
        chanbw_m = (mdmcfg4 >> 4) & 0x3
        bw = CC1101_QUARTZ / (8.0*(4+chanbw_m) * pow(2, chanbw_e))
        if self._debug:
            print(f"chanbw_e: {chanbw_e:x}   chanbw_m: {chanbw_m:x}   chanbw: {bw:f} hz")
        return bw


    # def get_FreqEst(self):
    #    freqest = self.reg_list[self.FREQEST]
    #    return freqest

    def set_FsIF(self, freq_if):

        ifBits = (freq_if * (pow(2, 10))) / CC1101_QUARTZ
        ifBits = int(ifBits + .5)       # rounded evenly

        if ifBits >0x1f:
            raise ValueError(f"FAIL:  freq_if is too high?  freqbits: {ifBits:x} (must be <0x1f)")

        fsctrl1 = self.reg_list[self.FSCTRL1]
        fsctrl1 &= ~(0x1f)
        fsctrl1 |= int(ifBits)
        self.reg_list[self.FSCTRL1] = fsctrl1

    def get_FsIF(self):
        fsctrl1 = self.reg_list[self.FSCTRL1]
        if fsctrl1 is None:
            return None

        freq_if = (fsctrl1 & 0x1f) * (CC1101_QUARTZ / pow(2, 10))
        return freq_if

    def set_FsOffset(self, if_off):
        self.reg_list[self.FSCTRL0] = if_off

    def get_FsOffset(self):
        freqoff = self.reg_list[self.FSCTRL0]
        return freqoff


    def get_Modulation(self):
        mdmcfg2 = self.reg_list[self.MDMCFG2]
        mod = (mdmcfg2) & MDMCFG2_MOD_FORMAT
        return mod

    def set_Modulation(self, mod):

        if mod not in self.mod_names:
            raise ValueError(f"Unknown Modulation: {mod}")

        mdmcfg2 = self.reg_list[self.MDMCFG2]
        mdmcfg2 &= ~MDMCFG2_MOD_FORMAT
        mdmcfg2 |= mod
        self.reg_list[self.MDMCFG2] = mdmcfg2

    def set_Deviatn(self, deviatn):
        for e in range(8):
            m = int(((deviatn * pow(2, 17)) / ((pow(2, e)* CC1101_QUARTZ))-8) + .5)
             # int((old_div(deviatn * pow(2, 17), (pow(2, e)* (mhz*1000000.0)))-8) + .5)
             # (old_div(deviatn * pow(2, 17), (pow(2, e)* (mhz*1000000.0)))-8) + .5
             # ((deviatn * pow(2, 17)) / ((pow(2, e)* (mhz*1000000.0)))-8) + .5
            if m < 8:
                dev_e = e
                dev_m = m
                break

        if dev_e is None:
            raise ValueError("Deviation does not translate into acceptable parameters.")

        dev = CC1101_QUARTZ * (8+dev_m) * pow(2, dev_e) / pow(2, 17)

        if self._debug:
            print(f"dev_e: {e:X}   dev_m: {m:X}   deviatn: {dev:f} Hz")

        reg_id = self.reg_num[ 'DEVIATN' ]
        d_reg = (dev_e << 4) | dev_m
        self.reg_list[reg_id] = d_reg

    def get_Deviatn(self):

        reg_id = self.reg_num[ 'DEVIATN' ]
        dev = self.reg_list[reg_id]

        if dev is None:
            return  None

        dev_e = dev >> 4
        dev_m = dev & DEVIATN_DEVIATION_M
        # dev = 1000000.0 * mhz * (8+dev_m) * pow(2, dev_e) / pow(2, 17)
        deviatn = CC1101_QUARTZ * (8+dev_m) * pow(2, dev_e) / pow(2, 17)

        return deviatn

    def get_PktDataWhitening(self):

        if self.reg_list[self.PKTCTRL0] is None:
            return None
        return (self.reg_list[self.PKTCTRL0] >>6) & 0x1

    def get_PktPQT(self):
        """ preamble quality threshold """
        if self.reg_list[self.PKTCTRL1] is None:
            return None

        return (self.reg_list[self.PKTCTRL1] >> 5) & 7

    def get_pktlen(self):
        # (self.radiocfg.pktlen, self.radiocfg.pktctrl0 & PKTCTRL0_LENGTH_CONFIG)
        return (self.reg_list[self.PKTLEN], self.reg_list[self.PKTCTRL0] & PKTCTRL0_LENGTH_CONFIG)


    def set_Manchester(self, enable=True):

        mdmcfg2 = self.reg_list[self.MDMCFG2]
        mdmcfg2 &= ~MDMCFG2_MANCHESTER_EN
        mdmcfg2 |= (enable<<3)

        self.reg_list[self.MDMCFG2] = mdmcfg2

    def get_Manchester(self):

        mdmcfg2 = self.reg_list[self.MDMCFG2]
        mchstr = (mdmcfg2>>3) & 0x01
        return mchstr

    def set_DRate(self, drate):

        for e in range(16):
            m = int(((drate * pow(2, 28)/ (pow(2, e)* CC1101_QUARTZ))-256) + .5)        # rounded evenly
            if m < 256:
                drate_e = e
                drate_m = m
                break

        if drate_e is None:
            raise ValueError("DRate does not translate into acceptable parameters.")

        drate = CC1101_QUARTZ * (256+drate_m) * pow(2, drate_e) / pow(2, 28)

        if self._debug:
            print(f"drate_e: {drate_e:x}  drate_m: {drate_m:x}   drate: {drate:f} Hz")

        self.reg_list[self.MDMCFG3] = drate_m

        mdmcfg4 = self.reg_list[self.MDMCFG4]
        mdmcfg4 &= ~MDMCFG4_DRATE_E
        mdmcfg4 |= drate_e

        self.reg_list[self.MDMCFG4] = mdmcfg4

    def get_DRate(self):

        drate_e = self.reg_list[self.MDMCFG4] & 0xf
        drate_m = self.reg_list[self.MDMCFG3]

        drate = CC1101_QUARTZ * (256+drate_m) * pow(2, drate_e) / pow(2, 28)

        return drate


    def get_SyncWord(self):

        if self.reg_list[self.SYNC1] is None:
            return None

        return (self.reg_list[self.SYNC1] << 8) + self.reg_list[self.SYNC0]

    def set_SyncWord(self, word):

        self.reg_list[self.SYNC1] = word >> 8
        self.reg_list[self.SYNC0] = word & 0xff

    def get_SyncMode(self):
        return self.reg_list[self.MDMCFG2] & MDMCFG2_SYNC_MODE

    # SYNCM_NONE                      = 0
    # SYNCM_15_of_16                  = 1
    # SYNCM_16_of_16                  = 2
    # SYNCM_30_of_32                  = 3
    # SYNCM_CARRIER                   = 4
    # SYNCM_CARRIER_15_of_16          = 5
    # SYNCM_CARRIER_16_of_16          = 6
    # SYNCM_CARRIER_30_of_32          = 7

    def set_SyncMode(self, syncmode=5):

        mdmcfg2 = self.reg_list[self.MDMCFG2]
        mdmcfg2 &= ~MDMCFG2_SYNC_MODE
        mdmcfg2 |= syncmode

        self.reg_list[self.MDMCFG2] =mdmcfg2

    # [2, 3, 4, 6, 8, 12, 16, 24 ]
    # MFMCFG1_NUM_PREAMBLE0          = 0x10
    # MFMCFG1_NUM_PREAMBLE1          = 0x20
    # MFMCFG1_NUM_PREAMBLE2          = 0x40

    # MFMCFG1_NUM_PREAMBLE_2         = (0x00 << 4)
    # MFMCFG1_NUM_PREAMBLE_3         = (0x01 << 4)
    # MFMCFG1_NUM_PREAMBLE_4         = (0x02 << 4)
    # MFMCFG1_NUM_PREAMBLE_6         = (0x03 << 4)
    # MFMCFG1_NUM_PREAMBLE_8         = (0x04 << 4)
    # MFMCFG1_NUM_PREAMBLE_12        = (0x05 << 4)
    # MFMCFG1_NUM_PREAMBLE_16        = (0x06 << 4)
    # MFMCFG1_NUM_PREAMBLE_24        = (0x07 << 4)

    def get_NumPreamble(self):

        if self.reg_list[self.MDMCFG1] is None:
            return None

        preamble= (self.reg_list[self.MDMCFG1]  & MFMCFG1_NUM_PREAMBLE)
        return preamble


    def set_NumPreamble(self, preamble=MFMCFG1_NUM_PREAMBLE_4):
        mdmcfg1 = self.reg_list[self.MDMCFG1]
        mdmcfg1 &= ~MFMCFG1_NUM_PREAMBLE
        mdmcfg1 |= preamble

        self.reg_list[self.MDMCFG1] = mdmcfg1


    # BSCFG_BS_LIMIT_0               = (0x00)    # "No data rate offset compensation performed",
    # BSCFG_BS_LIMIT_3               = (0x01)    # "+/- 3.125% data rate offset"
    # BSCFG_BS_LIMIT_6               = (0x02)    # "+/- 6.25% data rate offset",
    # BSCFG_BS_LIMIT_12              = (0x03)    # "+/- 12.5% data rate offset",

    def get_BSLimit(self):
        if self.reg_list[self.BSCFG] is None:
            return None
        return self.reg_list[self.BSCFG] & BSCFG_BS_LIMIT

    def set_BSLimit(self, bslimit):

        bscfg = self.reg_list[self.BSCFG]

        bscfg &= ~BSCFG_BS_LIMIT
        bscfg |= bslimit
        self.reg_list[self.BSCFG] = bscfg



    def set_Channel(self, channr):
        self.reg_list[self.CHANNR] = channr & 0xff

    def get_Channel(self):
        channr = self.reg_list[self.CHANNR]
        return channr

    def get_ChanSpc(self):

        if self.reg_list[self.MDMCFG0] is None or self.reg_list[self.MDMCFG1] is None:
            return None

        chanspc_m = self.reg_list[self.MDMCFG0]
        chanspc_e = self.reg_list[self.MDMCFG1] & 3
        chanspc = CC1101_QUARTZ / pow(2, 18) * (256 + chanspc_m) * pow(2, chanspc_e)
        if self._debug:
            print(f"chanspc_e: {chanspc_e:x}   chanspc_m: {chanspc_m:x}   chanspc: {chanspc:f} hz")
        return chanspc

    def set_ChanSpc(self, chanspc):

        chanspc_e = None
        chanspc_m = None
        for e in range(4):
            m = int(((chanspc * pow(2, 18)/ (CC1101_QUARTZ * pow(2, e)))-256) +.5)    # rounded evenly
            if m < 256:
                chanspc_e = e
                chanspc_m = m
                break
            if chanspc_e is None or chanspc_m is None:
                raise ValueError("ChanSpc does not translate into acceptable parameters.")


        #chanspc = CC1101_QUARTZ/pow(2, 18) * (256 + chanspc_m) * pow(2, chanspc_e)
        #print "chanspc_e: %x   chanspc_m: %x   chanspc: %f hz" % (chanspc_e, chanspc_m, chanspc)

        # mdmcfg0 = self.reg_list[self.MDMCFG0]
        mdmcfg1 = self.reg_list[self.MDMCFG1]

        mdmcfg0 = chanspc_m
        mdmcfg1 &= ~0x03 # MDMCFG1_CHANSPC_E            # clear out old exponent value
        mdmcfg1 |= chanspc_e
        self.reg_list[self.MDMCFG0] = mdmcfg0
        self.reg_list[self.MDMCFG1] = mdmcfg1

    def __repr__(self):
        return str({k: v for k, v in zip(self.reg_names, self.reg_list) if v is not None})


def main():

    if len(sys.argv) < 2:
        if os.path.isfile("setting_user"):
            filen = 'setting_user'
        else:
            print("requires setting_user file or saved sameple file as first arg")
            return
    else:
        filen = sys.argv[1]



    presets = {}

    with open(filen, 'r') as fd:
        preset_name = None
        preset_data = None
        for l in fd:
            if l.startswith('Custom_preset_name'):
                preset_name = l.split(':')[1].strip()

            if l.startswith('Custom_preset_data'):
                preset_data = l.split(':')[1].strip()

            if preset_name and preset_data:
                presets[preset_name] = CC_Config(name=preset_name, reg_str=preset_data)
                preset_name = None
                preset_data = None


    for k, v in presets.items():
        print(f"\n\n{k}")
        pprint.pprint(v.as_dict(), indent=4, width=50, compact=True)
        # print("\nas_preset_data")
        # pprint.pprint(presets['FM476'].as_preset_data(), compact=True)
        print("\nrf_conf")
        for a, b in v.rf_conf():
            print(f"    {a:<25s} {b:<10s}")

    # print(dir(presets['AM_1']))



if __name__ == '__main__':
    main()
