# -*- coding: utf-8 -*-

import sys
import os
from glob import glob
from PIL import Image, ImageFilter


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
            errored(e, "# ERROR>  Directory couldn't create.")


def alpha_mask(orig_img, mask_img, original_name):
    try:
        bg = Image.new('RGBA', orig_img.size, (0,0,0,0))
    except Exception as e:
        errored(e, '# ERROR> Make bg new: ' + original_name)
        return None
    try:
        bg.paste(orig_img, (0,0), mask_img.split()[0])
    except Exception as e:
        errored(e, '# ERROR> Paste with alpha: ' + original_name)
        return None
    return bg

def alpha(indirpath, maskimgpath, outdirpath, files):
    try:
        mask_img = Image.open(maskimgpath).convert('RGBA')
    except Exception as e:
        errored(e, '# ERROR> Open mask image: ' + maskimgpath)
        return
    for original in files:
        if (os.path.isdir('./' + original) or
                str(original) == str(filename(maskimgpath))):
            continue
        try:
            orig_img = Image.open(original).convert('RGBA')
        except Exception as e:
            errored(e, '# ERROR> Open image: ' + original)
            return None
        try:
            masked_image = alpha_mask(orig_img, mask_img, original)
        except:
            continue
        try:
            fname = original.replace(fileext(original),'.png')
        except Exception as e:
            errored(e, '# ERROR> Rename file: ' + original)
            continue
        try:
            masked_image.save(outdirpath + '/' + fname)
        except Exception as e:
            errored(e, '# ERROR> Save file: ' + outdirpath + '/' + fname)
            continue
    return


def valuecorrect(up, down, left, right):
    threshold = 15
    up = 0 if up > threshold else up
    down = 0 if down > threshold else down
    left = 0 if left > threshold else left
    right = 0 if right > threshold else right
    return up, down, left, right

def determine_resizing(edges):
    up = 0
    down = 0
    left = 0
    right = 0
    for i, row in enumerate(edges):     # 通常
        if list(row).count(255) > len(row)/3 or row[int(len(row)/2)] == 255:
            up = i
            break
    edges.reverse()
    for i, row in enumerate(edges):     # 上下反転
        if list(row).count(255) > len(row)/3 or row[int(len(row)/2)] == 255:
            down = i
            break
    edge_t = list(map(list, zip(*edges)))
    for i, row in enumerate(edge_t):    # 転置行列
        if list(row).count(255) > len(row)/3 or row[int(len(row)/2)] == 255:
            left = i
            break
    edge_t.reverse()
    for i, row in enumerate(edge_t):    # 転置+上下反転
        if list(row).count(255) > len(row)/3 or row[int(len(row)/2)] == 255:
            right = i
            break
    return valuecorrect(up, down, left, right)


def dot_removal(bin_image_array):
    ret_array = [
        [
            0 if (pix == 255 and (sum(bin_image_array[r-1][c-1:c+2]) == 0 and
                                sum(bin_image_array[r][c-1:c+2]) == 255 and
                                sum(bin_image_array[r+1][c-1:c+2]) == 0))
            else bin_image_array[r][c]
            for c, pix in enumerate(row)
        ]
        for r, row in enumerate(bin_image_array)
    ]
    return ret_array


def asarray(image):
    # list を 要素数 n ずつの sub list に分割して、画像を二次元配列へ変換
    width, _ = image.size
    return list(zip(*[iter(list(image.getdata()))]*width))


def trim(indirpath, maskimgpath, outdirpath, files):
    try:
        mask_img = Image.open(maskimgpath).convert('RGBA')
    except Exception as e:
        errored(e, '# ERROR> Open mask image: ' + maskimgpath)
        return
    for original in files:
        if os.path.isdir('./' + original):
            continue
        if str(original) == str(filename(maskimgpath)):
            print('# mask file.')
            continue
        try:
            orig_img = Image.open(original).convert('RGBA')
            gray_img = Image.open(original).convert('L')
            width, hight = orig_img.size
        except Exception as e:
            errored(e, '# ERROR> Open image: ' + original)
            continue
        try:
            padding = Image.new('RGBA', (width+6,hight+6), (255,255,255,255))
            padding.paste(gray_img, (3, 3))
        except Exception as e:
            errored(e, '# ERROR> Padding image: ' + original)
            continue
        try:
            gaussian = padding.filter(ImageFilter.GaussianBlur(radius=0.5))
        except Exception as e:
            errored(e, '# ERROR> Applicate Gaussian blur: ' + original)
            continue
        try:
            edges_bin = gaussian.filter(ImageFilter.FIND_EDGES).convert('L')
        except Exception as e:
            errored(e, '# ERROR> Find edge: ' + original)
            continue
        try:
            bin_npy = edges_bin.point(lambda dot: 255 if dot > 100 else 0)
        except Exception as e:
            errored(e, '# ERROR> Binarization: ' + original)
            continue
        try:
            dot_removed = dot_removal(asarray(bin_npy))
        except Exception as e:
            errored(e, '# ERROR> Remove dots: ' + original)
            continue
        try:
            edges = [raw[3:-3] for raw in dot_removed[3:-3]]
        except Exception as e:
            errored(e, '# ERROR> Delete redundant portion: ' + original)
            continue
        try:
            up, down, left, right = determine_resizing(edges)
        except Exception as e:
            errored(e, '# ERROR> Determine the width of resizing: ' + original)
            continue
        try:
            trim = orig_img.crop((left+3, up+3, width-right-3, hight-down-3))
        except Exception as e:
            errored(e, '# ERROR> Trimming image: ' + original)
            continue
        try:
            save_width, save_hight = mask_img.size
            if width > hight:
                save_width, save_hight = save_hight, save_width
            res = trim.resize((save_width, save_hight), resample=Image.HAMMING)
        except Exception as e:
            errored(e, '# ERROR> Resizing image: ' + original)
            continue
        try:
            fname = original.replace(fileext(original),'.png')
        except Exception as e:
            errored(e, '# ERROR> Rename file: ' + original)
            continue
        masked_image = alpha_mask(res, mask_img, original)
        try:
            masked_image.save(outdirpath + '/' + fname)
        except Exception as e:
            errored(e, '# ERROR> Save file: ' + outdirpath + '/' + fname)
            continue
    return


def main():
    _, indirpath, maskimgpath, outdirpath, mode = sys.argv
    makedir(outdirpath)
    os.chdir(indirpath + '/')
    files = glob('*')
    if not files:
        return
    elif mode == 'trim':
        trim(indirpath, maskimgpath, outdirpath, files)
    elif mode == 'mask':
        alpha(indirpath, maskimgpath, outdirpath, files)
    raw_input('# Finished.')
    return

if __name__ == '__main__':
    main()
