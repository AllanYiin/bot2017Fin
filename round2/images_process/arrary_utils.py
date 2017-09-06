import numpy as np
from PIL import Image


def img2array(img: Image):
    array = np.array(img, dtype=np.float32)
    return np.ascontiguousarray(array)


def array2img(arr: np.ndarray):
    sanitized_img = np.maximum(0, np.minimum(255, arr))
    img = Image.fromarray(np.uint8(sanitized_img))
    return img


# 請選手自行決定排列格式，一般深度學習分析工具與英偉達CUDA是CHW格式，Tensorflow則是WHC
def WHC2CHW(whcarr: np.ndarray):
    '''
    :param whcarr: 依照WHC (寬-高-通道(RGB))排列的向量
    :return: hwarr: 依照WHC (通道(RGB)-高-寬)排列的向量
    '''
    return np.transpose(whcarr, (2, 0, 1))


def CHW2WHC(chwarr: np.ndarray):
    '''
    :param chwarr: 依照WHC (通道(RGB)-高-寬)排列的向量
    :return: whcarr: 依照WHC (寬-高-通道(RGB))排列的向量
    '''
    return np.transpose(chwarr, (1, 2, 0))


def RGB2BGR(rgb: np.ndarray):
    return rgb[..., ::-1]


def BGR2RGB(bgr: np.ndarray):
    return bgr[..., ::-1]
