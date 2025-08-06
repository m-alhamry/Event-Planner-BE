#!/usr/bin/env bash
# Exit on error
set -o errexit
pipenv install
pipenv run python manage.py collectstatic --no-input
pipenv run python manage.py migrate