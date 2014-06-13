from flask import Blueprint, render_template, abort, redirect
from jinja2 import TemplateNotFound
from dheeranet import objects_bucket
from dheeranet.cache import cache
from ast import literal_eval
import json

pages = Blueprint('pages', __name__,template_folder='../template')

@pages.route('/<path:path>')
def show(path):
  try:

    if path[-1] == '/':
      path += '__index__'

    page = cache.get('pages:page:' + path)

    if not page:
      key = objects_bucket.get_key('pages/' + path)
      if not key:
        key = objects_bucket.get_key('pages/' + path + '/')
        if key:
          return redirect('/' + path + '/', code=302)
        else:
          abort(404)
      page = key.get_contents_as_string().decode('utf-8')
      cache.set('pages:page:' + path, page)

    subnavbar = '[]'
    if path[-1] == '/':
      subnavbar = cache.get('pages:subnavbar:' + path)
      if not subnavbar:
        key = objects_bucket.get_key('pages/' + path + '__nav__')
        if key:
          subnavbar = key.get_contents_as_string().decode('utf-8')
          cache.set('pages:subnavbar:' + path, subnavbar)
        else:
          cache.set('pages:subnavbar:' + path, '[]')
    elif path.find('/'):
      path_trunc = path[0:path.rfind('/')] + '/'
      subnavbar = cache.get('pages:subnavbar:' + path_trunc)
      if not subnavbar:
        key = objects_bucket.get_key('pages/' + path_trunc + '__nav__')
        if key:
          subnavbar = key.get_contents_as_string().decode('utf-8')
          cache.set('pages:subnavbar:' + path_trunc, subnavbar)
        else:
          cache.set('pages:subnavbar:' + path, '[]')

    if not subnavbar:
      subnavbar = '[]'
      
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
      subnavbar=literal_eval(subnavbar)
    )

  except IOError:
    abort(404)
