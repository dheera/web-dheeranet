from flask import Flask,request
from werkzeug.contrib.cache import NullCache, MemcachedCache
import marshal, hashlib
from random import randrange

CACHE_TIMEOUT = 3600
cache = MemcachedCache(['127.0.0.1:11211'])

class cached(object):
  def __init__(self, timeout=None):
    self.timeout = timeout or CACHE_TIMEOUT
  def __call__(self, f):
    def decorator(*args, **kwargs):
      key = 'python_' + marshal.dumps((id(f), args, kwargs)).encode('hex')
      response = cache.get(key)
      if response is None:
        response = f(*args, **kwargs)
        cache.set(key, response, self.timeout)
      return response
    return decorator

def s3_list_cached(s3_bucket, s3_prefix, s3_delimiter, timeout=None, force_recache=False):
  cache_key = 's3_' + marshal.dumps(('list', s3_bucket.name, s3_prefix, s3_delimiter)).encode('hex')
  response = cache.get(cache_key)
  if force_recache or not response:
    response = s3_bucket.list(s3_prefix, s3_delimiter)
    response = map(lambda(k): k.name.encode('utf-8'), response)
    cache.set(cache_key, response,
      timeout or randrange(CACHE_TIMEOUT-CACHE_TIMEOUT/10, CACHE_TIMEOUT + CACHE_TIMEOUT/10))
  return response

def s3_get_cached(s3_bucket, s3_key_name, timeout=None, force_recache=False):
  cache_key = 's3_' + marshal.dumps(('get', s3_bucket.name, s3_key_name)).encode('hex')
  response = cache.get(cache_key)
  if force_recache or not response:
    s3_key = s3_bucket.get_key(s3_key_name)
    if s3_key:
      response = s3_key.get_contents_as_string().decode('utf-8')
    else:
      response = None
    cache.set(cache_key, response,
      timeout or randrange(CACHE_TIMEOUT-CACHE_TIMEOUT/10, CACHE_TIMEOUT + CACHE_TIMEOUT/10))
  return response

