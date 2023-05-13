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

pre_commit: ## run pre-commit manually
	pre-commit run --all-files

readme: ## Generate README file.
	poetry run python generate_readme.py

########
# LINT #
########

lint:
	poetry run ruff .
	poetry run black --check .

format:
	poetry run black .

##########
# POETRY #
##########

poetry.lock:
	poetry lock --no-update
