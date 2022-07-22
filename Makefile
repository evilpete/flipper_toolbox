


FILES=create_sub_dat.py \
	gen_all_ir_codes.py gen_url_nfc.py generate_sub_cmd.py \
	prox2flip.py rnfc.py subghz_histogram.py 

all: pylint

pylint:
	for targ in ${FILES} ; do \
		echo $$targ ; \
		pylint $$targ  ; \
	done

# python -m py_compile $$targ ; \

# E303 : too many blank lines
# E302 : expected 2 blank lines, found 1
# E201 whitespace after '['
# E202 whitespace before ']'
# E501 line too long

# E203,E201,E202,E501
PEP8=pep8
PEP8ARG=--ignore=E303,E302,E201,E202,E501 --exclude=flipperzero_protobuf_compiled

clean:
	@/bin/rm -fr *sub *.ir *.nfc touch_tunes-???
