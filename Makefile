
# E303 : too many blank lines
# E302 : expected 2 blank lines, found 1
# E201 whitespace after '['
# E202 whitespace before ']'
# E501 line too long

# E203,E201,E202,E501
# PEP8=pep8
PYCODESTYLE=pycodestyle
PEP8ARG=--ignore=E501 
# PEP8ARG=--ignore=E303,E302,E201,E202,E501 

PYLINT=pylint


FILES=create_sub_dat.py \
	gen_all_ir_codes.py gen_url_nfc.py generate_sub_cmd.py \
	prox2flip.py rnfc.py subghz_histogram.py 

all: pylint

pylint:
	for targ in ${FILES} ; do \
		echo $$targ ; \
		pylint --load-plugins perflint $$targ  ; \
	done

# python -m py_compile $$targ ; \


pep8: pycodestyle

pycodestyle:
	for targ in ${FILES} ; do \
		echo $$targ ; \
		${PYCODESTYLE} ${PEP8ARG} $$targ ; \
	done
	

clean:
	@/bin/rm -fr *sub *.ir *.nfc touch_tunes-???
