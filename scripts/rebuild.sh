# update version in pyproject.toml first
rm -rf dist
python3 -m build
python3 -m twine upload --repository testpypi dist/*
