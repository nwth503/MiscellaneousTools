# -*- coding: utf-8 -*-

import sys
import os.path
import codecs
import datetime
from PIL import Image, ImageDraw, ImageFont


def c_type_normalize(orig):
    normal = orig.replace(
            'e','').replace('2c','c').replace('3','').replace('n','')
    return normal


def setframe(f_name):
    imgpath = 'resources/frame/' + f_name + '.png'
    return Image.open(imgpath).convert('RGBA')


def seticon(f_name):
    imgpath = 'resources/ic-st/ic-' + f_name + '.png'
    return Image.open(imgpath).convert('RGBA')


cost_dict = {
    '1':u'①', '2':u'②', '3':u'③', '4':u'④', '5':u'⑤',
    '6':u'⑥', '7':u'⑦', '8':u'⑧', '9':u'⑨', '10':u'⑩',
    '11':u'⑪', '12':u'⑫', '13':u'⑬', '14':u'⑭', '15':u'⑮',
    '17':u'⑰', '20':u'⑳', '25':u'㉕', '71':u'(71)', u'∞':u'(∞)'
    }
def setcost(cost):
    return cost_dict[cost]


color_dict = {
    'r':(255, 51, 51), 'f':(255, 51, 51),
    'g':(102, 255, 102), 'n':(102, 255, 102),
    'b':(0, 255, 255), 'u':(0, 255, 255),
    'k':(204, 102, 255), 'd':(204, 102, 255),
    'w':(255, 255, 0), 'y':(255, 255, 0), 'l':(255, 255, 0),
    'z':(250, 250, 250)
    }
def setcolor(color):
    return color_dict[color]


pos_dict_index = ('c_name', 'c_text', 'icon')
pos_dict = (
    {   # position of c_name
        'c':(10,5), 'dc':(10,5), 'g':(10,5),
        'ec':(20,5), 'eg':(20,5),
        's':(35,5), 'ps':(35,5),
        'ca':(15,8),
        'd2':(30,5)
    },
    {   # position of c_text
        'c':(0,35), 'dc':(0,35), 'g':(0,35), 's':(0,35), 'ps':(0,35),
        'd2':(0,35),
        'ca':(0,32)
    }
    )
def settextpos(x, y, c_type, mode):
    pos_index = pos_dict_index.index(mode)
    c_type = c_type_normalize(c_type)
    pos_correction = pos_dict[pos_index][c_type]
    x += pos_correction[0]
    y += pos_correction[1]
    return (x, y)


def textreform(c_text):
    splitted = c_text.upper().split(' ')

    iconset = ('ST', 'SB', 'B', 'UB', 'DS')
    icons = sorted(set(iconset).intersection(set(splitted)), key=iconset.index)
    splitted = sorted(set(splitted).difference(set(icons)), key=splitted.index)

    frameset = ('SV', 'WS', 'EX')
    frames = sorted(
                set(frameset).intersection(set(splitted)), key=frameset.index)
    splitted = sorted(
                set(splitted).difference(set(frames)), key=splitted.index)

    reformed = ' '.join(splitted)
    return reformed, list(icons), list(frames)


def set_correction(power, icons):
    correction = 13*len(power) + 3
    if '+' in power:
        correction += 3
    elif '-' in power:
        correction -= 5
    if icons:
        correction += 2
    return correction


def savenamecheck(savename):
    count = 1
    while os.path.isfile('save/' + savename):
        name, ext = os.path.splitext(savename)
        if count == 1:
            savename = name + '_1' + ext
        else:
            name = name[:-1]
            savename = name + str(count) + ext
        count += 1
    return savename


def mkdir(cwdir):
    if not os.path.isdir(cwdir + '/save'):
        try:
            os.mkdir(cwdir + '/save')
        except Exception as e:
            print('[save]フォルダの作成に失敗しました.手動作成してください.')
    return


