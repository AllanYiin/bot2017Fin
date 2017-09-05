import random
import math
import pandas as pd
import matplotlib.dates as mdates
import datetime
import os
import codecs
import shutil
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc,volume_overlay
import uuid

def kplot(df:pd.DataFrame, picturePath:str):
    """根据给的120day的交易日数据画出K线图
    :param df: 传进的DataFrame是120天的交易日日数据
    :param picturePath: 图片保存路径
    """
    df['ii'] = range(len(df))
    ohlc = df['ii'].map(lambda x: tuple(df.iloc[x][['时间', '开盘价(元)', '最高价(元)', '最低价(元)', '收盘价(元)']])).tolist()

    # 生成了120个(i,time,open,high,low,close)的tuple 这里注意这里处理了nan
    weekday_ohlc = [tuple([i] + list([0 if str(x) == 'nan' else float(x) for x in item[1:]])) for i, item in enumerate(ohlc)]
    week_line = [0 if str(x) == 'nan' else float(x) for x in df['周線'].tolist()]  # 一列的list
    month_line = [0 if str(x) == 'nan' else float(x) for x in df['月線'].tolist()]
    quarter_line = [0 if str(x) == 'nan' else float(x) for x in df['季線'].tolist()]
    half_line = [0 if str(x) == 'nan' else float(x) for x in df['半年線'].tolist()]
    year_line = [0 if str(x) == 'nan' else float(x) for x in df['年線'].tolist()]
    open = [0 if str(x) == 'nan' else float(x) for x in df['开盘价(元)'].tolist()]
    close = [0 if str(x) == 'nan' else float(x) for x in df['收盘价(元)'].tolist()]
    volume = [0 if str(x) == 'nan' else float(x) for x in df['成交量(股)'].tolist()]
    kdj_k=[0 if str(x) == 'nan' else float(x) for x in df['KDJ-K'].tolist()]
    kdj_d=[0 if str(x) == 'nan' else float(x) for x in df['KDJ-D'].tolist()]
    kdj_j=[0 if str(x) == 'nan' else float(x) for x in df['KDJ-J'].tolist()]


    fig = plt.figure(figsize=(18, 10))  # 设置形状的宽度和高度
    p1 = fig.add_axes([0, 0.6, 1, 0.6])
    p1.axes.get_xaxis().set_visible(False)
    plt.xlim(0, len(weekday_ohlc) - 1)  # 设置一下x轴的范围
    candlestick_ohlc(p1, weekday_ohlc, width=0.6, colorup='r', colordown='g')

    # 年线
    plt.plot(week_line, linewidth=1.5, color='orange')
    plt.plot(month_line, linewidth=1.5, color='cyan')
    plt.plot(quarter_line, linewidth=1.5, color='magenta')
    plt.plot(half_line, linewidth=1.5, color='navy')
    plt.plot(year_line, linewidth=1.5, color='olive')

    p2 = fig.add_axes([0, 0.4, 1, 0.2])
    p2.axes.get_xaxis().set_visible(False)
    plt.xlim(0, len(weekday_ohlc) - 1)  # 再次设置一下x轴的范围
    vc = volume_overlay(p2, open, close, volume, colorup='g', alpha=0.5, width=1)  # 成交量

    p3 = fig.add_axes([0, 0.2, 1, 0.2])
    p3.axes.get_xaxis().set_visible(False)  # 关闭x轴
    plt.xlim(0, len(weekday_ohlc) - 1)  # 再次设置一下x轴的范围
    plt.plot(kdj_k, linewidth=2, color='yellow')
    plt.plot(kdj_d, linewidth=2, color='blue')
    plt.plot(kdj_j, linewidth=2, color='purple')

    plt.savefig(picturePath, bbox_inches='tight', pad_inches=0)#保存图片

    plt.close()


def handler_all_price_csv(txtPath:str, pictureRoot:str):
    """处理csv内部为逗号格式的文件,生成k线图和对应label
    :param txtPath: 数据txt目录
    :param pictureRoot: 图片保存目录
    """
    if not os.path.exists(pictureRoot):
        os.mkdir(pictureRoot)
    DATA = pd.read_csv(txtPath, low_memory=False)
    # 用matplotlib.dates将time格式转换为时间戳
    DATA['时间'] = DATA['时间'].map(lambda x: mdates.date2num(datetime.datetime.strptime(x, '%Y/%m/%d')) if re.match(r"[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}", str(x)) else x)
    # 把股票的简称全部去重后找出来
    stocknames = list(set(DATA['简称'].tolist()))

    n=0
    while n<11000:
        stockname=random.choice(stocknames)
        data= DATA[DATA['简称'] == stockname ]  # 得到这支股票的所有数据记录
        length=len(data)#这支股票的数据记录数
        if length<360: continue#没有超过120+240不画了
        idx=random.randint(360,length-1)
        df=data.iloc[idx-120:idx]#得到第i个120条记录 #print(len(df))
        kplot(df,os.path.join(pictureRoot,"%s-%s" % (stockname,str(idx).zfill(6))))
        n+=1



if __name__=='__main__':
   # redraw_kplot('market_1.txt')
    txtPath='test.txt'
    pictureRoot="samples/new_index1"

    handler_all_price_csv(txtPath, pictureRoot)
