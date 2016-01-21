#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$HOME/lib/python
export PATH="$HOME/bin:$PATH"
export VERSIONER_PYTHON_VERSION=3.4
cd ~/cron
python3.4 mls.py
