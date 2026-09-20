#!/bin/bash
#
# Title: slug-validate.sh
# Description: verify collection files
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
echo "start validate"
#
docker rm slug;docker run -v /var/wombat:/mnt/wombat --name slug slug:latest
#
echo "end validate"
#
