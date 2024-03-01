build: clean
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel --universal

clean:
	rm -rf dist build mqttwrapper.egg-info

publish: clean build
	twine upload dist/*
