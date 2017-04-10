#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, Response, send_file, send_from_directory, request, make_response
import io
from jinja2 import TemplateNotFound
import os, sys
from dheeranet.cache import cached
from PIL import Image, ImageDraw, ImageFont

headline = Blueprint('headline', __name__,template_folder='../template')

@cached()
@headline.route('/<text>')
def show_headline(text):
  size = 40
  color = (200, 200, 200)
  width = size*3
  height = size*3
  font = ImageFont.truetype("dheeranet/res/notosanshant-regular.otf", size*3)
  height = height + 10
  image = Image.new("RGBA", (width, height), (255,255,255))
  draw = ImageDraw.Draw(image)

  draw.text((0, 0), text, color, font=font)

  image = image.resize((width / 2, height / 2), Image.ANTIALIAS)
  image = image.crop((0, 0, width/2, height/2))
  buf = io.StringIO()
  image.save(buf, 'PNG')
  image_data = buf.getvalue()
  buf.close()

  response = make_response(image_data)
  response.headers['Content-Type'] = 'image/png'
  return response

