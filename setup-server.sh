#!/bin/sh
sudo apt-get install lighttpd python-pip imagemagick graphicsmagick git exiftool
sudo pip install boto flup django flask
sudo lighty-enable-mod fastcgi
sudo mkdir /www
sudo git clone https://github.com/dheera/web-dheeranet /www/dheeranet
sudo chown -R ubuntu /www/dheeranet
sudo mv /etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf.default
sudo cp /www/dheeranet/lighttpd.conf /etc/lighttpd/lighttpd.conf
sudo /etc/init.d/lighttpd force-reload
