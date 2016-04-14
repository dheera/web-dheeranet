#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, send_file, send_from_directory, redirect
from flask_sslify import SSLify
from jinja2 import Markup
from boto.s3.connection import S3Connection
import boto.s3.connection
from cache import cached, s3_get_cached
import re
import json
import os
import socket
from urllib2 import quote
from random import randrange
import pygeoip

geoip = pygeoip.GeoIP('/usr/local/share/geoip/GeoIP.dat', pygeoip.MEMORY_CACHE)

s3 = S3Connection(
  open(os.path.dirname(__file__) + '/../.aws_id').read().strip(),
  open(os.path.dirname(__file__) + '/../.aws_secret').read().strip(),
  calling_format = boto.s3.connection.OrdinaryCallingFormat()
)
static_bucket = s3.get_bucket('static.dheera.net')

@cached()
def revdns(ip):
  try:
    if hasattr(socket, 'setdefaulttimeout'):
      socket.setdefaulttimeout(2)
    response = socket.gethostbyaddr(ip)
    return response[0]
  except Exception:
    return ''

def request_hostname():
  return revdns(request.remote_addr)

# replaces chinese characters with images (for headlines)
#def zhimage_filter(code):
#  def replace(char):
#    if char >= u'\u4e00' and char <= u'\u9fff':
#      return u'<img class="char" style="height:1em;margin-top:-10px;" align="absmiddle" src="/headline/' + quote(char.encode('utf-8')) + '">'
#    else:
#      return char
#  return Markup("".join(map(replace, code)))

# parses for host-based filters: {$cn?youku_url}{$!cn?youtube_url$}
def host_filter(code):
  host_tags = []
  host_tags.append(geoip.country_code_by_addr(request.remote_addr).lower())
  host_tags_info = json.loads(s3_get_cached(static_bucket, '__hosts__'))

  hostname = request_hostname()

  for tag, match_str_list in host_tags_info.items():
    for match_str in match_str_list:
      if match_str in hostname:
        host_tags.append(tag)

  def repl_func(subcode):
    subcode_string = subcode.group(0).strip('{$}');
    subcode_search = re.search('(.*?)\?(.*)', subcode_string, flags=re.S)

    if not subcode_search:
      return subcode.group(0)

    if subcode_search.lastindex == 2:
      if subcode_search.group(1)[0] == '!':
        if subcode_search.group(1).lower()[1:] in host_tags:
          return ''
        else:
          return subcode_search.group(2)
      else:
        if subcode_search.group(1).lower() in host_tags:
          return subcode_search.group(2)
        else:
          return ''
    else:
      return subcode.group(0)

  return re.sub('\{\$.*?\$\}', repl_func,code, flags=re.S)

# parses for multi-lingual strings: {|en:apple|zh:蘋果|}
def lang_filter(code):
  def repl_func(subcode):
    if 'HTTP_ACCEPT_LANGUAGE' in request.environ:
      accept_languages = request.environ['HTTP_ACCEPT_LANGUAGE']
    else:
      accept_languages = 'en'

    # check if user has overridden browser language with a cookie
    if 'lang' in request.cookies:
      accept_languages = request.cookies['lang'] + ',' + accept_languages

    # check if user wants to override browser language
    if 'lang' in request.args:
      # todo: actually set the cookie
      accept_languages = request.args['lang'] + ',' + accept_languages

    # build dictionary { 'en' => 'apple', 'zh' => '蘋果‘ }
    subcode_dict=dict()
    for subcode_string in subcode.group(0).strip('{|}').split('|'):
      k, v = subcode_string.split(':',1)
      subcode_dict[k]=v
      if not k[0:2] in subcode_dict:
        subcode_dict[k[0:2]]=v

    # iterate through language preferences and return the first match
    for accept_language in accept_languages.split(','):
      # don't care about q= spec for now, kill it
      accept_language = re.sub(';.*','',accept_language)
      # check if there is an exact match, e.g. zh_TW
      if accept_language in subcode_dict:
        return subcode_dict[accept_language]
      # check if there is an approximate match, e.g. zh
      if accept_language[0:2] in subcode_dict:
        return subcode_dict[accept_language[0:2]]
    # fall back to English
    if 'en' in subcode_dict:
      return subcode_dict['en']
    # fall back to null
    if '' in subcode_dict:
      return subcode_dict['']

  return re.sub('\{\|.*?\|\}',repl_func,code,flags=re.S)

app = Flask(__name__)
sslify = SSLify(app)

app.jinja_options['extensions'].append('jinja2htmlcompress.HTMLCompress')
app.jinja_env.filters['lang'] = lang_filter
app.jinja_env.filters['host'] = host_filter
# app.jinja_env.filters['zhimage'] = zhimage_filter
app.jinja_env.globals.update(request_hostname=request_hostname)
app.jinja_env.globals.update(randrange=randrange)
app.jinja_env.globals.update(request=request)
app.jinja_env.globals.update(enumerate=enumerate)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(min=min)
app.jinja_env.globals.update(max=max)

from views.home import home
app.register_blueprint(home)

from views.headline import headline
app.register_blueprint(headline,url_prefix='/headline')

from views.photos import photos
app.register_blueprint(photos,url_prefix='/photos')

@app.route('/static/<path:filename>')
def send_foo(filename):
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def send_favicon():
    return send_file('static/favicon.ico')

from views.pages import pages
app.register_blueprint(pages)

@app.after_request
def after_request(response):

  hostname = request_hostname()
  #if hostname:
    #if 'embarqhsd' in hostname:
    #  return redirect('http://old.dheera.net/')

    #if 'nj.comcast' in hostname:
    #  return redirect('http://old.dheera.net/')

  if response.headers['Content-Type'].find('image/')==0:
    response.headers['Cache-Control'] = 'max-age=7200, must-revalidate'
    response.headers['Expires'] = '0'
  elif response.headers['Content-Type'].find('application/')==0:
    response.headers['Cache-Control'] = 'max-age=7200, must-revalidate'
    response.headers['Expires'] = '0'
  else:
    response.headers['Cache-Control'] = 'no-cache, must-revalidate'
    response.headers['Expires'] = '0'

  if 'lang' in request.args:
    response.set_cookie('lang', request.args['lang'])
  return response

if __name__ == '__main__':
  print(app.url_map)
  app.run(debug=True)
