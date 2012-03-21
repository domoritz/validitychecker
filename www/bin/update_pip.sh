#!/bin/sh
pip freeze --local | cut -d = -f 1  | xargs echo pip install -U
