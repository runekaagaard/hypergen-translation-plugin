SHELL := /bin/bash

pypi-build:
	rm -rf dist/*
	python3 -m build
pypi-check:
	python3 -m twine check dist/*
pypi-show:
	rm -rf /tmp/hypergen_test_build
	virtualenv --python=python3.9 /tmp/hypergen_test_build
	source /tmp/hypergen_test_build/bin/activate && \
		pip install dist/*.whl && \
		tree /tmp/hypergen_test_build/lib/python3.*/site-packages/hypergen_translation/
pypi-release-test:
	python3 -m twine upload --repository testpypi dist/*
pypi-release:
	python3 -m twine upload dist/*
