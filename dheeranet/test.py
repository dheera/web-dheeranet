#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib2 import quote

def zh_image_filter(code):
  def replace(char):
    if char >= u'\u4e00' and char <= u'\u9fff':
      return u'<img class="char" src="/headline/' + quote(char.encode('utf-8')) + '">'
    else:
      return char
  return "".join(map(replace, code))

print zh_image_filter(u'喵哈哈test哈哈')
