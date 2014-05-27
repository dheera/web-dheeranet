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

photos = Blueprint('photos', __name__,template_folder='../template')

#@photos.route('/<album>/<photo>/<size>')
#def get_photo_resized(album,photo,size):
#  allowed_sizes = ['154x154','300x200','600x400']
#
#  if '..' in album or album.startswith('/'):
#    abort(404)
#  if '..' in photo or photo.startswith('/'):
#    abort(404)
#  if size not in allowed_sizes:
#    abort(404)
#
#  image_file = PHOTOS_DIR + '/' + album + '/' + photo
#  thumb_file = CACHE_DIR + '/photos-'+slugify(album+'-'+photo)+'-'+size+'.jpg'
#  thumb_url = 'static/cache/photos-'+slugify(album+'-'+photo)+'-'+size+'.jpg'
#
#  if not os.path.exists(thumb_file):
#    call(["convert", "-strip", image_file, "-thumbnail", size+"^", "-gravity", "center", "-quality", "83", "-extent", size, thumb_file])
#
#  return send_file('../'+thumb_file)


#@photos.route('/<album>/<photo>')
#def get_photo(album,photo):
#  if '..' in album or album.startswith('/'):
#    abort(404)
#  if '..' in photo or photo.startswith('/'):
#    abort(404)
#
#  image_file = PHOTOS_DIR + '/' + album + '/' + photo
#  return send_file('../' + image_file)

def get_resized_url(filename,width,height,full=0):
  original_key = photos_bucket.get_key(filename)

  if not original_key:
    print 'Error'
    return 'http://static.dheera.net/images/blank.gif'

  size = str(width) + 'x' + str(height)

  resized_filename = 'cache/%s-%s-%s-%s.jpg' % (sha1('photos/' + filename + '/').hexdigest(), width, height, full)
  resized_url = 'http://static.dheera.net/' + resized_filename

  resized_key = static_bucket.get_key(resized_filename)

  print resized_filename
  print resized_url

  if not resized_key:
    resized_key = Key(static_bucket)
    resized_key.key = resized_filename

    original_tempfilename = '/tmp/foo_original.jpg'
    original_key.get_contents_to_filename(original_tempfilename)

    resized_tempfilename = '/tmp/foo_resized.jpg'

    call(["convert", "-strip", original_tempfilename, "-thumbnail", size+"^", "-gravity", "center", "-quality", "83", "-extent", size, resized_tempfilename])

    resized_key.set_contents_from_filename(resized_tempfilename)

  return resized_url

@photos.route('/', defaults={'album': ''})
@photos.route('/<path:album>')
def show(album):
  content = ''
  album_files = photos_bucket.list(album+'/','/')
  for key in album_files:
    filename = key.name.encode('utf-8')
    if filename[-4:] == '.jpg':

      download_url = 'http://photos.dheera.net/' + filename
      display_url = get_resized_url(filename,width=1024,height=680,full=1)
      thumb_url = get_resized_url(filename,width=140,height=140)

      content += "<div class=\"photos_thumbnail clickable\">"
      content += '<a href="%s"><img src="%s" width="100" height="100"></a> ' % (download_url, thumb_url)
      content += "</div> "

  return render_template('page.html',title='Photos',content=content)
