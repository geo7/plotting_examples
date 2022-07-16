# simple script to run a few things when working on stuff.
dvc repro dvc.yaml
python -m generate_readme
pre-commit run --all-files
mypy --strict . 