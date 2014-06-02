from flask import Blueprint, render_template, abort, Response, send_file, send_from_directory
from jinja2 import TemplateNotFound
from subprocess import call
from dheeranet import static_bucket
from dheeranet import photos_bucket
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

  album_files = photos_bucket.list(album+'/web-1024/','/')
  thumb_files = photos_bucket.list('thumb/' + PHOTOS_THUMB_SIZE + '/' + album + '/','/')

  thumbs=list()

  for key in thumb_files:
    thumbs.append(key.name.encode('utf-8').replace('thumb/' + PHOTOS_THUMB_SIZE + '/' + album + '/',''))

  for key in album_files:
    filename = key.name.encode('utf-8').replace(album+'/web-1024/','')
    if filename[-4:] == '.jpg':

      display_url = 'http://photos.dheera.net/' + album + '/web-1024/' + filename
      download_url = 'http://photos.dheera.net/' + album + '/' + filename
      thumb_url = 'http://photos.dheera.net/thumb/' + PHOTOS_THUMB_SIZE + '/' + album + '/' + filename

      if not filename in thumbs:
        print 'Creating thumbnail for '+filename
        original_tempfilename = '/tmp/foo_original.jpg'
        key.get_contents_to_filename(original_tempfilename)
        resized_tempfilename = '/tmp/foo_resized.jpg'
        call(["convert", "-strip", original_tempfilename, "-thumbnail", PHOTOS_THUMB_SIZE + "^", "-gravity", "center", "-sharpen", "0x0.7", "-extent", PHOTOS_THUMB_SIZE, resized_tempfilename])
        resized_key = Key(photos_bucket)
        resized_key.key = 'thumb/' + PHOTOS_THUMB_SIZE + '/' + album + '/' + filename
        resized_key.set_contents_from_filename(resized_tempfilename)

      content += "<div class=\"photos_thumbnail clickable\">"
      content += '<a href="%s"><img data-download="%s" src="%s" width="%s" height="%s"></a>' % (display_url, download_url, thumb_url, PHOTOS_THUMB_WIDTH, PHOTOS_THUMB_HEIGHT)
      content += "</div> "

  return render_template('page.html',title='Photos',content=content)
