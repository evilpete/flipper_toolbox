
#
# make lint :  runs pylint on all all sripts (default)
# 
# make pep8 : run pycodestyle on all script files
#
# make secplus : download the secplus library
#
# make ndeflib ; install ndeflib (NDEF messages) library
#
# make gen-files : (re)generate ir/subghz/nfc data file.
#
# make clone-repos : doanload other repos with useful flipper data files
#



PYCODESTYLE=pycodestyle
PEP8ARG=--ignore=E501,E221,E241,E502,W503

PYLINT=pylint


FILES=subghz_secplusv1.py subghz_secplusv2.py \
	nfc_diff_dict.py \
	subghz_ook_to_sub.py subghz_x10.py subghz_insteon.py \
	ir_gen_all_codes.py ir_plot.py \
	nfc_gen_url.py nfc_hexdump.py nfc_prox2flip.py \
	subghz_create_dat.py subghz_decode_presets.py subghz_gen_cmd.py \
	subghz_histogram.py

all: pylint

gen-files: x10-brute ir-brute fan-brute nfc-Rick_Roll

clone-repos: t119bruteforcer flipperzero-bruteforce CAMEbruteforcer Flipper-IRDB secplus

lint: pylint

pylint:
	for targ in ${FILES} ; do \
		echo $$targ ; \
		pylint $$targ  ; \
	done

# pylint --load-plugins perflint $$targ  ; \
# python -m py_compile $$targ ; \
#


pep8: pycodestyle

pycodestyle:
	for targ in ${FILES} ; do \
		echo $$targ ; \
		${PYCODESTYLE} ${PEP8ARG} $$targ ; \
	done


# generage brute force files

ir-brute:
	mkdir -p IR/All-Codes
	bash IR/.gen-all-ir.sh

x10-brute:
	mkdir -p subghz/X10
	( cd subghz/X10 ; ../../subghz_x10.py -b )

fan-brute:
	mkdir -p subghz/fan
	( cd subghz/fan_bruteforce ; ../../subghz_create_dat.py fan )

nfc-Rick_Roll:
	mkdir -p nfc
	./nfc_gen_url.py https://youtu.be/dQw4w9WgXcQ "Rick Roll" > nfc/Rick_Roll.nfc

# used 3rd party libraries

ndeflib:
	python3 -m pip install ndeflib

secplus:
	git clone https://github.com/argilo/secplus.git


####

clean:
	@/bin/rm -f *sub *.ir *.nfc touch_tunes-?? *_ON.sub *_OFF.sub X10_All-*.sub secv2-*.sub
	@/bin/rm -rf __pycache__ repos 


# clone usful repos with flipper  datafiles

t119bruteforcer: repos
	mkdir -p repos
	( cd repos ; git clone https://github.com/xb8/t119bruteforcer.git )

flipperzero-bruteforce:
	mkdir -p repos
	( cd repos ; git clone https://github.com/tobiabocchi/flipperzero-bruteforce.git )

CAMEbruteforcer:
	mkdir -p repos
	( cd repos ; git clone https://github.com/BitcoinRaven/CAMEbruteforcer.git )

Flipper-IRDB:
	mkdir -p repos
	( cd repos ; git clone https://github.com/logickworkshop/Flipper-IRDB.git )

