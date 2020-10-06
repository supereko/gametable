lint:
	isort .
	pylint --rcfile=setup.cfg $(shell pwd)/gametable