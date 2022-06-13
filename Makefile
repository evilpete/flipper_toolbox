


FILES= create_sub_dat.py gen_url_nfc.py gen_all_ir_codes.py prox2flip.py

all: pylint

pylint:
	for targ in ${FILES} ; do \
		echo $$targ ; \
		pylint $$targ  ; \
	done

# python -m py_compile $$targ ; \
