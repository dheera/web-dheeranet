from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound

import json

home = Blueprint('home', __name__,template_folder='../template')

@home.route('/')
def show():
  return lang(render_template('home.html'))

def lang(text):
  lang_cookie = request.cookies.get('lang')
  lang_final = ('en','zh')
  return text
