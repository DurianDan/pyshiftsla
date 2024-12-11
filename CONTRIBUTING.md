# Contributing to pyshiftsla
Thank you for your interest in contributing! Here's how you can help:

## Development setup
1. Clone the repository
2. Publish your branch
3. Install dependencies with [poetry](https://python-poetry.org/docs/): `poetry install`
4. Make some local changes
5. Test with `pytest -v`
6. Run pre commit hooks: `pre-commit run --all`
7. Push to your branch
8. Make Pull request

## To Publish To PyPi
```bash
source .env
poetry publish --build --username $PIPY_USERNAME --password $PIPY_PASSWORD
```