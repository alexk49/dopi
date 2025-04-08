#!/bin/bash

set -e

ruff check src --fix
ruff format src

mypy src
