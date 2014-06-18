#!/usr/bin/env python

# Photo format generating script, to be executed separate from web server

from __future__ import print_function
import sys
from dheeranet.views import photos
from subprocess import call, check_output

# get watermark files
photos.album_get_photo('__watermark__', 'light.png', '/tmp/small-light.png', pic_format=photos.PHOTOS_FORMAT_SMALL)
photos.album_get_photo('__watermark__', 'dark.png', '/tmp/small-dark.png', pic_format=photos.PHOTOS_FORMAT_SMALL)
photos.album_get_photo('__watermark__', 'contrast.png', '/tmp/small-contrast.png', pic_format=photos.PHOTOS_FORMAT_SMALL)
photos.album_get_photo('__watermark__', 'light.png', '/tmp/large-light.png', pic_format=photos.PHOTOS_FORMAT_LARGE)
photos.album_get_photo('__watermark__', 'dark.png', '/tmp/large-dark.png', pic_format=photos.PHOTOS_FORMAT_LARGE)
photos.album_get_photo('__watermark__', 'contrast.png', '/tmp/large-contrast.png', pic_format=photos.PHOTOS_FORMAT_LARGE)

album = 'events/20140614dragonboat'

print("listing album {0} ... ".format(album), end='')
sys.stdout.flush()

filenames_original = photos.album_get_filenames(album, pic_format=photos.PHOTOS_FORMAT_ORIGINAL)
filenames_small    = photos.album_get_filenames(album, pic_format=photos.PHOTOS_FORMAT_SMALL)
filenames_large    = photos.album_get_filenames(album, pic_format=photos.PHOTOS_FORMAT_LARGE)
filenames_thumb    = photos.album_get_filenames(album, pic_format=photos.PHOTOS_FORMAT_THUMB)

print('done')
sys.stdout.flush()

for filename in filenames_original:

  if(filename.endswith('.jpg')):

    if not filename in filenames_small:
      print("  creating small for {0} ".format(filename), end='')
      sys.stdout.flush()

      # get image

      photos.album_get_photo(album, filename, '/tmp/foo_original.jpg')

      # scale it
      print('.', end='')
      sys.stdout.flush()

      call(['nice', 'convert',
           '-scale', str(photos.PHOTOS_SMALL_WIDTH*3/2),
           '-sharpen', '0x1',
           '/tmp/foo_original.jpg', '/tmp/foo.bmp'])

      print('.', end='')
      call(['nice', 'convert',
           '-strip',
           '-scale', str(photos.PHOTOS_SMALL_WIDTH),
           '/tmp/foo.bmp', '/tmp/foo.bmp'])

      # get mean and std of region to be watermarked

      print('.', end='')
      sys.stdout.flush()

      (mean, std) = map(float, check_output(['nice', 'identify',
           '-crop', '300x100+0+0',
           '-format', '%[mean] %[standard-deviation]',
           '/tmp/foo.bmp']).strip().split(' '))

      if std>8000:
        watermark_file = '/tmp/small-contrast.png'
      elif mean>32768:
        watermark_file = '/tmp/small-light.png'
      else:
        watermark_file = '/tmp/small-dark.png'

      # composite watermark

      print('.', end='')
      sys.stdout.flush()

      call(['nice', 'composite',
           '-gravity', 'SouthWest',
           '-quality', '94',
           '-compose', 'over', watermark_file,
           '/tmp/foo.bmp', '/tmp/foo_scaled.jpg'])

      print('.', end='')
      sys.stdout.flush()

      call(['exiftool',
           '-q',
           '-overwrite_original',
           '-Author=\"%s\"'.format(photos.PHOTOS_EXIF_AUTHOR),
           '/tmp/foo_scaled.jpg'])

      # put image

      print('.', end='')
      sys.stdout.flush()

      photos.album_put_photo(album, filename, '/tmp/foo_scaled.jpg', pic_format=photos.PHOTOS_FORMAT_SMALL)

      print(' done')
      sys.stdout.flush()

    if not filename in filenames_large:
      print("  creating large for {0} ".format(filename), end='')
      sys.stdout.flush()

      # get image

      photos.album_get_photo(album, filename, '/tmp/foo_original.jpg')

      # scale it

      print('.', end='')
      sys.stdout.flush()

      call(['nice', 'convert',
           '-scale', str(photos.PHOTOS_LARGE_WIDTH*3/2),
           '-sharpen', '0x1',
           '/tmp/foo_original.jpg', '/tmp/foo.bmp'])

      print('.', end='')
      sys.stdout.flush()

      call(['nice', 'convert',
           '-strip',
           '-scale', str(photos.PHOTOS_LARGE_WIDTH),
           '/tmp/foo.bmp', '/tmp/foo.bmp'])

      # get mean and std of region to be watermarked

      print('.', end='')
      sys.stdout.flush()

      (mean, std) = map(float, check_output(['nice', 'identify',
           '-crop', '300x100+0+0',
           '-format', '%[mean] %[standard-deviation]',
           '/tmp/foo.bmp']).strip().split(' '))

      if std>8000:
        watermark_file = '/tmp/large-contrast.png'
      elif mean>32768:
        watermark_file = '/tmp/large-light.png'
      else:
        watermark_file = '/tmp/large-dark.png'

      # composite watermark

      print('.', end='')
      sys.stdout.flush()

      call(['nice', 'composite',
           '-gravity', 'SouthWest',
           '-quality', '94',
           '-compose', 'over', watermark_file,
           '/tmp/foo.bmp', '/tmp/foo_scaled.jpg'])

      print('.', end='')
      sys.stdout.flush()

      call(['exiftool',
           '-q',
           '-overwrite_original',
           '-Author=\"%s\"'.format(photos.PHOTOS_EXIF_AUTHOR),
           '/tmp/foo_scaled.jpg'])

      # put image
      print('.', end='')
      sys.stdout.flush()

      photos.album_put_photo(album, filename, '/tmp/foo_scaled.jpg', pic_format=photos.PHOTOS_FORMAT_LARGE)

      print(' done')
      sys.stdout.flush()

    if not filename in filenames_thumb:
      print("creating thumb for {0}".format(filename))

