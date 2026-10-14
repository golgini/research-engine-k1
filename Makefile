install:
	python -m pip install -e .
test:
	pytest -q
lint:
	python -m compileall -q src
