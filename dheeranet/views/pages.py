from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from dheeranet import objects_bucket

import json

pages = Blueprint('pages', __name__,template_folder='../template')

@pages.route('/<path>')
@pages.route('/<path>/')
def show(path):
  try:
    isHeaderFinished=0
    header_json=''
    content=''

    key = objects_bucket.get_key('pages/' + path)
    content = key.get_contents_as_string().decode('utf-8')
#    with open('pages/' + pages) as fp:
#      for line in fp:
#        if(line.strip()==''):
#          isHeaderFinished=1
#        if(isHeaderFinished):
#          content+=line.decode('utf-8')
#        else:
#          header_json+=line.decode('utf-8')
#    print 'Loaded'
#    header = json.loads(header_json)
#    print 'JSON decoded'
    return render_template('page.html',title='foo',content=content)
  except IOError:
    abort(404)
  except TemplateNotFound:
    abort(404)
