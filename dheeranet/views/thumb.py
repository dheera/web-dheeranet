from flask import Blueprint, render_template, abort, Response, send_file
from jinja2 import TemplateNotFound
from summit.database import db_session
from summit.models import *

from sqlalchemy import desc
from sqlalchemy.orm import subqueryload

import json
import datetime, time, os, io
from subprocess import call

thumb = Blueprint('thumb', __name__,template_folder='../template')

# thumbnail images of database objects to serve to end user
# e.g. /person/1074/100x100 gets a 100x100 thumbnail of person with id 1074

@thumb.route('/<object_type>/<object_id>/',defaults={'size':'120x120'})
@thumb.route('/<object_type>/<object_id>/<size>')
def show(object_type,object_id,size):
  try:
    # restrict the allowed sizes to prevent a DoS attack
    allowed_sizes = ['60x60','120x120','240x240']

    if size not in allowed_sizes:
      abort(404)

    # the source image we are looking for
    src_filename = 'summit/media/thumb/%s/%s' % (object_type, object_id)
  
    # where we hope to find a cached copy, or create one if it doesn't exist
    cache_filename = 'summit/media/thumb/.cache/%s_%s_%s.jpg' % (object_type, object_id, size)

    # look for a cached copy
    if os.path.exists(cache_filename):
      # we have cached it already, just serve it up
      return Response(open(cache_filename).read(), mimetype='image/jpeg')
    else:
      if os.path.exists(src_filename):
        # first time or cache expired, generate a new one
        call(["convert", "-sharpen", "0x0.8", "-strip", src_filename, "-thumbnail", size+"^", "-gravity", "center", "-extent", size, "-quality", "90", cache_filename])
        return Response(open(cache_filename).read(), mimetype='image/jpeg')
      else:
        # requested an object without an image, return a blank GIF
        return Response(open("summit/static/images/blank.gif").read(), mimetype='image/gif')

  except IOError:
    abort(404)
  except TemplateNotFound:
    abort(404)
