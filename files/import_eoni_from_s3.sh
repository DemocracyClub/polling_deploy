#!/bin/sh
set -e
set -x


LATEST_FILE=$(/usr/local/bin/aws s3 ls s3://eoni-data.wheredoivote.co.uk/production_data/ | sort | tail -n1 | rev | cut -d' ' -f1 | rev)
SRCDIR='/tmp/eoni_production_data'
rm -rf $SRCDIR && mkdir -p $SRCDIR

/usr/local/bin/aws s3 cp s3://eoni-data.wheredoivote.co.uk/production_data/"${LATEST_FILE}" $SRCDIR

/var/www/polling_stations/env/bin/python /var/www/polling_stations/code/manage.py import_eoni --cleanup $SRCDIR/"${LATEST_FILE}"