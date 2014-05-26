#!/bin/sh
rm summit/cache/*
sync
#rsync -r -u -v --delete --delete-after --exclude 'README.md' --exclude 'htaccess' --exclude '.git' --exclude '.htaccess' --exclude 'deploy.sh' . /mit/sustainability/web_scripts/summit/
