#!/bin/bash
#
# Title:drop_schema.sh
# Description: remove schema
# Development Environment: OS X 10.15.2/postgres 12.12
# Author: G.S. Cole (guy at shastrax dot com)
#
export PGDATABASE=slug
export PGHOST=localhost
export PGPASSWORD=woofwoof
export PGUSER=slug_admin
#
psql $PGDATABASE -c "drop table slug_load_log"
#
