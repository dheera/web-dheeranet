#!/bin/sh
sudo apt-get install nginx python-pip imagemagick graphicsmagick git exiftool memcached vim uwsgi uwsgi-plugin-python
sudo pip install boto flup django flask python-memcached pygeoip uwsgi
sudo lighty-enable-mod fastcgi accesslog
sudo mkdir /www
sudo git clone https://github.com/dheera/web-dheeranet /www/dheeranet
sudo chown -R ubuntu /www/dheeranet

# lighttpd
# sudo mv /etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf.default
# sudo cp /www/dheeranet/lighttpd.conf /etc/lighttpd/lighttpd.conf
# sudo /etc/init.d/lighttpd force-reload

# nginx
sudo rm /etc/nginx/sites-available/*
sudo rm /etc/nginx/sites-enabled/*
sudo cp nginx/dheeranet /etc/nginx/sites-available/dheeranet
sudo ln -s /etc/nginx/sites-available/dheeranet /etc/nginx/sites-enabled/dheeranet
sudo cp uwsgi/dheeranet.ini /etc/uwsgi/apps-available/dheeranet.ini
sudo ln -s uwsgi/dheeranet.ini /etc/uwsgi/apps-available/dheeranet.ini /etc/uwsgi/apps-enabled/dheeranet.ini

sudo /etc/init.d/uwsgi start
sudo /etc/init.d/nginx start

sudo wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz -O /tmp/GeoIP.dat.gz
sudo gunzip /tmp/GeoIP.dat.gz
sudo mkdir /usr/local/share/geoip
sudo mv /tmp/GeoIP.dat /usr/local/share/geoip/

# search for and rebuild any lost objects
# (low res versions stored as reduced redundancy)
sudo ln -s /www/dheeranet/photos_gen_sizes.py /etc/cron.hourly
