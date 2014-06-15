#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, Response, send_file, send_from_directory
from jinja2 import TemplateNotFound
from subprocess import call
from dheeranet import static_bucket
from dheeranet.cache import cache, cached
from dheeranet.slugify import slugify
from boto.s3.key import Key
import os, glob
import json
from hashlib import sha1

PHOTOS_BUCKET = static_bucket
PHOTOS_BUCKET_NAME = 'static.dheera.net'
PHOTOS_PREFIX = 'photos/'
PHOTOS_THUMB_WIDTH = '140'
PHOTOS_THUMB_HEIGHT = '140'

PHOTOS_THUMB_SIZE = PHOTOS_THUMB_WIDTH + 'x' + PHOTOS_THUMB_HEIGHT

photos = Blueprint('photos', __name__,template_folder='../template')

@photos.route('/')
def show():
  content = ''

  featured_json = cache.get('photos:featured')
  if not featured_json:
    featured_key = PHOTOS_BUCKET.get_key('photos/featured')
    if featured_key:
      featured_json = featured_key.get_contents_as_string().decode('utf-8')
      cache.set('photos:featured', featured_json)

  featured = json.loads(featured_json)

  for featured_section in featured:
    content += '<h2>%s</h2>' % featured_section['title']

  return render_template('page.html',title='{|en:photos|zh:相冊|}',content=content)

@photos.route('/<path:album>')
def show_album(album):
  content = ''
  album = album.strip('/')

  album_info = album_get_info(album)
  if not album_info:
    abort(404)

  album_filenames = album_get_filenames(album)

  for filename in album_filenames:

    if filename.endswith('.jpg'):

      display_url = album_get_display_url(album,filename)
      download_url = album_get_download_url(album,filename)
      thumb_url = album_get_thumb_url(album,filename)

      content += "<div class=\"photos_thumbnail clickable\">"
      content += '<a href="%s"><img data-download="%s" src="%s" width="%s" height="%s"></a>' % (display_url, download_url, thumb_url, PHOTOS_THUMB_WIDTH, PHOTOS_THUMB_HEIGHT)
      content += "</div> "

  return render_template('page.html',title=album_info['title'],content=content)

@cached()
def album_get_info(album):
  info_key = PHOTOS_BUCKET.get_key('photos/'+album+'/info')
  if info_key:
    return json.loads(info_key.get_contents_as_string().decode('utf-8'))
  else:
    return None

@cached()
def album_get_filenames(album):
  filenames = PHOTOS_BUCKET.list('photos/'+album+'/web-1024/','/')
  filenames = map(lambda(k): k.name.encode('utf-8'), filenames)
  filenames = map(lambda(s): s[s.rfind('/')+1:], filenames)
  return filenames

def album_get_display_url(album,filename):
  return "http://%s/%s%s/web-1024/%s" % (PHOTOS_BUCKET_NAME, PHOTOS_PREFIX, album, filename)

def album_get_download_url(album,filename):
  return "http://%s/%s%s/original/%s" % (PHOTOS_BUCKET_NAME, PHOTOS_PREFIX, album, filename)

def album_get_thumb_url(album,filename):
  return "http://%s/%s%s/thumb-%s-%s/%s" % (PHOTOS_BUCKET_NAME, PHOTOS_PREFIX, album, PHOTOS_THUMB_WIDTH, PHOTOS_THUMB_HEIGHT, filename)
