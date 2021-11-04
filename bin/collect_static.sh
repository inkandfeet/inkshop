#! /bin/sh
python3 manage.py collectstatic --settings=envs.live_local --noinput
python3 manage.py collectstatic --settings=envs.live --noinput
python3 manage.py compress --settings=envs.live_compress --force
python3 manage.py compilestatic --settings=envs.live
cp -Rv inkshop/collected_static/* inkshop/apps/utils/static/
# python3 manage.py sync_s3 --gzip --settings=envs.live
python3 manage.py collectstatic --settings=envs.live_local --noinput
python3 manage.py collectstatic --settings=envs.live --noinput