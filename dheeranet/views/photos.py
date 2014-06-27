#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, Response, send_file, send_from_directory, request
from jinja2 import TemplateNotFound
from subprocess import call
from dheeranet import static_bucket
from dheeranet.cache import cache, cached, s3_get_cached, s3_list_cached
from dheeranet.slugify import slugify
from boto.s3.key import Key
import os, glob, sys
import json
from hashlib import sha1
import random
import datetime

PHOTOS_BUCKET = static_bucket
PHOTOS_PREFIX = 'photos/'
PHOTOS_THUMB_WIDTH = 140
PHOTOS_THUMB_HEIGHT = 140
PHOTOS_THUMB2_WIDTH = 200
PHOTOS_THUMB2_HEIGHT = 200
PHOTOS_SMALL_WIDTH = 1024
PHOTOS_LARGE_WIDTH = 2048
PHOTOS_EXIF_AUTHOR = 'Dheera Venkatraman | http://dheera.net'

PHOTOS_BUCKET_NAME = PHOTOS_BUCKET.name
PHOTOS_FORMAT_ORIGINAL = 'original'
PHOTOS_FORMAT_SMALL = 'web-{}'.format(PHOTOS_SMALL_WIDTH)
PHOTOS_FORMAT_LARGE = 'web-{}'.format(PHOTOS_LARGE_WIDTH)
PHOTOS_FORMAT_THUMB = 'thumb-{}-{}'.format(PHOTOS_THUMB_WIDTH, PHOTOS_THUMB_HEIGHT)
PHOTOS_FORMAT_THUMB2 = 'thumb-{}-{}'.format(PHOTOS_THUMB2_WIDTH, PHOTOS_THUMB2_HEIGHT)
PHOTOS_THUMB_SIZE = '{}x{}'.format(PHOTOS_THUMB_WIDTH, PHOTOS_THUMB_HEIGHT)

photos = Blueprint('photos', __name__,template_folder='../template')

@photos.route('/')
def show():

  return render_template('photos.html',
    title = u'{|en:photos|zh:相冊|}',
    sections = get_home_sections()
  )


@photos.route('/banner')
def show_banner():
  now = datetime.datetime.now()
  random.seed((now.year, now.month, now.day, now.hour))
  banner_list = s3_get_cached(PHOTOS_BUCKET,
                  PHOTOS_PREFIX + '__banner__',
                  timeout = 86400).split('\n')
  banner_list = map(lambda x:x.strip().split(','), banner_list)
  banner_list = filter(lambda x: len(x)==2, banner_list)
  banner_list = random.sample(banner_list, 10)
  urls = map(lambda x:album_get_url(x[0], x[1], PHOTOS_FORMAT_SMALL), banner_list)

  return render_template('photos-banner.html',
    title = u'banner',
    urls = urls
  )


@photos.route('/download/<path:album>/<filename>')
def show_download(album, filename):
  album_info = album_get_info(album)
  if not album_info:
    abort(404)

  return render_template('photos-download.html',
    title = u'{|en:download original|zh:下載原始照片|}',
    preview_url = album_get_url(album, filename, pic_format = PHOTOS_FORMAT_SMALL),
    download_url = album_get_url(album, filename, pic_format = PHOTOS_FORMAT_ORIGINAL),
  )


@photos.route('/<path:album>')
def show_album(album):
  album = album.strip('/')
  album_info = album_get_info(album)
  if not album_info:
    abort(404)
  album_filenames = album_list_filenames(album)

  album_images = map(
    lambda filename:
      { 
       'album': album,
       'id': filename.replace('.jpg',''),
       'filename': filename,
       'display_url': album_get_url(album, filename, pic_format = PHOTOS_FORMAT_SMALL),
       'thumb_url': album_get_url(album, filename, pic_format = PHOTOS_FORMAT_THUMB),
       'download_url': '/photos/download/{}/{}'.format(album, filename)
      },
    album_filenames
  )

  return render_template('photos-album.html',
    album_info = album_info,
    album_images = album_images,
    like_buttons = False
  )

def list_albums(path, force_recache = False):
  albums = s3_list_cached(PHOTOS_BUCKET,
    PHOTOS_PREFIX + path + '/', '/',
    force_recache = force_recache)
  albums = map(lambda(k): k.strip('/').replace('photos/',''), albums)
  if path in albums:
    albums.remove(path)
  return [album for album in albums if album_get_info(album)]

