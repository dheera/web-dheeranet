from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from dheeranet import objects_bucket
from dheeranet.cache import cache

import json

pages = Blueprint('pages', __name__,template_folder='../template')

@pages.route('/<path:path>')
def show(path):
  try:
    path = path.strip('/')

    page = cache.get('pages:' + path)
    if not page:
      key = objects_bucket.get_key('pages/' + path)
      if not key:
        key = objects_bucket.get_key('pages/' + path + '/index')
        if not key:
          abort(404)
      page = key.get_contents_as_string().decode('utf-8')
      cache.set('pages:' + path, page)

    headers_json, content = page.split('\n\n',1);
    headers = json.loads(headers_json)
    return render_template('page.html',title=headers['title'],content=content)
  except IOError:
    abort(404)
  except TemplateNotFound:
    abort(404)
