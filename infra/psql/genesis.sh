#!/bin/bash
#
# Title:genesis.sh
# Description:
# Development Environment: OS X 12.7.6/postgres 15.8
#
psql -U postgres template1 (or psql -U gsc template1)

# (mac) user
createuser -U gsc -d -e -l -P -r -s slug_admin
woofwoof
createuser -U gsc -e -l -P slug_client
batabat

# (linux) su - postgres
createuser -U postgres -d -e -l -P -r -s slug_admin
woofwoof
createuser -U postgres -e -l -P slug_client
batabat

# as pg superuser
# create tablespace slug location '/mnt/pp1/postgres/slug';
# create tablespace slug location '/Library/PostgreSQL/pg_tablespace/slug';
# create tablespace slug location '/usr/local/opt/postgresql@15/pg_tablespace/slug';
# create tablespace slug location '/mnt/pg_tablespace/slug'
#
#createdb slug -O slug_admin -D slug -E UTF8 -T template0 -l C
createdb slug -O slug_admin -E UTF8 -T template0 -l C

# psql -h localhost -p 5432 -U slug_admin -d slug
# psql -h localhost -p 5432 -U slug_client -d slug

# as slug_admin
#create schema slug_v1;
#grant usage on schema slug_v1 to slug_client;

##
## old stuff
##
#create user heeler_client with encrypted password 'batabat';
#create database heeler owner heeler_admin tablespace heeler locale 'C.utf8' template template0;
#create database heeler owner heeler_admin locale 'C.utf8' template template0;

#create role heeler_py with login;
#alter role heeler_py with password 'bogus';

#psql -U heeler_py -d heeler_v1
