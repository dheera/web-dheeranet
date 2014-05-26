from flask import Flask,request
from werkzeug.contrib.cache import FileSystemCache

CACHE_TIMEOUT = 300
cache = FileSystemCache('dheeranet/cache')

class cached(object):
  def __init__(self, timeout=None):
    self.timeout = timeout or CACHE_TIMEOUT
  def __call__(self, f):
    def decorator(*args, **kwargs):
      response = cache.get(request.path)
      if response is None:
        response = f(*args, **kwargs)
        cache.set(request.path, response, self.timeout)
      return response
    return decorator
