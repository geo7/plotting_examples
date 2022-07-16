# simple script to run a few things when working on stuff.
dvc repro dvc.yaml
python -m generate_readme
mypy --strict .
pre-commit run --all-files
