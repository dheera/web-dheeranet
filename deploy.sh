#!/bin/sh
rm dheeranet/cache/*
sync
rsync -r -u -v --delete --delete-after --exclude 'README.md' --exclude 'htaccess' --exclude '.git' --exclude '.htaccess' --exclude 'deploy.sh' . /net/s7.dheera.net/www/dheeranet/
