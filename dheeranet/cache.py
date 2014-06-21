from flask import Flask,request
from werkzeug.contrib.cache import FileSystemCache, NullCache, MemcachedCache
from dheeranet import app
import marshal

CACHE_TIMEOUT = 3600
if app.debug:
  cache = NullCache()
else:
  cache = MemcachedCache(['127.0.0.1:11211'])

class cached(object):
  def __init__(self, timeout=None):
    self.timeout = timeout or CACHE_TIMEOUT
  def __call__(self, f):
    def decorator(*args, **kwargs):
      key = marshal.dumps((id(f),args,kwargs)).encode('hex')
      response = cache.get(key)
      if response is None:
        response = f(*args, **kwargs)
        cache.set(key, response, self.timeout)
      return response
    return decorator
