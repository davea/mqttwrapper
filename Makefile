build: clean
	uv build

clean:
	rm -rf dist build mqttwrapper.egg-info

publish: clean build
	uv publish
