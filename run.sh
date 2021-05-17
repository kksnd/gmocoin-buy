#!/bin/bash

DIR=/your/path/to/this/repo

LOG=${DIR}/run.log

date >> "$LOG"
cd "$DIR" || exit

python main.py >> "$LOG" 2>&1
date >> "$LOG"
