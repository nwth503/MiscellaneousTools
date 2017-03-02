# -*- coding: utf-8 -*-

import sys
import os
import glob
import string

from PIL import Image


_, parentpath, ignorefile = sys.argv
dirlist = os.listdir(parentpath)
for f_ignore in ignorefile.split(','):
    try:
        dirlist.remove(f_ignore)
    except:
        pass
for dirname in dirlist:
    os.chdir(parentpath + dirname + '/')
    files = glob.glob(u'*.png')
    if files:
        for f_name in files:
            try:
                original = Image.open(f_name).convert('RGBA')
            except Exception as e:
                print('ERROR> open')
                print(e)
            try:
                alphamask = original.split()[3]
            except Exception as e:
                print('ERROR> split')
                print(e)
            try:
                bgwhite = Image.new('RGB', original.size, (255,255,255))
            except Exception as e:
                print('ERROR> bg new')
                print(e)
            try:
                bgwhite.paste(original, None, alphamask)
            except Exception as e:
                print('ERROR> paste')
                print(e)
            try:
                bgwhite.save(f_name, quality=100)
            except Exception as e:
                print('ERROR> save')
                print(e)
