from __future__ import absolute_import
from __future__ import print_function

import os
import re

import cv2

from  round2.images_process.arrary_utils import *

# 目前圖片上的主要顏色，依照RGB排列(請注意，OPENCV是BGR)

candlestickRed = [254, 0, 0]
candlestickGreen = [1, 128, 0]

volumnRed = [255, 127, 126]
volumnGreen = [128, 192, 127]

week_lineColor = [68, 165, 220]
month_lineColor = [0, 255, 255]
quarter_lineColor = [255, 0, 255]
semiannual_lineColor = [0, 0, 128]
annualColor = [128, 128, 54]

kdj_kColor = [250, 250, 77]
kdj_dColor = [0, 0, 255]
kdj_jColor = [9, 11, 113]


def load_img(path, grayscale=False, target_size=None):
    '''
    :param path: 圖片路徑
    :param grayscale: 是否為灰階(默認為否)
    :param target_size: 目標圖片大小(默認為圖片原始大小)
    :return:
    '''
    img = Image.open(path)
    if grayscale:
        if img.mode != 'L':
            img = img.convert('L')
    else:
        if img.mode != 'RGB':
            img = img.convert('RGB')
    if target_size:
        hw_tuple = (target_size[1], target_size[0])
        if img.size != hw_tuple:
            img = img.resize(hw_tuple)
    return img


def list_pictures(directory, ext='jpg|jpeg|bmp|png|ppm'):
    return [os.path.join(root, f)
            for root, _, files in os.walk(directory) for f in files
            if re.match(r'([\w]+\.(?:' + ext + '))', f)]


def resize(img: Image, expect_size):
    '''
    :param img:
    :param expect_size:以tuple形式表示大小 例如size=128,128
    :return:保持原本長寬比例且不會被裁切的新的縮放後圖片
    '''
    thumb = img.thumbnail(expect_size)
    return thumb


def blackize(img: Image):
    '''
    將圖片的白色變成黑色，因為白是255不是0，黑色才是
    :param img:
    :return:
    '''
    white = [225, 225, 225]
    black = [0, 0, 0]
    data = np.array(img)
    data[(data >= white).all(axis=-1)] = black
    return Image.fromarray(data, mode='RGB')


def whitize(img: Image):
    '''
    將圖片的黑色變成白色，給人類看的
    :param img:
    :return:
    '''
    white = [255, 255, 255]
    black = [25, 25, 25]
    data = np.array(img)
    data[(data <= black).all(axis=-1)] = white
    return Image.fromarray(data, mode='RGB')


def crop(img: Image, left: int, upper: int, right: int, lower: int):
    return img.crop([left, upper, right, lower])


def equal_color(img: Image, color):
    arr_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    arr_img = cv2.resize(arr_img, (img.size[0] * 10, img.size[1] * 10))
    boundaries = []
    boundaries.append(([max(color[2] - 15, 0), max(color[1] - 15, 0), max(color[0] - 15, 0)],
                       [min(color[2] + 15, 255), min(color[1] + 15, 255), min(color[0] + 15, 255)]))
    for (lower, upper) in boundaries:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(arr_img, lower, upper)
        res = cv2.bitwise_and(arr_img, arr_img, mask=mask)
        res = cv2.resize(res, (img.size[0], img.size[1]))
        cv2_im = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
        output_img = Image.fromarray(cv2_im)

        return output_img


if __name__ == '__main__':
    img = Image.open('0cfd7265e70e45e38d96ae888d27fd9b.jpg')
    bimg = equal_color(img, kdj_kColor)

    bimg.save('kdj_kColor_0cfd7265e70e45e38d96ae888d27fd9b.jpg')
