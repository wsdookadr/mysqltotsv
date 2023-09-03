install_pkg_deps:
	pip install wheel
	pip install twine

package_upload:
	rm -rf dist/ build/ *.egg-info/
	python3 setup.py sdist bdist_wheel
	twine upload dist/*


test:
	nosetests --nocapture -v tests/*.py

