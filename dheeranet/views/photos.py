from flask import Blueprint, render_template, abort, Response, send_file, send_from_directory
from jinja2 import TemplateNotFound
from subprocess import call
from dheeranet import static_bucket
from dheeranet.cache import cache
from dheeranet.slugify import slugify
from boto.s3.key import Key
import os, glob
import json
from hashlib import sha1

PHOTOS_THUMB_WIDTH = '140'
PHOTOS_THUMB_HEIGHT = '140'
PHOTOS_THUMB_SIZE = PHOTOS_THUMB_WIDTH + 'x' + PHOTOS_THUMB_HEIGHT

photos = Blueprint('photos', __name__,template_folder='../template')

@photos.route('/', defaults={'album': ''})
@photos.route('/<path:album>')
def show(album):
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

def album_get_info(album):
  info_json = cache.get('photos:info:' + album)
  if not info_json:
    info_key = static_bucket.get_key('photos/'+album+'/info')
    if info_key:
      info_json = info_key.get_contents_as_string().decode('utf-8')
      cache.set('photos:info:' + album, info_json)
    else:
      return None

  info = json.loads(info_json)
  return info

def album_get_filenames(album):
  filenames = ()
  filenames_json = cache.get('photos:filenames:' + album)

  if filenames_json:
    filenames = json.loads(filenames_json)
  else:
    filenames = static_bucket.list('photos/'+album+'/web-1024/','/')
    filenames = map(lambda(k): k.name.encode('utf-8'), filenames)
    filenames = map(lambda(s): s[s.rfind('/')+1:], filenames)
    cache.set('photos:filenames:' + album, json.dumps(filenames))

  return filenames

def album_get_display_url(album,filename):
  return "http://static.dheera.net/photos/%s/web-1024/%s" % (album, filename)

def album_get_download_url(album,filename):
  return "http://static.dheera.net/photos/%s/original/%s" % (album, filename)

def album_get_thumb_url(album,filename):
  return "http://static.dheera.net/photos/%s/thumb-%s-%s/%s" % (album, PHOTOS_THUMB_WIDTH, PHOTOS_THUMB_HEIGHT, filename)
