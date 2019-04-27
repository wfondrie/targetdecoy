help:
	@echo 'Build and upload pip wheels and docs'
	@echo '    make help: Display this text.'
	@echo '    make clean: Remove old pip wheels.'
	@echo '    make build: Build new pip wheels.'
	@echo '    make update: Update setuptools, wheel, and twine'
	@echo '    make upload: Upload wheels to PyPI'
  @echo '    make curve: Generate example curve.png'
	@echo ' '
	@echo 'Normal usage is: update -> clean -> build -> upload'

clean:
	rm -r dist

build:
	python3 setup.py sdist bdist_wheel

upload:
	twine upload dist/*

update:
	python3 -m pip install --upgrade setuptools wheel twine

curve: REAMD.md
	python -m doctest -v README.md

.PHONY: help clean build upload update curve
