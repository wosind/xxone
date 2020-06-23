# -*- encoding: utf-8 -*-
"""
@File    :   xxpublic.py    
@Time    :   2020-06-16 9:54
一些常用的自定义函数
"""

import base64
import time
from ctypes import windll

# from ctypes import *
import win32gui, win32ui, win32con, win32api


def Int2Rgb(IntVar):
    # 10进制颜色值->RGB值
    return [IntVar & 0xff, (IntVar >> 8) & 0xff, (IntVar >> 16) & 0xff]


def Hex2Rgb(HexVar):
    # 16进制颜色值->RGB值
    value = HexVar.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def Rgb2Hex(R, G, B):
    # RGB值->16进制颜色值
    H = hex(R)[2:4] + hex(G << 8)[2:4] + hex(B << 16)[2:4]
    return H.upper()


def Rgb2Int(R, G, B):
    # RGB值->10进制颜色值
    return R + (G << 8) + (B << 16)


def ImgTobase64(target):
    res = ''
    with open(target, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        res = 'data:image/png;base64,' + base64_data.decode()
    return res


def TimeOfNow():
    # 当前时间格式化
    return time.strftime("%H:%M:%S", time.localtime())


def StampOfNow():
    # 当前时间戳
    return int(round(time.time() * 1000))


def window_capture(filename):
    hwnd = 0  # 窗口的编号，0号表示当前活跃窗口
    # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
    hwndDC = win32gui.GetWindowDC(hwnd)
    # 根据窗口的DC获取mfcDC
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    # mfcDC创建可兼容的DC
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建bigmap准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    # 获取监控器信息
    MoniterDev = win32api.EnumDisplayMonitors(None, None)
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]
    # print w,h　　　#图片大小
    # 为bitmap开辟空间
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    # 高度saveDC，将截图保存到saveBitmap中
    saveDC.SelectObject(saveBitMap)
    # 截取从左上角（0，0）长宽为（w，h）的图片
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, filename)


def getcolor(dc, x, y):
    return windll.gdi32.GetPixel(dc, x, y)


if __name__ == '__main__':
    print("TimeOfNow:%s" % TimeOfNow())
    print("StampOfNow:%s" % StampOfNow())
    print("Int2Rgb:%s" % Int2Rgb(9482850))
    print("Rgb2Hex:%s" % Rgb2Hex(98, 178, 144))
    print("Rgb2Int:%s" % Rgb2Int(98, 178, 144))
