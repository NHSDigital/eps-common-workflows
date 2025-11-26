.PHONY: install

install: install-node install-python install-hooks

install-node:
	npm ci

install-python:
	poetry install

install-hooks: install-python
	poetry run pre-commit install --install-hooks --overwrite

deep-clean:
	find . -name 'node_modules' -type d -prune -exec rm -rf '{}' +

check-licenses: check-licenses-python

check-licenses-python:
	scripts/check_python_licenses.sh

lint: lint-githubactions lint-githubaction-scripts

lint-githubactions:
	actionlint

lint-githubaction-scripts:
	shellcheck .github/scripts/*.sh

test:
	echo "Not implemented"

build:
	echo "Not implemented"

run-all-release:
	./scripts/run_all_release.sh 2>&1 | tee release_$(shell date +%Y%m%d_%H%M%S).log
