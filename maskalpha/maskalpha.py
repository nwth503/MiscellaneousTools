# -*- coding: utf-8 -*-

import sys
import os
import glob
from PIL import Image


desktop = 'C:/Users/' + os.environ.get("USERNAME") + '/Desktop/'


def filename(filepath):
    return os.path.split(filepath)[-1]


def fileext(filepath):
    return os.path.splitext(filepath)[-1]


def errored(e, errmsg):
    print(errmsg)
    print(e)


def makedir(directory):
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            errored(e, "# Directory couldn't create.")


def main():
    _, indirpath, maskimgpath, outdirpath = sys.argv
    makedir(outdirpath)
    os.chdir(indirpath + '/')
    files = glob.glob('*')
    if not files:
        return
    for original in files:
        if os.path.isdir('./' + original):
            continue
        if str(original) == str(filename(maskimgpath)):
            print('# Is mask file.')
            continue
        try:
            img = Image.open(original).convert('RGBA')
        except Exception as e:
            errored(e, '# ERROR> open image: ' + original)
            continue
        try:
            msk = Image.open(maskimgpath).convert('RGBA')
        except Exception as e:
            errored(e, '# ERROR> open mask image: ' + maskimgpath)
            continue
        try:
            bg = Image.new('RGBA', img.size, (0,0,0,0))
        except Exception as e:
            errored(e, '# ERROR> bg new: ' + original)
            continue
        try:
            bg.paste(img, (0,0), msk.split()[0])
        except Exception as e:
            errored(e, '# ERROR> paste with alpha: ' + original)
            continue
        try:
            fname = original.replace(fileext(original),'.png')
        except Exception as e:
            errored(e, '# ERROR> rename file: ' + original)
            continue
        try:
            bg.save(outdirpath + '/0' + fname)
        except Exception as e:
            errored(e, '# ERROR> save file: ' + outdirpath + '/0' + fname)
            continue
    raw_input('# Finished.')
    return


if __name__ == '__main__':
    main()
