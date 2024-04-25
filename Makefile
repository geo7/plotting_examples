.PHONY: clean requirements
.PHONY: git-stats git-log cloc clean-git
.PHONY: deploy
.PHONY: test
.PHONY: requirements
.PHONY: help

GIT := git
CLOC := cloc

#########
# UTILS #
#########

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

clean:
	@echo "Cleaning up temporary and cache files"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +

cloc:
	@echo "Code statistics using cloc:"
	$(CLOC) --exclude-dir=venv .

######################
# WORKING ON PROJECT #
######################

pre-commit-run:
	poetry run pre-commit run --all-files

readme: ## Generate README file.
	poetry run python generate_readme.py

# This'll just run through all the plots.
repro: ## run dvc repro
	poetry run dvc repro dvc.yaml


########
# LINT #
########

mypy:
	poetry run mypy . --strict

lint: mypy ## run linting - mypy,ruff
	poetry run ruff check .
	poetry run ruff format . --check
	@$(MAKE) --no-print-directory clean

# Using this as format & lint really...
format: pre-commit-run ## run formatters - pre-commit,ruff
	poetry run ruff format .
	poetry run ruff check . --fix --unsafe-fixes
	@$(MAKE) --no-print-directory clean


##########
# POETRY #
##########

poetry.lock:
	poetry lock --no-update
