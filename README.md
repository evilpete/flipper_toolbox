# Flipper File Toolbox #

Random scripts and links for generating Flipper data files.

(An occasional work in Progress)

## Tools ##

#### prox2flip.py ####

Python script to convert proxmark json dump into Flipper NFC Save File

>`prox2flip.py test_dat/mf-classic-1k-23AD7C86.json > mfc1k-23AD7C86.nfc`

---
 
#### create_sub_dat.py ####

Based on @[jinschoi](https://gist.github.com/jinschoi)'s [create_sub.py](https://gist.github.com/jinschoi/f39dbd82e4e3d99d32ab6a9b8dfc2f55)

Python script to generate Flipper RAW .sub files from OOK bitstreams

Added :
* FSK support
* insteon (Broken)
* FAN-11T Remote Control of Harbor Breeze Fan (Brute Force)

---

#### gen_url_nfc.py ####

Generates NFC with URL address data and outputs Flipper NFC "save" file format

>`gen_url_nfc.py https://youtu.be/dQw4w9WgXcQ "Rick Roll" > rick_roll.nfc`

see file [rick_roll.nfc](test_dat/Rick_Roll.nfc)

Note: requires [ndeflib](https://github.com/nfcpy/ndeflib) (available on [pypi](https://pypi.org/project/ndeflib/))

---

#### gen_all_ir_codes.py ####

Generates file Flipper IR file will all command codes for a given address

>`gen_all_ir_codes.py RC5 03 00`

Will generate filename [IR-CMD-RC5-03.ir](test_dat/IR-CMD-RC5-03.ir)

---

### See Also: ###


* [FlipperScripts](https://github.com/DroomOne/FlipperScripts.git) "
	Reads the `DolphinStoreData` struct from `dolphin.state` files.

* [create_sub.py](https://gist.github.com/jinschoi/f39dbd82e4e3d99d32ab6a9b8dfc2f55) :
	Python script to generate Flipper RAW .sub files from OOK bitstreams.

* [bitstream-from-sub.py](https://gist.github.com/jinschoi/40a470e432c6ac244be8159145454b5c) :
	Decode raw bitstring captured Flipper RAW .sub file.

* [csv2ir](https://github.com/Spexivus/csv2ir) :
	csv2ir is a script to convert ir .csv files to .ir files for the flipper.

* [awesome-flipperzero](https://github.com/djsime1/awesome-flipperzero)
	 Another collection of Awesome resources for the Flipper Zero device.
