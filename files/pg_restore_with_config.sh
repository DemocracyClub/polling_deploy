#!/bin/bash

conf_dir=/etc/postgresql/10/main
main_config=$conf_dir/postgresql.conf

mkdir -p "$conf_dir/conf.d"
egrep -q '^include_dir' $main_config || echo "include_dir 'conf.d'" >> $main_config

( echo "fsync=off";
  echo "full_page_writes=off";
  echo "checkpoint_segments=32";
  echo "autovacuum=off";
  echo "work_mem=16MB";
  echo "maintenance_work_mem=256MB";
) > "$conf_dir/conf.d/pg_restore.conf"

undo_conf() {
  rm -f $conf_dir/conf.d/pg_restore.conf
  service postgresql restart
}
trap undo_conf "EXIT"

service postgresql restart
sudo -u postgres pg_restore "$@"
status=$?
service postgresql restart
exit $status
