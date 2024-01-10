#!/bin/bash

# create .venv if it doesn't exist
if [ ! -d dir ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt
python3 main.py