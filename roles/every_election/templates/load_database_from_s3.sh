#!/bin/sh
set -e
set -x

# Get the latest backup file
LATEST_FILE=`s3cmd ls s3://dc-ee-short-term-backups/every_election/ | sort | tail -n 1 | rev | cut -d' ' -f 1 | rev`
FILENAME=`echo $LATEST_FILE | rev | cut -d '/' -f 1 | rev`
SRCDIR='/tmp/s3backups_{{ ee_name }}'
mkdir -p $SRCDIR


# database access details
HOST='127.0.0.1'
PORT='5432'
USER='{{ ee_name }}'
DB={{ ee_name }}


echo $FILENAME
s3cmd get --skip-existing $LATEST_FILE $SRCDIR --region=eu-west-2
dropdb -U $USER $DB
createdb -U $USER $DB
pg_restore -j 2 -U $USER  -d $DB  $SRCDIR/$FILENAME
rm $SRCDIR/*
