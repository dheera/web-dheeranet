from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from dheeranet import static_bucket
from dheeranet.cache import s3_get_cached
import json, datetime

home = Blueprint('home', __name__,template_folder='../template')

@home.route('/')
def show():
  home_items = json.loads(s3_get_cached(static_bucket, '__home__'))
  news_items = filter(lambda x:x['type']=='news', home_items)

  return render_template('home.html', news_items = news_items)
