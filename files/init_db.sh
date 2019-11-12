#!/bin/sh
set -e
set -x

# This script helps us to work around poor EBS performance
# on first disk read after restoring a volume from a snapshot. See:
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSPerformance.html
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-initialize.html
# Basically: After restoring from shapshot, the first read on any block
# is a network access, not a disk access.

# By running pg_dump > /dev/null on the two most performance-ciritcal
# tables in our DB, we ensure that all the blocks relating to those tables
# have been touched at least once before we mark the server 'healthy'
# and allow the ELB to start forwarding traffic to it.
# Doing this gets us to an acceptable level of performance.
# We'll also continue to 'warm' the ONSUD table in the background
# while the server is under load.

# don't run this script if we're building an image
/usr/local/bin/instance-tags 'Env=packer-ami-build' && exit 0

# ensure the dirver is marked dirty before we start
rm ~/clean || true

# have a little snooze to ensure the postgres
# service has started before we try to run pg_dump
sleep 30

# dump a bunch of tables in parallel
pg_dump -d polling_stations -t addressbase_address > /dev/null &
pg_dump -d polling_stations -t pollingstations_residentialaddress > /dev/null &
pg_dump -d every_election -t uk_geo_utils_onspd > /dev/null &
pg_dump -d every_election -t organisations_divisiongeography > /dev/null &
pg_dump -d every_election -t organisations_organisationgeography > /dev/null &

wait
# once both of those are done, make the server clean
# we can swap it in now
touch ~/clean

# continue dumping the ONSUD table in the background
pg_dump -d polling_stations -t addressbase_onsud > /dev/null
