#!/bin/sh
set -e
set -x


LATEST_FILE=$(/usr/local/bin/aws s3 ls s3://eoni-data.wheredoivote.co.uk/production_data/ | sort | tail -n1 | rev | cut -d' ' -f1 | rev)
SRCDIR='/tmp/eoni_production_data'
rm -rf $SRCDIR && mkdir -p $SRCDIR

/usr/local/bin/aws s3 cp s3://eoni-data.wheredoivote.co.uk/production_data/"${LATEST_FILE}" $SRCDIR

echo '"PREM_X_4326","PREM_Y_4326"' > prem_4326.csv
mlr --icsv --otsv --headerless-csv-output cut -f PREM_X_COR,PREM_Y_COR $SRCDIR/"${LATEST_FILE}" |
	cs2cs -f "%.6f" +init=epsg:29902 +to +init=epsg:4326 |
	awk '{print "\""$1"\",\""$2"\""}' >> PREM_4326.csv

echo '"PRO_X_4326","PRO_Y_4326"' > pro_4326.csv
mlr --icsv --otsv --headerless-csv-output cut -f PRO_X_COR,PRO_Y_COR $SRCDIR/"${LATEST_FILE}" |
	cs2cs -f "%.6f" +init=epsg:29902 +to +init=epsg:4326 |
	awk '{print "\""$1"\",\""$2"\""}'  >> PRO_4326.csv

paste -d ',' PRO_4326.csv PREM_4326.csv $SRCDIR/"${LATEST_FILE}" > eoni_reprojected.csv

/var/www/polling_stations/env/bin/python /var/www/polling_stations/code/manage.py import_eoni --cleanup --reprojected eoni_reprojected.csv

rm PREM_4326.csv PRO_4326.csv eoni_reprojected.csv