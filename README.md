# CloudShell package repo template

[![Build status](https://travis-ci.org/QualiSystems/cloudshell-package-repo-template.svg?branch=dev)](https://travis-ci.org/QualiSystems/cloudshell-package-repo-template)
[![codecov](https://codecov.io/gh/QualiSystems/cloudshell-package-repo-template/branch/dev/graph/badge.svg)](https://codecov.io/gh/QualiSystems/cloudshell-package-repo-template)
[![PyPI version](https://badge.fury.io/py/cloudshell-package-repo-template.svg)](https://badge.fury.io/py/cloudshell-package-repo-template)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Use this template for creating a new package for the Shells.

## tox.ini
- set package-name var regarding your package
- set python version in envlist

## .travis.yml
- set python version regarding to tox.ini

## pyproject.toml
- set python version for black

## setup.py
- set name and description for the package
- set python version

## add git hook
run `pre-commit install`
