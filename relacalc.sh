#!/usr/bin/env bash

SCRIPT_NAME="relacalc.py"

SCRIPT_HOME="$(dirname "$(realpath "$0")")"
echo "Real path to RelaNotes is $SCRIPT_HOME"
SCRIPT_MAIN="$SCRIPT_HOME/$SCRIPT_NAME"
python3 "$SCRIPT_MAIN"

