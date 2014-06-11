from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound

import json

banner = Blueprint('banner', __name__,template_folder='../template')

@banner.route('/banner')
def show():
  return render_template('banner.html')

