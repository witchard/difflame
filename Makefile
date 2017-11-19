VERSION = $(shell python3 setup.py --version)

.PHONY: release clean

help:
	@echo "doc: Build documentation"
	@echo "cleandoc: Clean documentation"
	@echo "showdoc: Show documentation in webbrowser"
	@echo "release: Package and release to PyPI"
	@echo "cleanrelease: Clean release packaging"
	@echo "test: Run tests"
	@echo "coverage: Run coverage tests, requires coverage (pip install coverage)"
	@echo "clean: Clean all"

release:
	python3 setup.py --version | egrep -q -v '[a-zA-Z]' # Fail on dev/rc versions
	git commit -e -m "Release of $(VERSION)"            # Fail on nothing to commit
	git tag -a -m "Release of $(VERSION)" $(VERSION)    # Fail on existing tags
	git push origin HEAD                                # Fail on out-of-sync upstream
	git push origin tag $(VERSION)                      # Fail on dublicate tag
	python3 setup.py sdist register upload              # Release to pypi

clean:
	rm -rf build/ dist/ MANIFEST 2>/dev/null || true
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +
