
#!/bin/bash
set -xeEo pipefail

# rotate the log file otherwise output is lost in cloudwatch
echo "" > /var/log/db_replication/logs.log

USER={{ project_name }}
INSTANCE_ID=`curl http://instance-data/latest/meta-data/instance-id`
SUBSCRIPTION=${USER}_${INSTANCE_ID:2}

drop_subscription () {
    psql -U $USER -c "DROP SUBSCRIPTION $SUBSCRIPTION;"
}

# if subscription is active it will fail - repeat until inactive
until drop_subscription; do
    echo "Trying to drop subscription again..."
done

echo "Subscription dropped"
touch {{ project_root }}/home/server_dirty