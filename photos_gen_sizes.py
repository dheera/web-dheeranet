#!/usr/bin/env python

# Photo format generating script, to be executed separate from web server

from __future__ import print_function
import sys, os, shutil, signal
from dheeranet.views import photos
from subprocess import call, check_output
from tempfile import mkdtemp
from time import sleep

tempdir = mkdtemp();
tempdir_watermark = mkdtemp();

def signal_handler(signal, frame):
  shutil.rmtree(tempdir)
  shutil.rmtree(tempdir_watermark)
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# get watermark files
photos.album_get_photo('__watermark__', 'light.png', tempdir_watermark + '/small-light.png', pic_format=photos.PHOTOS_FORMAT_SMALL)
photos.album_get_photo('__watermark__', 'dark.png', tempdir_watermark + '/small-dark.png', pic_format=photos.PHOTOS_FORMAT_SMALL)
photos.album_get_photo('__watermark__', 'contrast.png', tempdir_watermark + '/small-contrast.png', pic_format=photos.PHOTOS_FORMAT_SMALL)
photos.album_get_photo('__watermark__', 'light.png', tempdir_watermark + '/large-light.png', pic_format=photos.PHOTOS_FORMAT_LARGE)
photos.album_get_photo('__watermark__', 'dark.png', tempdir_watermark + '/large-dark.png', pic_format=photos.PHOTOS_FORMAT_LARGE)
photos.album_get_photo('__watermark__', 'contrast.png', tempdir_watermark + '/large-contrast.png', pic_format=photos.PHOTOS_FORMAT_LARGE)

albums = photos.list_albums('places', force_recache=True) + \
         photos.list_albums('journeys', force_recache=True) + \
         photos.list_albums('events', force_recache=True) + \
         photos.list_albums('abstract', force_recache=True) + \
         photos.list_albums('things', force_recache=True)

process_count = 0

