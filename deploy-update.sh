#!/bin/bash
ssh ubuntu@s7.dheera.net 'cd /www/dheeranet && git pull && sudo /etc/init.d/memcached restart'
