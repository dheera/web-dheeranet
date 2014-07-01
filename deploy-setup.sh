#!/bin/sh
sudo apt-get install lighttpd python-pip imagemagick graphicsmagick git exiftool memcached vim
sudo pip install boto flup django flask python-memcached pygeoip
sudo lighty-enable-mod fastcgi accesslog
sudo mkdir /www
sudo git clone https://github.com/dheera/web-dheeranet /www/dheeranet
sudo chown -R ubuntu /www/dheeranet
sudo mv /etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf.default
sudo cp /www/dheeranet/lighttpd.conf /etc/lighttpd/lighttpd.conf
sudo /etc/init.d/lighttpd force-reload

sudo wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz -O /tmp/GeoIP.dat.gz
sudo gunzip /tmp/GeoIP.dat.gz
sudo mkdir /usr/local/share/geoip
sudo mv /tmp/GeoIP.dat /usr/local/share/geoip/

