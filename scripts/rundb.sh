#!/usr/bin/env bash
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATADIR=$BASEDIR/../mongodb_data
mongod --dbpath $DATADIR