#!/bin/bash
set -xeEo pipefail

# rotate the log file otherwise output is lost in cloudwatch
echo "" > /var/log/db_replication/logs.log

# Set env variables
USER=polling_stations
DB=polling_stations
RDS_DB_PASSWORD=dvov7x9k79
RDS_DB_HOST=wdiv-test.cl0ejuxihujo.eu-west-2.rds.amazonaws.com
RDS_DB_NAME=polling_stations_20220505
INSTANCE_ID=`curl http://instance-data/latest/meta-data/instance-id`
SUBSCRIPTION=${USER}_${INSTANCE_ID:2}

dropdb --if-exists $DB -U $USER
createdb $DB -U $USER
psql $DB -U $USER -c 'create extension postgis;'
source /var/www/polling_stations/env/bin/activate && /var/www/polling_stations/code/manage.py migrate
psql $DB -U $USER -c 'TRUNCATE "spatial_ref_sys", "auth_permission", "django_migrations", "django_content_type", "django_site", "pollingstations_customfinder" RESTART IDENTITY CASCADE;'
psql $DB -U $USER -c 'alter table addressbase_address drop constraint addressbase_address_pkey cascade;'
psql $DB -U $USER -c 'alter table addressbase_uprntocouncil drop constraint addressbase_uprntocouncil_pkey cascade;'
psql $DB -U $USER -c 'DROP INDEX addressbase_address_location_id, addressbase_address_postcode_e4d0a0bc, addressbase_address_postcode_e4d0a0bc_like, addressbase_address_uprn_c43af01b_like, addressbase_uprntocouncil_advance_voting_station_id_770ab03a, addressbase_uprntocouncil_uprn_7abf1568_like, lookup_lad_idx;'
psql $DB -U $USER -c "CREATE SUBSCRIPTION $SUBSCRIPTION CONNECTION 'dbname=$RDS_DB_NAME host=$RDS_DB_HOST user=postgres password=$RDS_DB_PASSWORD' PUBLICATION alltables;"

echo "starting initial db sync"

WORKER_STATS=("not-set")
while [ "${WORKER_STATS[0]}" !=  "r" ]
do
    WORKER_STATS=$(psql polling_stations -U polling_stations -AXqtc "select distinct srsubstate from pg_subscription_rel;")
    sleep 15
done

echo "initial db sync complete"

psql $DB -U $USER -c 'ALTER TABLE addressbase_address ADD PRIMARY KEY (uprn);'
psql $DB -U $USER -c 'ALTER TABLE addressbase_uprntocouncil ADD PRIMARY KEY (uprn);'

psql $DB -U $USER -c 'ALTER TABLE addressbase_uprntocouncil ADD CONSTRAINT addressbase_uprntoco_uprn_7abf1568_fk_addressba FOREIGN KEY (uprn) REFERENCES addressbase_uprntocouncil (uprn) MATCH FULL;'
psql $DB -U $USER -c 'CREATE INDEX addressbase_address_location_id ON public.addressbase_address USING gist (location);'
psql $DB -U $USER -c 'CREATE INDEX addressbase_address_postcode_e4d0a0bc ON public.addressbase_address USING btree (postcode);'
psql $DB -U $USER -c 'CREATE INDEX addressbase_address_postcode_e4d0a0bc_like ON public.addressbase_address USING btree (postcode varchar_pattern_ops);'
psql $DB -U $USER -c 'CREATE INDEX addressbase_address_uprn_c43af01b_like ON public.addressbase_address USING btree (uprn varchar_pattern_ops);'
psql $DB -U $USER -c 'CREATE INDEX addressbase_uprntocouncil_advance_voting_station_id_770ab03a ON public.addressbase_uprntocouncil USING btree (advance_voting_station_id);'
psql $DB -U $USER -c 'CREATE INDEX addressbase_uprntocouncil_uprn_7abf1568_like ON public.addressbase_uprntocouncil USING btree (uprn varchar_pattern_ops);'
psql $DB -U $USER -c 'CREATE INDEX lookup_lad_idx ON public.addressbase_uprntocouncil USING btree (lad);'

rm -f ~/server_dirty
