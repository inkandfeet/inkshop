#! /bin/sh
rsync -ac --progress ../inkandfeet-inkshop/ ../inkshop --exclude .git  --exclude .pyc --exclude .DS_Store