#!/bin/bash

# Fix PYTHONPATH to prioritize virtual environment packages
ANTENV_PATH=$(find /tmp -name "antenv" -type d 2>/dev/null | head -1)
if [ -n "$ANTENV_PATH" ]; then
    export PYTHONPATH="$ANTENV_PATH/lib/python3.11/site-packages:$PYTHONPATH"
fi

# Start gunicorn
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
