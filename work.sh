# simple script to run a few things when working on stuff.
poetry run dvc repro dvc.yaml
poetry run mypy --strict .
poetry run pre-commit run --all-files
poetry run python -m generate_readme




# add changes to dvc.lock if there are any
git diff --name-only HEAD -- dvc.lock && git add dvc.lock && git commit -m 'update dvc.lock'
# automatically add changes to image files
git diff --name-only --diff-filter=dM HEAD | egrep '.*images.*\.png$' | xargs -r git add && git commit -m 'updated generated image'

