from flask import Flask,request
from werkzeug.contrib.cache import FileSystemCache
import marshal

CACHE_TIMEOUT = 3600
cache = FileSystemCache('dheeranet/cache')

def get_id(f, args, kwargs, mark=object()):
    l = [id(f)]
    for arg in args:
        l.append(id(arg))
    l.append(id(mark))
    for k, v in kwargs:
        l.append(k)
        l.append(id(v))
    return marshal.dumps(tuple(l))

class cached(object):
  def __init__(self, timeout=None):
    self.timeout = timeout or CACHE_TIMEOUT
  def __call__(self, f):
    def decorator(*args, **kwargs):
      key = get_id(f,args,kwargs)
      response = cache.get(key)
      if response is None:
        response = f(*args, **kwargs)
        cache.set(key, response, self.timeout)
      return response
    return decorator
