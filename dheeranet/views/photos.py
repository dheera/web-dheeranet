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
PHOTOS_THUMB_WIDTH = 140
PHOTOS_THUMB_HEIGHT = 140
PHOTOS_SMALL_WIDTH = 1024
PHOTOS_LARGE_WIDTH = 2048
PHOTOS_EXIF_AUTHOR = 'Dheera Venkatraman | http://dheera.net'

PHOTOS_FORMAT_ORIGINAL = 'original'
PHOTOS_FORMAT_SMALL = 'web-%d' % PHOTOS_SMALL_WIDTH
PHOTOS_FORMAT_LARGE = 'web-%d' % PHOTOS_LARGE_WIDTH
PHOTOS_FORMAT_THUMB = 'thumb-%d-%d' % (PHOTOS_THUMB_WIDTH, PHOTOS_THUMB_HEIGHT)
PHOTOS_THUMB_SIZE = '%dx%d' % (PHOTOS_THUMB_WIDTH, PHOTOS_THUMB_HEIGHT)

photos = Blueprint('photos', __name__,template_folder='../template')

@photos.route('/')
def show():
  content = generate_photos_home()

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
def generate_photos_home():
  content = ''
  index_key = PHOTOS_BUCKET.get_key(PHOTOS_PREFIX + '__index__')
  index = json.loads(index_key.get_contents_as_string().decode('utf-8'))

  for index_section in index:
    content += '<h2>%s</h2>' % index_section['title']
    if 'show' not in index_section:
      subpaths = PHOTOS_BUCKET.list(PHOTOS_PREFIX + index_section['path'] + '/', '/')
      subpaths = map(lambda(k): k.name.encode('utf-8'), subpaths)
      subpaths = map(lambda(s): s[s.rfind('/')+1:], subpaths)
      for subpath in subpaths:
          content += '<h3>%s</h3>' % subpath
  return content

@cached()
def album_get_info(album):
  info_key = PHOTOS_BUCKET.get_key(PHOTOS_PREFIX + album + '/__info__')
  if info_key:
    return json.loads(info_key.get_contents_as_string().decode('utf-8'))
  else:
    return None

@cached()
def album_get_filenames(album,pic_format = PHOTOS_FORMAT_ORIGINAL):
  filenames = PHOTOS_BUCKET.list(PHOTOS_PREFIX + album + '/' + pic_format + '/', '/')
  filenames = map(lambda(k): k.name.encode('utf-8'), filenames)
  filenames = map(lambda(s): s[s.rfind('/')+1:], filenames)
  return filenames

def album_get_display_url(album,filename):
  return "http://%s/%s%s/%s/%s" % (PHOTOS_BUCKET_NAME, PHOTOS_PREFIX, album, PHOTOS_FORMAT_SMALL, filename)

def album_get_download_url(album,filename):
  return "http://%s/%s%s/%s/%s" % (PHOTOS_BUCKET_NAME, PHOTOS_PREFIX, album, PHOTOS_FORMAT_ORIGINAL, filename)

def album_get_thumb_url(album,filename):
  return "http://%s/%s%s/%s/%s" % (PHOTOS_BUCKET_NAME, PHOTOS_PREFIX, album, PHOTOS_FORMAT_THUMB, filename)

def album_get_photo(album,filename,local_filename,pic_format = PHOTOS_FORMAT_ORIGINAL):
  key = PHOTOS_BUCKET.get_key(PHOTOS_PREFIX + album + '/' + pic_format + '/' + filename)

  if key:
    key.get_contents_to_filename(local_filename)

  else:
    raise Exception("Nonexistent photo")

def album_put_photo(album,filename,local_filename,pic_format):

  # re-generatable formats, can overwrite, use reduced redundancy storage
  if pic_format in (PHOTOS_FORMAT_LARGE, PHOTOS_FORMAT_SMALL, PHOTOS_FORMAT_THUMB):
    key = PHOTOS_BUCKET.get_key(PHOTOS_PREFIX + album + '/' + pic_format + '/' + filename)
    key.set_contents_from_filename(local_filename, reduced_redundancy == True)

  # don't overwrite existing originals, use normal S3 storage
  elif pic_format == PHOTOS_FORMAT_ORIGINAL:
    key = PHOTOS_BUCKET.get_key(PHOTOS_PREFIX + album + '/' + pic_format + '/' + filename)
    if not key:
      key.set_contents_from_filename(local_filename)

  else:
    raise Exception("Invalid picture format: " + pic_format)