@cached()
def get_home_sections():
  index = json.loads(s3_get_cached(PHOTOS_BUCKET,
                  PHOTOS_PREFIX + '__featured__',
                  timeout = 1200))
  sections = []

  for index_section in index:
    section = {}
    section['title'] = index_section['title']

    if 'albums' in index_section:
      albums = index_section['albums']

    else:
      albums = list_albums(index_section['path'])
      if index_section['sort']:
        albums.sort(reverse=(index_section['sort']=="reverse"))

    album_infos = filter(lambda x:x!=None, map(album_get_info, albums))

    album_infos = map(
      lambda album_info:
        album_info.update({
          'thumb_url': album_get_url(album_info['album'], album_info['cover'], pic_format = PHOTOS_FORMAT_THUMB),
          'thumb2_url': album_get_url(album_info['album'], album_info['cover'], pic_format = PHOTOS_FORMAT_THUMB2),
        }) or album_info,
        album_infos
    )
    section['albums'] = album_infos
    sections.append(section)

  return sections

def album_get_info(album):
  info_json = s3_get_cached(PHOTOS_BUCKET,
                PHOTOS_PREFIX + album + '/__info__',
                timeout = 86400)

  if not info_json:
    return None

  try:
    info = json.loads(info_json)
    info['album'] = album
    if 'date' not in info:
      if album[album.find('/')+1:][0:8].isdigit():
        info['date'] = album[album.rfind('/')+1:][0:8]
      else:
        info['date'] = None
    if 'cover' not in info:
      info['cover'] = album_list_filenames(album)[0]
    if 'title' not in info:
      info['title'] = album
    return info

  except ValueError, e:
    print "error: invalid json: %s" % info_json
    return None

def album_list_filenames(album, pic_format = PHOTOS_FORMAT_ORIGINAL, force_recache = False):
  filenames = s3_list_cached(PHOTOS_BUCKET,
    PHOTOS_PREFIX + album + '/' + pic_format + '/', '/',
    force_recache = force_recache)
  filenames = map(lambda(k): k.strip('/'), filenames)
  filenames = map(lambda(s): s[s.rfind('/')+1:], filenames)
  filenames = filter(lambda x: x.endswith('.jpg') or x.endswith('.png'), filenames)
  return filenames

def album_get_url(album,filename,pic_format=PHOTOS_FORMAT_ORIGINAL):
  return "http://{bucket_name}/{prefix}{album}/{pic_format}/{filename}".format(
    bucket_name = PHOTOS_BUCKET_NAME,
    prefix = PHOTOS_PREFIX,
    album = album,
    pic_format = pic_format,
    filename = filename,
  )

def album_get_key(album, filename, pic_format = PHOTOS_FORMAT_ORIGINAL, create = False):
  key_name = PHOTOS_PREFIX + album + '/' + pic_format + '/' + filename
  key = PHOTOS_BUCKET.get_key(key_name)
  if create and not key:
    key = PHOTOS_BUCKET.new_key(key_name)
  return key
    

def album_get_photo(album, filename, local_filename, pic_format = PHOTOS_FORMAT_ORIGINAL):
  key = album_get_key(album, filename, pic_format)
  if key:
    key.get_contents_to_filename(local_filename)
  else:
    raise Exception("Nonexistent photo")

def album_put_photo(album, filename, local_filename, pic_format):

  # re-generatable formats, can overwrite, use reduced redundancy storage
  if pic_format in (PHOTOS_FORMAT_LARGE, PHOTOS_FORMAT_SMALL, PHOTOS_FORMAT_THUMB, PHOTOS_FORMAT_THUMB2):
    key = album_get_key(album, filename, pic_format = pic_format, create = True)
    key.set_contents_from_filename(local_filename, reduced_redundancy = True)

  # don't overwrite existing originals, use normal S3 storage
  elif pic_format == PHOTOS_FORMAT_ORIGINAL:
    key = album_get_key(album, filename, pic_format = pic_format, create = False)
    if not key:
      key = album_get_key(album, filename, pic_format = pic_format, create = True)
      key.set_contents_from_filename(local_filename)

  else:
    raise Exception("Invalid picture format: " + pic_format)
