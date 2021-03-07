#!/usr/bin/env bash

export PATH="$PATH:/usr/local/bin"

REALPATH=$(realpath "$0")
DIR=$(dirname $REALPATH)
$DIR/env/bin/python $DIR/bitbar-gmail-notifier-impl.py
