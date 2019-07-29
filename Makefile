test:
	( \
	python3 -m venv venv; \
	. venv/bin/activate; \
	pip install -r requirements.txt; \
	nosetests muspractice/test/test_*.py \
	)

clean :
	rm -rf venv