for album in albums:

  print("listing album {0} ... ".format(album), end='')
  sys.stdout.flush()

  filenames_original = photos.album_list_filenames(album,
                         pic_format=photos.PHOTOS_FORMAT_ORIGINAL, force_recache=True)
  filenames_small    = photos.album_list_filenames(album,
                         pic_format=photos.PHOTOS_FORMAT_SMALL, force_recache=True)
  filenames_large    = photos.album_list_filenames(album,
                         pic_format=photos.PHOTOS_FORMAT_LARGE, force_recache=True)
  filenames_thumb    = photos.album_list_filenames(album,
                         pic_format=photos.PHOTOS_FORMAT_THUMB, force_recache=True)
  filenames_thumb2   = photos.album_list_filenames(album,
                         pic_format=photos.PHOTOS_FORMAT_THUMB2, force_recache=True)

  print('done')
  sys.stdout.flush()

  for filename in filenames_original:

  
    if(filename.endswith('.jpg')):
  
      if not filename in filenames_small:
        process_count += 1
        if process_count % 32 == 0:
          sleep(5)

        print("  creating small for {0} ".format(filename), end='')
        sys.stdout.flush()
  
        # get image
  
        photos.album_get_photo(album, filename, tempdir + '/' + filename)
  
        # scale it
        print('.', end='')
        sys.stdout.flush()
  
        call(['nice', 'convert',
             '-scale', str(photos.PHOTOS_SMALL_WIDTH*3/2),
             '-sharpen', '0x1',
             tempdir + '/' + filename,
             tempdir + '/' + filename + '.bmp'])
  
        print('.', end='')
        call(['nice', 'convert',
             '-strip',
             '-scale', str(photos.PHOTOS_SMALL_WIDTH),
             tempdir + '/' + filename + '.bmp',
             tempdir + '/' + filename + '.bmp'])
  
        # get mean and std of region to be watermarked
  
        print('.', end='')
        sys.stdout.flush()
  
        call(['nice', 'convert',
             '-crop', '150x70+0+0',
             '-gravity', 'SouthWest',
             tempdir + '/' + filename + '.bmp',
             tempdir + '/' + filename + '.sub.bmp'])
  
        (mean, std) = map(float, check_output(['nice', 'identify',
             '-format', '%[mean] %[standard-deviation]',
             tempdir + '/' + filename + '.sub.bmp']).strip().split(' '))
  
        if std>8000:
          watermark_file = tempdir_watermark + '/small-contrast.png'
        elif mean>32768:
          watermark_file = tempdir_watermark + '/small-dark.png'
        else:
          watermark_file = tempdir_watermark + '/small-light.png'
  
        # composite watermark
  
        print('.', end='')
        sys.stdout.flush()
  
        call(['nice', 'composite',
             '-gravity', 'SouthWest',
             '-quality', '94',
             '-compose', 'over', watermark_file,
             tempdir + '/' + filename + '.bmp',
             tempdir + '/' + filename + '.small.jpg'])
  
        print('.', end='')
        sys.stdout.flush()
  
        call(['exiftool',
             '-q',
             '-overwrite_original',
             '-Author=\"%s\"'.format(photos.PHOTOS_EXIF_AUTHOR),
             tempdir + '/' + filename + '.small.jpg'])
  
        # put image
  
        print('.', end='')
        sys.stdout.flush()
  
        photos.album_put_photo(album,
          filename,
          tempdir + '/' + filename + '.small.jpg',
          pic_format=photos.PHOTOS_FORMAT_SMALL)
  
        print(' done')
        sys.stdout.flush()
  
      if not filename in filenames_large:
        process_count += 1
        if process_count % 32 == 0:
          sleep(5)

        print("  creating large for {0} ".format(filename), end='')
        sys.stdout.flush()
  
        # get image
  
        if not os.path.isfile(tempdir + '/' + filename):
          photos.album_get_photo(album, filename, tempdir + '/' + filename)
  
        # scale it
        print('.', end='')
        sys.stdout.flush()
  
        call(['nice', 'convert',
             '-scale', str(photos.PHOTOS_LARGE_WIDTH*3/2),
             '-sharpen', '0x1',
             tempdir + '/' + filename,
             tempdir + '/' + filename + '.bmp'])
  
        print('.', end='')
        call(['nice', 'convert',
             '-strip',
             '-scale', str(photos.PHOTOS_LARGE_WIDTH),
             tempdir + '/' + filename + '.bmp',
             tempdir + '/' + filename + '.bmp'])
  
        # get mean and std of region to be watermarked
  
        print('.', end='')
        sys.stdout.flush()

        call(['nice', 'convert',
             '-crop', '300x140+0+0',
             '-gravity', 'SouthWest',
             tempdir + '/' + filename + '.bmp',
             tempdir + '/' + filename + '.sub.bmp'])
  
        (mean, std) = map(float, check_output(['nice', 'identify',
             '-format', '%[mean] %[standard-deviation]',
             tempdir + '/' + filename + '.sub.bmp']).strip().split(' '))
  
        if std>8000:
          watermark_file = tempdir_watermark + '/large-contrast.png'
        elif mean>32768:
          watermark_file = tempdir_watermark + '/large-dark.png'
        else:
          watermark_file = tempdir_watermark + '/large-light.png'
  
        # composite watermark
  
        print('.', end='')
        sys.stdout.flush()
  
        call(['nice', 'composite',
             '-gravity', 'SouthWest',
             '-quality', '94',
             '-compose', 'over', watermark_file,
             tempdir + '/' + filename + '.bmp',
             tempdir + '/' + filename + '.large.jpg'])
  
        print('.', end='')
        sys.stdout.flush()
  
        call(['exiftool',
             '-q',
             '-overwrite_original',
             '-Author=\"%s\"'.format(photos.PHOTOS_EXIF_AUTHOR),
             tempdir + '/' + filename + '.large.jpg'])
  
        # put image
  
        print('.', end='')
        sys.stdout.flush()
  
        photos.album_put_photo(album,
          filename,
          tempdir + '/' + filename + '.large.jpg',
          pic_format=photos.PHOTOS_FORMAT_LARGE)
  
        print(' done')
        sys.stdout.flush()
  
  
      if not filename in filenames_thumb:
        process_count += 1
        if process_count % 32 == 0:
          sleep(5)

        print("  creating thumb for {0} ".format(filename), end='')
        sys.stdout.flush()
  
        if not os.path.isfile(tempdir + '/' + filename + '.small.jpg'):
          photos.album_get_photo(album, filename, tempdir + '/' + filename + '.small.jpg', photos.PHOTOS_FORMAT_SMALL)
  
        print('.', end='')
        sys.stdout.flush()
  
        call(['convert',
             '-strip',
             tempdir + '/' + filename + '.small.jpg',
             '-thumbnail', '140x140^',
             '-gravity', 'center',
             '-sharpen', '0x0.5',
             '-quality', '80',
             '-extent', '140x140',
             tempdir + '/' + filename + '.thumb.jpg'])
 
        print('.', end='')
        sys.stdout.flush()
  
        photos.album_put_photo(album,
          filename,
          tempdir + '/' + filename + '.thumb.jpg',
          pic_format=photos.PHOTOS_FORMAT_THUMB)
  
        print('.... done')
        sys.stdout.flush()

      if not filename in filenames_thumb2:
        process_count += 1
        if process_count % 32 == 0:
          sleep(5)

        print("  creating thumb2 for {0} ".format(filename), end='')
        sys.stdout.flush()
  
        if not os.path.isfile(tempdir + '/' + filename + '.small.jpg'):
          photos.album_get_photo(album, filename, tempdir + '/' + filename + '.small.jpg', photos.PHOTOS_FORMAT_SMALL)
  
        print('.', end='')
        sys.stdout.flush()
  
        call(['convert',
             '-strip',
             tempdir + '/' + filename + '.small.jpg',
             '-thumbnail', '200x200^',
             '-gravity', 'center',
             '-sharpen', '0x0.5',
             '-quality', '80',
             '-extent', '200x200',
             tempdir + '/' + filename + '.thumb2.jpg'])
 
        print('.', end='')
        sys.stdout.flush()
  
        photos.album_put_photo(album,
          filename,
          tempdir + '/' + filename + '.thumb2.jpg',
          pic_format=photos.PHOTOS_FORMAT_THUMB2)
  
        print('.... done')
        sys.stdout.flush()

  map(os.unlink, [os.path.join(tempdir, f) for f in os.listdir(tempdir)])

shutil.rmtree(tempdir)
shutil.rmtree(tempdir_watermark)
