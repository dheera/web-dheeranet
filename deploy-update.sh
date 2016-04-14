#!/bin/bash
ssh ubuntu@dheera.net 'cd /www/dheeranet && git pull && sudo /etc/init.d/memcached restart'
