import re

# avoid recompiling every time slugify() is called
_slugify_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
  """Generates a URL-friendly slug."""
  result = []
  for word in _slugify_punct_re.split(text.lower()):
    if word:
      result.append(word)
  return unicode(delim.join(result))
