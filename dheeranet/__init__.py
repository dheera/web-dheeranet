#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask,request,render_template,send_file,send_from_directory,redirect
from jinja2 import Markup
from boto.s3.connection import S3Connection
import re

s3 = S3Connection(open('.aws_id').read().strip(),open('.aws_secret').read().strip())

objects_bucket = s3.get_bucket('objects.dheera.net')
photos_bucket = s3.get_bucket('photos.dheera.net')
static_bucket = s3.get_bucket('static.dheera.net')

# parse multilingual HTML
def lang(code):
  # function to parse one string unit {|en:apple|zh:蘋果|}
  def repl_func(subcode):
    accept_languages = request.environ['HTTP_ACCEPT_LANGUAGE']

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
app.jinja_options['extensions'].append('jinja2htmlcompress.HTMLCompress')
app.jinja_env.filters['lang'] = lang

from views.home import home
app.register_blueprint(home)

from views.photos import photos
app.register_blueprint(photos,url_prefix='/photos')

# silly werkzeug issue <path:filename> doesn't work in root with dev server
# http://stackoverflow.com/questions/17135006/url-routing-conflicts-for-static-files-in-flask-dev-server

@app.route('/static/<filename>')
def send_static_0(filename):
  return redirect('http://static.dheera.net/'+filename)

@app.route('/static/<subdir>/<path:filename>')
def send_static_1(subdir,filename):
  return redirect('http://static.dheera.net/'+subdir+'/'+filename)

from views.pages import pages
app.register_blueprint(pages)

@app.after_request
def add_header(response):
  if(response.headers['Content-Type'].find('image/')==0):
    # tell client to cache images for 2 hours
    response.headers['Cache-Control'] = 'max-age=7200, must-revalidate'
    response.headers['Expires'] = '0'
  elif(response.headers['Content-Type'].find('application/')==0):
    # tell client to cache downloads for 2 hours
    response.headers['Cache-Control'] = 'max-age=7200, must-revalidate'
    response.headers['Expires'] = '0'
  else:
    # tell client to cache everything else (especially text/html) for 5 minutes only
    # in case urgent updates to content need to be made
    response.headers['Cache-Control'] = 'max-age=300, must-revalidate'
    response.headers['Expires'] = '0'
  return response

if __name__ == '__main__':
  print(app.url_map)
  app.run(debug=True)
