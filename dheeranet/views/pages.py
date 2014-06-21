from flask import Blueprint, render_template, abort, redirect
from jinja2 import TemplateNotFound
from dheeranet import objects_bucket
from dheeranet.cache import cached
from ast import literal_eval
import json

pages = Blueprint('pages', __name__,template_folder='../template')

@pages.route('/<path:path>')
def show(path):
  try:


    page = get_page(path)
    if not page:
      abort(404)

    subnavbar = get_subnavbar(path)

    params_json, content = page.split('\n\n',1);
    params = json.loads(params_json)

    if 'title' not in params:
      params['title'] = ''

    if 'subtitle' not in params:
      params['subtitle'] = ''

    return render_template(
      'page.html',
      title=params['title'],
      subtitle=params['subtitle'],
      content=content,
      subnavbar=subnavbar
    )

  except IOError:
    abort(404)

@cached()
def get_page(path, abort_on_not_found=True):
  if path[-1] == '/':
    path += '__index__'

  key = objects_bucket.get_key('pages/' + path)
  if not key:
    key = objects_bucket.get_key('pages/' + path + '/__index__')

  if key:
    return key.get_contents_as_string().decode('utf-8')
  else:
    if abort_on_not_found:
      abort(404)
    return None

@cached()
def get_subnavbar(path):
  key = None

  if path[-1] == '/':
    key = objects_bucket.get_key('pages/' + path + '__nav__')

  if not key:
    key = objects_bucket.get_key('pages/' + path + '/' + '__nav__')

  if not key:
    path_trunc = path[0:path.rfind('/')] + '/'
    key = objects_bucket.get_key('pages/' + path_trunc + '__nav__')

  if key:
    return json.loads(key.get_contents_as_string().decode('utf-8'))
  else:
    return []