def main():
    WHITE = (255,255,255,0)
    BLACK = (0,0,0,0)
    C_WIDTH = 221   # カード横幅
    C_HEIGHT = 74   # カード縦幅
    MARGIN = 50     # 印刷余白
    INTERVAL = 3    # カード毎の配置間隔
    last_info = ['', '', '', '', '']  # 最後の読み取り結果を記憶

    fname = sys.argv[1]
    # D&Dの場合はexeのパスが入るのでカレントディレクトリを移動する
    cwdir = sys.argv[0].replace('ichimai.exe','')
    if cwdir:
        os.chdir(cwdir)
    else:
        cwdir = os.getcwd()

    # csv読み込み
    with codecs.open(fname, 'r', 'utf_8_sig') as f_list:
        lines = f_list.readlines()

    # 一枚プロキシ作成(カードを1枚ずつ生成して貼り付けていく)
    ichimai_bg = Image.new('RGB', (1000,1400), WHITE)
    for number, line in enumerate(lines):
        card_info = line.rstrip().split(',')
        # 最後に読み取ったカード情報の更新
        for i in range(4):
            new_info = card_info[i]
            if new_info:
                last_info[i] = new_info
                if i == 3:
                    # カード名が更新された場合テキストも同時に更新する
                    last_info[i+1] = card_info[i+1]
        cost, colors, c_type, c_name, c_text = last_info

        # 枠の分割彩色
        c_bg = Image.new('RGBA', (C_WIDTH,C_HEIGHT), WHITE)
        color_num = len(colors)
        for n, i in enumerate(range(color_num)):
            color = setcolor(colors[i])
            width = int(C_WIDTH/color_num) + 1
            rectangle = Image.new('RGBA', (width,C_HEIGHT), color)
            c_bg.paste(rectangle, (width*i,0))

        # 枠の貼り付け
        mask = setframe(c_type_normalize(c_type))
        x = (C_WIDTH + INTERVAL)*(number % 4) + MARGIN
        y = (C_HEIGHT + INTERVAL)*int(number / 4) + MARGIN
        card_pos = (x, y)
        ichimai_bg.paste(c_bg, card_pos, mask.split()[0])
        # 進化アイコンを重ねる
        if c_type.startswith('e'):
            evo_frame = setframe(c_type)
            alphamask = evo_frame.split()[3]
            ichimai_bg.paste(evo_frame, card_pos, alphamask)

        # 文字入れ
        draw = ImageDraw.Draw(ichimai_bg)
        x, y = settextpos(x, y, c_type, 'c_name')
        # コスト
        cost_font = ImageFont.truetype('meiryo', 26)
        draw.text((x,y), setcost(cost), font=cost_font, fill=BLACK)
        # カード名
        text_font = ImageFont.truetype('meiryo', 21)
        draw.text((x+27,y+5), c_name, font=text_font, fill=BLACK)
        # テキスト
        x, y = settextpos(x, y, c_type, 'c_text')
        c_text, icons, frames = textreform(c_text)
        # フレームを重ねる場合は位置補正
        if frames and not c_type.startswith('e'):
            x += 10
        # クリーチャーの場合パワー部分を左下に最優先で配置して位置補正
        if c_type.endswith('c'):
            power = c_text.split(' ')[0]
            draw.text((x,y), power, font=text_font, fill=BLACK)
            c_text = c_text.replace(power,'', 1).strip()
            x += set_correction(power, icons)
        # サバイバー / ウェーブストライカーのアイコンは透過フレーム
        for frame in frames:
            try:
                frameimage = setframe(frame.lower())
            except:
                frameimage = setframe('clear')
            alphamask = frameimage.split()[3]
            ichimai_bg.paste(frameimage, card_pos, alphamask)
        # アイコンの埋め込み
        for icon in icons:
            x += 1   # 位置微調整
            # アイコンがなければ代替アイコンを設置
            try:
                iconimage = seticon(icon.lower())
            except:
                iconimage = seticon('no')
            alphamask = iconimage.split()[3]
            ichimai_bg.paste(iconimage, (x, y), alphamask)
            x += 24  # アイコン幅+間隔の分位置補正
        draw.text((x+5,y), c_text, font=text_font, fill=BLACK)
    # 画像の保存
    timestamp = str(datetime.datetime.today().strftime('%Y.%m.%d_%H%M'))
    savename = os.path.basename(fname).split('.')[0] + '_' + timestamp + '.png'
    savename = savenamecheck(savename)
    mkdir(cwdir)
    ichimai_bg.save('save/' + savename)
    print(u'できたよ> ' + savename)
    raw_input()

if __name__ == "__main__":
    print(u'処理中...ちょっと待ってね')
    main()
