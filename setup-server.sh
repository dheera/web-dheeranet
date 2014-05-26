apt-get install lighttpd pip imagemagick

pip install boto
pip install flup 
pip install django
pip install flask

lighty-enable-mod fastcgi

mkdir /www
mkdir /www/dheeranet
chown -R ubuntu /www/dheeranet

mv /etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf.default
cp lighttpd.conf /etc/lighttpd/lighttpd.conf

/etc/init.d/lighttpd force-reload
