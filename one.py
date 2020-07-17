# -*- encoding: utf-8 -*-

"""
@File    :   one.py
@Time    :   2020-04-30 16:31
pyinstaller one.py -i app.ico --hidden-import docx --hidden-import pynput --add-data "msg1.wav;." --add-data  "title.ico;." --add-data  "query.png;." --add-data "msg2.wav;." --add-data  "close.gif;."

程序主要功能
A:百度知道问题自动刷新
B:集合日常工作的一些应用工具，
天气查看、翻译、颜色值管理、Base64编码生成
"""

import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import os, sys, time
import requests
import webbrowser
import execjs
import json
import sqlite3
import logging

from time import sleep
from ctypes import windll
from pynput.mouse import Listener
from queue import Queue
from threading import Thread
from tkinter import messagebox
from tkinter import Canvas
from tkinter.filedialog import askopenfilename, asksaveasfilename
from requests.cookies import RequestsCookieJar
from PIL import Image, ImageTk
from playsound import playsound
from xxpublic import *


# from io import StringIO


class Translate():
    # 百度翻译爬取
    def __init__(self):
        self.detect_url = "https://fanyi.baidu.com/langdetect"
        self.trans_url = "https://fanyi.baidu.com/v2transapi"
        self.header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}

        self.jscode = """var i = "320305.131321201"
function n(r, o) {
    for (var t = 0; t < o.length - 2; t += 3) {
        var a = o.charAt(t + 2);
        a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
            a = "+" === o.charAt(t + 1) ? r >>> a : r << a,
            r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
    }
    return r
}
function e(r) {
    var o = r.match(/\uD800-\uDBFF/g);
    if (null === o) {
        var t = r.length;
        t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10))
    } else {
        for (var e = r.split(/\uD800-\uDBFF/), C = 0, h = e.length, f = []; h > C; C++)
            "" !== e[C] && f.push.apply(f, a(e[C].split(""))),
            C !== h - 1 && f.push(o[C]);
        var g = f.length;
        g > 30 && (r = f.slice(0, 10).join("") + f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") + f.slice(-10).join(""))
    }
    var u = void 0
        , l = "" + String.fromCharCode(103) + String.fromCharCode(116) + String.fromCharCode(107);
    u = null !== i ? i : (i = window[l] || "") || "";
    for (var d = u.split('.'), m = Number(d[0]) || 0, s = Number(d[1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) {
        var A = r.charCodeAt(v);
        128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)),
            S[c++] = A >> 18 | 240,
            S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224,
            S[c++] = A >> 6 & 63 | 128),
            S[c++] = 63 & A | 128)
    }
    for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++)
        p += S[b],
            p = n(p, F);
    return p = n(p, D),
        p ^= s,
    0 > p && (p = (2147483647 & p) + 2147483648),
        p %= 1e6,
    p.toString() + "." + (p ^ m)
}"""

    def sendDePost(self, trans_str):
        de_data = {"query": trans_str}
        response = requests.post(self.detect_url, de_data, headers=self.header)
        re = json.loads(response.content.decode(), encoding="utf-8")
        logger.info("sendDePost: ", re)
        return re["lan"]

    def sendTranslatePost(self, trans_str):
        try:
            lan = self.sendDePost(trans_str)
            lan_from = "zh" if lan == "zh" else "en"
            lan_to = "en" if lan == "zh" else "zh"
        except BaseException as e:
            logger.info(e)
            logger.info('翻译失败')
            return False
        try:
            set_sign = self.getSign(trans_str)
        except BaseException as e:
            logger.info(e)
            logger.info('翻译失败')
            return False
        fanyi_data = {"from": lan_from,
                      "to": lan_to,
                      "query": trans_str,
                      "transtype": "translang",
                      "simple_means_flag": "3",
                      "sign": set_sign,
                      "token": "b01862bd6d087dbdb2dd562ecd940435"}
        Cookies = {
            "BAIDUID": "E5BB6C7348B207E45C3486FEEF987D2B:FG=1",
        }

        try:
            response = requests.post(self.trans_url, fanyi_data, headers=self.header, cookies=Cookies)
        except BaseException as e:
            logger.info(e)
            logger.info('翻译失败')
            return False

        data_dict = json.loads(response.content.decode())

        if "trans_result" in data_dict:
            res = data_dict["trans_result"]["data"][0]["dst"]
            return res
        else:
            res = data_dict
            return False

    def getSign(self, trans_str):
        js_compile = execjs.compile(self.jscode)
        res = js_compile.call("e", trans_str)
        return res


class App(tk.Tk):
    # 主应用对象
    def __init__(self):
        super().__init__()

        self.dynamicStr = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂', '▁']
        self.titleStr = 'ONE - Tools In One  '
        self.title(self.titleStr + ''.join(self.dynamicStr))

        # 获取当前工作路径
        if getattr(sys, 'frozen', None):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(__file__)

        # 拼接资源文件的绝对路径
        icofile = os.path.join(basedir, 'title.ico')
        self.configFileName = os.path.join(basedir, 'config.data')
        imageQueryFname = os.path.join(basedir, 'query.png')
        global imageQuery
        imageQuery = tk.PhotoImage(file=imageQueryFname)

        # 读取系统配置
        fname = 'config.data'
        self.configs = {}
        if os.path.exists(self.configFileName):
            try:
                with open(self.configFileName, 'r') as f:
                    content = f.read()
                self.configs = eval(content)
            except BaseException as e:
                logger.info(e)
        else:
            self.configs = {'issave': False, 'qlist': True}
            with open(fname, 'w') as f:
                f.write("{'issave':True,'qlist':True}")

        # 限制窗口最小尺寸
        w = 1024 if self.configs["qlist"] else 480
        self.wm_minsize(w, 600)

        # 窗口标题图标
        self.iconbitmap(icofile)

        # 主窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.onMainClosing)

        # 绑定窗口全局按键按下事件
        self.bind("<Key>", self.onKeyDown)

        # 构造欢迎界面
        self.welcomeF = WelcomeFrame(self)

        # 主界面对象
        self.Mf = None

        # 隐藏主窗口边框
        # self.overrideredirect(True)

        self.after(2000, lambda args=self.welcomeF: self.GoToMain(args))

        self.mainloop()

    def onKeyDown(self, e):
        # F5快捷键
        if e.keycode == 116 and self.Mf:
            global coolDown
            coolDown = 19

    # def protectThread(self):
    #     if stopApp: return
    #     self.dynamicStr.append(self.dynamicStr.pop(0))
    #     self.title(self.titleStr + "".join(self.dynamicStr))
    #     if threading.activeCount() < 3:
    #         global th_tm
    #         th_tm = threading.Thread(target=self.TaskMonitoring, name="TM", daemon=True)
    #         th_tm.start()
    #
    #     self.after(500, self.protectThread)

    def TaskMonitoring(self):
        # 如果主窗口标记已关闭，停止多任务管理
        if stopApp: return
        global coolDown
        if coolDown > 18:
            self.after(1000, self.Mf.updateInfo())
            coolDown = 1
        if coolDown: coolDown += 1
        global th_tm
        self.after(3000, self.TaskMonitoring)

    # 系统设置页面
    # def GotoConfig(self, FromObject):
    #     stopAllThread()
    #     FromObject.destroy()
    #     ConfigFrame(self)

    def GoToMain(self, FromObject):
        FromObject.destroy()
        self.Mf = MainFrame(self)

        # 启动多任务管理线程
        self.after(1000, self.TaskMonitoring)

    def onMainClosing(self, _sysTrayIcon=None):

        # global stopApp
        # stopApp = True
        # if not runing.empty():
        #     res = messagebox.askokcancel('注意', '正在更新列表\n确定要强制关闭程序吗？')
        #     if res:
        #         tk._exit()
        #     else:
        #         return
        # while True:
        #     for th in threading.enumerate():
        #         if type(th) == threading.Timer:
        #             th.cancel()
        #     if len(threading.enumerate()) == 1: break
        self.destroy()


class WelcomeFrame(tk.Frame):
    # 欢迎界面
    def __init__(self, master):
        super().__init__(master)
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self.ft = tkFont.Font(family='微软雅黑', size=10, weight='bold')  # 创建字体
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=300);
        self.rowconfigure(1, weight=1);
        self.rowconfigure(2, weight=1);
        self.rowconfigure(3, weight=300);
        self.columnconfigure(0, weight=1)
        tk.Frame(self).grid(row=0, column=0, sticky=tk.NSEW)
        self.Lable = tk.Label(self, text="ONE", font=("Times New Roman", 48), fg="#00A198")
        self.Lable.grid(row=1, column=0, sticky=tk.NSEW)
        self.Lable = tk.Label(self, text="正在初始化程序...", font=("微软雅黑", 9), fg="#924D26")
        self.Lable.grid(row=2, column=0, sticky=tk.NSEW)
        tk.Frame(self).grid(row=3, column=0, sticky=tk.NSEW)


class MainFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.main = master

        # 百度翻译模块
        self.translater = Translate()

        # 控制台输出信息重定向到内存文件中
        # self.sio = StringIO()
        # sys.stdout = self.sio

        # 构造资源文件路径
        if getattr(sys, 'frozen', None):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(__file__)
        self.wavfile1 = os.path.join(basedir, 'msg1.wav')
        self.wavfile2 = os.path.join(basedir, 'msg2.wav')
        self.cleargif = os.path.join(basedir, 'close.gif')
        self.dataFileName = os.path.join(basedir, 'Qlist.data')
        self.tkimg = ImageTk.PhotoImage(Image.open(self.cleargif))

        # 问题列表
        self.qlist = {}

        # 是否保存列表到本地
        self.isSave = self.main.configs['issave']
        if self.isSave:
            with open(self.dataFileName, 'r') as f:
                content = f.read()
                self.qlist = eval(content)

        # 浏览器初始化，用于打开问题详情窗口页面
        chromePath = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chromePath))
        self.browser = webbrowser.get('chrome')

        # 构造百度cookie
        self.cookie_jar = RequestsCookieJar()
        self.cookie_jar.set("BAIDUID", "1ECEF68B5E6366CEC3C66E2EC5538FF9:FG=1")
        self.cookie_jar.set("BDUSS",
                            "9-NUdFZXRDdnhoRm5pSEVRb1dMSX5oMkJhZ0lqQXI0R2FPdExIR1M5Qk4tNjVlSVFBQUFBJCQAAAAAAAAAAAEAAACk~mItaHkxMzk3NDcxAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAE1uh15NbodeSG")

        # 拉取问题列表接口、请求参数
        self.pushUrl = "https://zhidao.baidu.com/ihome/api/push"
        self.pushPostData = {
            "pn": 1,
            "rn": 50,
            "type": "newRecommend",
            "keyInTag": 1,
            "filter": '',
            "t": 0,
            "tags": "powerbuilder python Python",
            "isMavin": 1,
            "isAll": 0,
            "isExpGroup": 1
        }

        # 消息数
        self.msgcount = 0

        # 过滤后的列表
        self.qfiltered = []

        # 问题ID
        self.selectedQid = ""

        # 状态提示信息
        self.showState = tk.StringVar()

        # 列表各字段样式
        self.head = {"qid": {'inx': 0, 'sort': True},
                     "createTimeOrg": {'inx': 1, 'sort': True},
                     "title": {'inx': 2, 'sort': True},
                     "uname": {'inx': 3, 'sort': True}
                     }

        # 搜索输入框绑定信息
        self.entry_var = tk.StringVar()

        # 监控输入信息的变化，即输入状态
        self.entry_var.trace("w", lambda name, index, mode, arg=self.entry_var: self.onEditChange(arg))

        # 颜色右键弹出菜单
        self.rightMenubar = tk.Menu(self.main, tearoff=False)

        # 初始化主窗口
        self.initMain(master)

    def initMain(self, master):
        # 设置顶级窗体的行列权重，否则子组件的拉伸不会填充整个窗体
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.ft = tkFont.Font(family='微软雅黑', size=10, weight='bold')  # 创建字体
        # self.initMenu(master)  # 为顶级窗体添加菜单项

        # 设置继承类MWindow的grid布局位置，并向四个方向拉伸以填充顶级窗体
        self.grid(row=0, column=0, sticky=tk.NSEW)

        # 设置继承类MWindow的行列权重，保证内建子组件会拉伸填充
        self.rowconfigure(0, weight=1);
        # self.rowconfigure(1, weight=1);
        self.columnconfigure(0, weight=1)

        self.panedwin = ttk.Panedwindow(self, orient=tk.HORIZONTAL)  # 添加水平方向的推拉窗组件
        self.panedwin.grid(row=0, column=0, sticky=tk.NSEW)  # 向四个方向拉伸填满MWindow帧

        # 底部程序说明
        self.lbver = ttk.Label(self, font=self.ft)
        self.lbver["text"] = "One 我的工具箱 V20200618A Code By Xiaox@2020 Tel : 18627472125"
        self.lbver["anchor"] = tk.CENTER
        self.lbver.grid(row=1, column=0, sticky=tk.NSEW)

        # 判断是否加载问题刷新模块
        isload = self.main.configs['qlist']
        if isload:
            self.initQaList()  # 初始化左边列表界面
        self.initDetail()  # 初始化右边明细、控制界面

        # 加载历史列表
        if self.qlist: self.qListFilter()

        # 显示程序说明
        self.showVerInfo()

        # 添加自动更新到任务列表
        global coolDown
        if isload: coolDown = 1

    # def initMenu(self, master):
    #     '''初始化菜单'''
    #     mbar = tk.Menu(master)  # 定义顶级菜单实例
    #     fmenu = tk.Menu(mbar, tearoff=False)  # 在顶级菜单下创建菜单项
    #
    #     mbar.add_cascade(label=' 关于开发者 ', menu=fmenu, )  # 添加子菜单
    #     fmenu.add_command(label=" 开发者信息 ", command=self.onMenuClicked)
    #     # fmenu.add_command(label="保存", command=self.menu_click_event)
    #     # fmenu.add_separator()  # 添加分割线
    #     # fmenu.add_command(label="退出", command=master.quit())
    #
    #     master.config(menu=mbar)  # 将顶级菜单注册到窗体

    def initQaList(self):
        # 左边问题列表区域
        self.frm_left = ttk.Frame(self.panedwin, relief=tk.SUNKEN, padding=0)
        self.frm_left.grid(row=0, column=0, sticky=tk.NSEW);  # 左侧Frame帧拉伸填充
        self.panedwin.add(self.frm_left, weight=4)  # 将左侧Frame帧添加到推拉窗控件，左侧权重1
        self.frm_left.rowconfigure(0, weight=1)  # 左侧问题列表区域行列权重配置
        self.frm_left.rowconfigure(1, weight=200)
        self.frm_left.columnconfigure(0, weight=1)
        self.frm_left_top = ttk.Frame(self.frm_left, padding=(4, 4))  #
        self.frm_left_top.grid(row=0, column=0, sticky=tk.EW, columnspan=2)
        self.frm_left_top.rowconfigure(0, weight=1)  # 左侧顶部按钮、输入框布局
        self.frm_left_top.columnconfigure(0, weight=100)
        self.frm_left_top.columnconfigure(1, minsize=4)
        self.frm_left_top.columnconfigure(2, weight=1)
        self.frm_left_top.columnconfigure(3, minsize=2)
        self.frm_left_top.columnconfigure(4, weight=1)
        self.frm_left_top.columnconfigure(5, minsize=2)
        self.frm_left_top.columnconfigure(6, weight=1)

        self.Entry_query = ttk.Entry(self.frm_left_top, textvariable=self.entry_var)
        self.Entry_query.grid(row=0, column=0, sticky=tk.EW)
        self.Entry_query.bind("<Return>", self.onEditEnter)

        self.canvas = tk.Canvas(self.frm_left_top, width=0, height=22)
        self.canvas.create_image(0, 4, image=self.tkimg, anchor=tk.NW)
        self.canvas.bind("<Button-1>", self.onClearEnter)
        self.canvas.grid(row=0, column=1, sticky=tk.E)

        self.button_query = ttk.Button(self.frm_left_top, image=imageQuery)
        self.button_query["command"] = self.onEditEnter
        self.button_query.grid(row=0, column=2)
        # self.button_query.bind("<Enter>", self.onMouseIn)
        # self.button_query.bind("<Leave>", self.onMouseOut)

        # self.button_update = ttk.Button(self.frm_left_top, text='刷新列表')
        # self.button_update["command"] = lambda: self.onButtonClicked('刷新列表')
        # self.button_update.grid(row=0, column=4)

        # self.rb_issave = ttk.Checkbutton(self.frm_left_top, onvalue=1, offvalue=0)
        # self.rb_issave["variable"] = self.checkbuttonState
        # self.rb_issave["text"] = '保存列表到本地'
        # self.rb_issave["command"] = self.onCheckButtonClicked
        # self.rb_issave.grid(row=0, column=6)

        self.tree_qlist = ttk.Treeview(self.frm_left, selectmode='browse', show="headings")
        self.tree_qlist.grid(row=1, column=0, sticky=tk.NSEW)  # 像4个方向拉伸

        self.allCols = ('qid', 'title', 'isFromWap', 'cid', 'className', 'createTimeOrg',
                        'createTime', 'replyNum', 'score', 'tagName', 'import_id', 'content',
                        'sup', 'modeType', 'modeUid', 'uid', 'imId', 'isNoUserName',
                        'isAnonymous', 'hasZhimaTag', 'hasPic', 'unpushFlag', 'isVideo', 'uname',
                        'contentRich', 'supRich', 'pvNum')

        self.showDetails = ["title", "content", "qid", "pvNum", "uname", "isFromWap", "cid", "score",
                            "className", "replyNum", "tagName", "import_id", "sup",
                            "uid", "imId", "isNoUserName", "isAnonymous", "hasZhimaTag", "hasPic",
                            "unpushFlag", "isVideo", "supRich", "modeType", "modeUid", ]

        self.listBind = (
            {'col': 'createTimeOrg', 'width': 80, 'anchor': 'center', 'stretch': True},
            {'col': 'title', 'width': 280, 'anchor': 'w', 'stretch': False},
            {'col': 'uname', 'width': 100, 'anchor': 'center', 'stretch': False},
        )
        self.tree_qlist["columns"] = [x['col'] for x in self.listBind]  # #定义列
        for x in self.listBind:
            self.tree_qlist.column(x['col'], width=x['width'], anchor=x['anchor'],
                                   stretch=tk.NO if x['stretch'] else tk.YES)  # #设置列
            self.tree_qlist.heading(x['col'], text=x['col'],
                                    command=lambda arg=x['col']: self.onListHeadClicked(arg))  # #设置显示的表头名

        self.tree_qlist.bind("<<TreeviewSelect>>", self.showDetail)
        self.tree_qlist.bind("<Double-Button-1>", self.onListDoubleClicked)

        scr1 = ttk.Scrollbar(self.frm_left, orient=tk.VERTICAL)
        self.tree_qlist.configure(yscrollcommand=scr1.set)
        scr1['command'] = self.tree_qlist.yview
        scr1.grid(row=1, column=1, sticky=tk.NS)

        # 测试数据
        # for i in range(40):
        #     self.tree_qlist.insert("", 0, text='', values=(i, 'title%s' % i, ''))

    def initDetail(self):
        self.frm_right = ttk.Frame(self.panedwin, relief=tk.SUNKEN)  # 右侧Frame帧用于放置视频区域和控制按钮
        self.frm_right.grid(row=0, column=0, sticky=tk.NSEW)  # 右侧Frame帧四个方向拉伸
        self.panedwin.add(self.frm_right, weight=3)  # 将右侧Frame帧添加到推拉窗控件,右侧权重10
        self.frm_right.columnconfigure(0, weight=1);  # 右侧Frame帧两行一列，配置列的权重
        self.frm_right.rowconfigure(0, weight=3);  # 右侧Frame帧两行的权重8:1
        # self.frm_right.rowconfigure(1, weight=1)

        self.text_output = tk.Text(self.frm_right, relief=tk.RIDGE, height=16)
        self.text_output["bg"] = "#21252B"
        self.text_output["fg"] = "#ABB2BF"
        self.text_output["insertbackground"] = "#ABB2BF"
        self.text_output["font"] = self.ft
        self.text_output.grid(row=0, column=0, sticky=tk.NSEW)
        self.text_output.tag_config('link', foreground='#F39801')

        scr2 = ttk.Scrollbar(self.frm_right, orient=tk.VERTICAL, command=self.text_output.yview)
        scr2.grid(row=0, column=1, sticky=tk.NSEW)
        self.text_output.configure(yscrollcommand=scr2.set)

        # 测试数据
        # for i in range(80):
        #     self.text_output.insert(tk.END, '%s:%s\n' %('1', i))

        # 右边底部区域
        self.frm_control = ttk.Frame(self.frm_right)  # 四个方向拉伸
        self.frm_control.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2)

        self.frm_control.columnconfigure(0, weight=1);  # 配置控制区Frame各行列的权重
        # self.frm_control.rowconfigure(0, weight=1);  # 第一行状态栏
        # self.frm_control.rowconfigure(1, weight=1);  # 第二行按钮组
        # self.frm_control.rowconfigure(2, weight=4);  # 第三行翻译输入区域
        # self.frm_control.rowconfigure(3, weight=4);  # 第四行颜色管理

        frm_state = ttk.Frame(self.frm_control, padding=(0, 2))  # 第一行状态栏
        frm_state.grid(row=0, column=0, sticky=tk.NSEW)

        frm_state.columnconfigure(0, weight=300)
        frm_state.columnconfigure(1, weight=1)
        frm_state.rowconfigure(0, weight=1)

        self.lalbe_state = tk.Label(frm_state, height=1, textvariable=self.showState)
        self.lalbe_state["font"] = self.ft
        self.lalbe_state["padx"] = 4
        self.lalbe_state["bg"] = "#21252B"
        self.lalbe_state["fg"] = "#F39801"
        self.lalbe_state.grid(row=0, column=0, sticky=tk.NSEW)

        ttk.Labelframe(frm_state, width=15).grid(row=0, column=1)

        frm_but = ttk.Frame(self.frm_control, padding=(0, 4))  # 第二行按钮组
        frm_but.grid(row=1, column=0, sticky=tk.EW)

        # 按钮组区域大小调整触发事件
        # frm_but.bind("<Configure>", self.resize)

        cblists = ['转Base64编码',
                   '百度翻译',
                   '今日天气',
                   '查看线程'
                   ]

        for inx, cbname in enumerate(cblists):
            b = ttk.Button(frm_but, text=cbname)
            b["command"] = lambda arg=cbname: self.onButtonClicked(arg)
            b.grid(row=0, column=inx)

        for i in range(300):  # 为每列添加权重值以便水平拉伸
            frm_but.columnconfigure(i, weight=1)
        frm_but.rowconfigure(0, weight=1)

        frm_minput = ttk.Frame(self.frm_control)  # 第三行翻译输入区域
        frm_minput.grid(row=2, column=0, sticky=tk.NSEW)

        frm_minput.columnconfigure(0, weight=1)
        frm_minput.rowconfigure(0, weight=1)

        self.text_input = tk.Text(frm_minput, spacing1=3, height=3)
        self.text_input["font"] = self.ft
        self.text_input["insertbackground"] = "#ABB2BF"
        self.text_input["padx"] = 4
        self.text_input["bg"] = "#21252B"
        self.text_input["fg"] = "#ABB2BF"
        self.text_input.grid(row=0, column=0, sticky=tk.NSEW)

        scr4 = ttk.Scrollbar(frm_minput, orient=tk.VERTICAL, command=self.text_input.yview)
        scr4.grid(row=0, column=1, sticky=tk.NS)
        self.text_input.configure(yscrollcommand=scr4.set)

        s = ttk.Style()
        s.configure('My1.TFrame', relief='groove')
        s.configure('My2.TFrame', background='#334353')
        if colors:
            c = colors[0]
        else:
            c = '#FFFFFF'
        s.configure('showcolor.TLabel', background=c)
        s.configure('L1.TLabel', foreground="#334353")
        s.configure('B1.TButton', height=1)

        # 颜色管理区域
        frm_colormanage = ttk.Frame(self.frm_control, padding=(0, 4))
        frm_colormanage.grid(row=3, column=0, sticky=tk.NSEW)
        # frm_colormanage.columnconfigure(0, weight=1)
        frm_colormanage.columnconfigure(1, weight=3)
        frm_colormanage.rowconfigure(0, weight=1)

        # 颜色管理 - 左边区域
        frm_colors_left = ttk.Frame(frm_colormanage, padding=(4, 4), style='My1.TFrame')
        frm_colors_left.grid(row=0, column=0, sticky=tk.NSEW)

        frm_colors_left.columnconfigure(0, weight=1)
        frm_colors_left.columnconfigure(1, weight=1)
        frm_colors_left.rowconfigure(0, weight=1)

        self.frm_lb_showcolor = ttk.Frame(frm_colors_left, padding=(4, 4), width=200)  # 第四行版本信息
        self.frm_lb_showcolor.grid(row=0, column=0, sticky=tk.NSEW)

        self.frm_lb_showcolor.columnconfigure(0, weight=1)
        self.frm_lb_showcolor.rowconfigure(0, weight=2)
        # self.frm_lb_showcolor.rowconfigure(1, weight=1)
        # self.frm_lb_showcolor.rowconfigure(2, weight=1)

        ttk.Label(self.frm_lb_showcolor, style="showcolor.TLabel", width=10).grid(row=0, column=0, sticky=tk.NSEW)

        b = ttk.Button(self.frm_lb_showcolor, text='收藏色值')
        b["command"] = lambda arg=cbname: self.onButtonClicked('收藏色值')
        b.grid(row=1, column=0, sticky=tk.EW)

        b = ttk.Button(self.frm_lb_showcolor, text='拾取颜色')
        b["command"] = lambda arg=cbname: self.onButtonClicked('拾取颜色')
        b.grid(row=2, column=0, sticky=tk.EW)

        frm_lb_entry = ttk.Frame(frm_colors_left, padding=(2, 2), height=50)  # 第四行版本信息
        frm_lb_entry.grid(row=0, column=1, sticky=tk.NSEW)

        frm_lb_entry.columnconfigure(0, weight=1)
        frm_lb_entry.columnconfigure(1, weight=10)
        frm_lb_entry.columnconfigure(2, weight=1)
        frm_lb_entry.rowconfigure(0, weight=1)
        frm_lb_entry.rowconfigure(1, weight=1)
        frm_lb_entry.rowconfigure(2, weight=1)

        self.colorValues = {
            "RGB": tk.StringVar(), "DEC": tk.StringVar(), "HEX": tk.StringVar()
        }

        ttk.Label(frm_lb_entry, text="RGB:", style='L1.TLabel').grid(row=0, column=0, sticky=tk.EW)
        E = ttk.Entry(frm_lb_entry, width=12, textvariable=self.colorValues["RGB"])
        E.grid(row=0, column=1, sticky=tk.EW)
        E.bind("<Return>", lambda event, arg="RGB": self.onColorEditEnter(event, arg))

        ttk.Label(frm_lb_entry, text="DEC:", style='L1.TLabel').grid(row=1, column=0, sticky=tk.EW)
        E = ttk.Entry(frm_lb_entry, width=12, textvariable=self.colorValues["DEC"])
        E.grid(row=1, column=1, sticky=tk.EW)
        E.bind("<Return>", lambda event, arg="DEC": self.onColorEditEnter(event, arg))

        ttk.Label(frm_lb_entry, text="HEX:", style='L1.TLabel').grid(row=2, column=0, sticky=tk.EW)
        E = ttk.Entry(frm_lb_entry, width=12, textvariable=self.colorValues["HEX"])
        E.grid(row=2, column=1, sticky=tk.EW)
        E.bind("<Return>", lambda event, arg="HEX": self.onColorEditEnter(event, arg))

        # 颜色管理右边区域
        frm_colors_right = ttk.Frame(frm_colormanage, height=50, style='My1.TFrame')
        frm_colors_right.grid(row=0, column=1, sticky=tk.NSEW)

        frm_colors_right.columnconfigure(0, weight=1)
        frm_colors_right.rowconfigure(0, weight=1)

        self.colorGroup = tk.Text(frm_colors_right, spacing1=1, height=6)
        self.colorGroup["font"] = self.ft
        self.colorGroup["insertbackground"] = "#ABB2BF"
        self.colorGroup["padx"] = 4
        # self.colorGroup["relief"] = 'groove'
        self.colorGroup["bg"] = "#DDDDDD"
        self.colorGroup["fg"] = "#ABB2BF"
        self.colorGroup.grid(row=0, column=0, sticky=tk.NSEW)

        self.onBuildColorGroup(self.colorGroup)
        scr5 = ttk.Scrollbar(frm_colors_right, orient=tk.VERTICAL, command=self.colorGroup.yview)
        scr5.grid(row=0, column=1, sticky=tk.NS)
        self.colorGroup.configure(yscrollcommand=scr5.set)

    # def resize(self, e):
    #     # 控件大小调整触发事件
    #     logger.info(e.width)

    # def showStinOut(self):
    #     # 读取控制台输出消息
    #
    #     self.sio.seek(0)
    #     lines = self.sio.readlines()
    #     self.text_output.delete(0.0, tk.END)
    #     if len(lines) > 0:
    #         for line in lines:
    #             content = line.strip()
    #             self.text_output.insert(tk.END, '%s\n' % content)
    #     else:
    #         self.text_output.insert(tk.END, '%s\n' % "暂无异常~~~")

    # self.sio.seek(self.nseek)
    # lines = self.sio.readlines()
    # self.text_output.delete(0.0, tk.END)
    # if len(lines) > 0:
    #     for line in lines:
    #         self.nseek += len(line)
    #         content = line.strip()
    #         self.text_output.insert(tk.END, '%s\n' % content)
    # if content[:2] == ">>":
    #     self.text_output.tag_add('link', '%s.0' % self.rownum, '%s.11' % self.rownum)
    # self.rownum += 1
    # self.text_output.see(tk.END)
    # self.thireadStinout = Timer(2, self.stinOut)
    # self.thireadStinout.start()

    def createMenuItem(self, event, menubar, item):
        self.rightMenubar.delete(0, tk.END)
        self.rightMenubar.add_command(label='删除色值', command=lambda arg=item: self.delColor(arg))
        self.rightMenubar.post(event.x_root, event.y_root)

    def delColor(self, item):
        colors.remove(item)
        self.colorGroup.delete(0.0, tk.END)
        self.onBuildColorGroup(self.colorGroup)
        # 保存删除后的color列表
        with open('color.data', 'w') as f:
            f.write(str(colors))

    def showDetail(self, event):
        # event.widget获取Treeview对象，调用selection获取选择对象名称

        sels = event.widget.selection()
        if len(sels) == 1:
            self.text_output.delete(0.0, tk.END)
            qid = self.tree_qlist.item(sels[0])['text']
            qid = str(qid)
            self.selectedQid = qid
            content = "%s\n" % ('在浏览器中>>')
            info = self.qlist[qid]
            for x in self.showDetails:
                tmp = info[x] if "content" != x else "\n" + info[x] + "\n"
                content += '{0}{1} : {2}\n'.format(x, '\t' * 2, tmp)
            content += "=" * 50
            self.addToOutput(content)
            button_asker = tk.Button(self.text_output, text='查看提问人')
            button_asker["command"] = lambda: self.onButtonClicked('查看提问人')
            self.text_output.window_create(1.15, window=button_asker)

    def showDetailInBrower(self, qid):
        url = "https://zhidao.baidu.com/question/%s.html?entry=uhome_homecenter_recommend" % qid
        self.browser.open(url)

    def showUserInBrower(self):
        if self.selectedQid:
            url = "https://zhidao.baidu.com/usercenter?uid=%s" % self.qlist[self.selectedQid]['imId']
            self.browser.open(url)

    def showTransResult(self):
        self.text_output.delete(0.0, tk.END)
        inputStr = self.text_input.get(0.0, tk.END).strip()
        outText = ""
        if inputStr:
            outText = "正在翻译：%s\n" % inputStr
            self.addToOutput(outText)
            res = self.translater.sendTranslatePost(inputStr)
            outText += "翻译结果：%s" % res if res else "翻译失败"
            self.addToOutput(outText)
        else:
            self.addToOutput("请输入要翻译的内容！")

    def showLisUpdate(self):
        nmsg = "(有%s消息未处理)" % self.msgcount if self.msgcount else ""
        qcount = "记录数：%s/%s" % (len(self.qfiltered), len(self.qlist))
        self.addToState("最后更新时间：%s %s %s" % (TimeOfNow(), nmsg, qcount))

    def showVerInfo(self):
        self.addToOutput(note)

    def addToOutput(self, s):
        self.text_output.delete(0.0, tk.END)
        self.text_output.insert(tk.END, s + '\n')

    def addToState(self, s):
        self.showState.set(s)

    def onMouseWatch(self):
        self.dc = windll.user32.GetDC(0)
        with Listener(on_move=self.onGlobalMouseMove, on_click=self.onGlobalMouseClick) as listener:
            listener.join()

    def getc(self, x, y):
        # 监听全屏鼠标移动（包括窗口外）
        pass
        # DEC = getcolor(self.dc, x, y)
        # logger.info(DEC)
        # R, G, B = Int2Rgb(DEC)
        # s = ttk.Style()
        # s.configure('showcolor.TLabel', background=Rgb2Hex(R, G, B))

    def onGlobalMouseMove(self, x, y):
        pass
        # 监听全屏鼠标移动（包括窗口外）
        # logger.info('mousepos:{0}'.format((x, y)))
        # self.getc(x,y)
        # logger.info('rgb:{0}'.format(getcolor(x, y)))

    def onGlobalMouseClick(self, x, y, button, pressed):
        # 监听颜色吸管启动后的,鼠标点击事件
        logger.info('{0} at {1}'.format('mouse click ', (x, y)))
        if not pressed:
            DEC = getcolor(self.dc, x, y)
            logger.info(DEC)
            R, G, B = Int2Rgb(DEC)
            s = ttk.Style()
            h = "#%s" % Rgb2Hex(R, G, B)
            s.configure('showcolor.TLabel', background=h)
            # Stop listener
            self.main.wm_attributes('-topmost', 1)
            self.main.wm_attributes('-topmost', 0)
            return False

    def onBuildColorGroup(self, t):
        for color in colors:
            # "flat(默认),sunken,raised,groove,ridge
            l = tk.Label(t, text=color, width=10, bg=color, relief="flat")
            t.window_create(tk.END, window=l)
            l.bind("<Enter>", lambda event, arg=color, obj=l: self.onColorMoveIn(event, arg, obj))
            l.bind("<Leave>", lambda event, arg=color, obj=l: self.onColorMoveOut(event, arg, obj))

            # 绑定左键键鼠标事件
            l.bind("<Button-1>", lambda event, arg=color: self.onColorClicked(event, arg))
            # 绑定右键鼠标事件
            l.bind("<Button-3>", lambda event, lable=l, arg=color: self.createMenuItem(event, lable, arg))

    def onColorMoveIn(self, e, color, obj):
        obj["relief"] = 'groove'
        obj["cursor"] = "arrow"

    def onColorMoveOut(self, e, color, obj):
        obj["relief"] = "flat"

    def onListHeadClicked(self, Head):
        self.qListSort(Head)

    def onListDoubleClicked(self, event):
        sels = event.widget.selection()
        if len(sels) == 1:
            qid = self.tree_qlist.item(sels[0])['text']
            self.showDetailInBrower(qid)

    def onButtonClicked(self, cbname):
        if cbname == '查看线程':
            logger.info(threading.activeCount())
            for th in threading.enumerate():
                logger.info(th)
        elif cbname == "刷新列表":
            logger.info(cbname)

        elif cbname == '系统设置':
            self.main.GotoConfig(self)

        elif cbname == '查看提问人':
            self.showUserInBrower()

        elif cbname == '转Base64编码':
            path_ = askopenfilename()
            if path_:
                res = ImgTobase64(path_)
                self.addToOutput(res)

        elif cbname == '百度翻译' and self.text_input.get(0.0, tk.END):

            self.after(500, self.showTransResult)

        elif cbname == "拾取颜色":
            logger.info("拾取颜色")
            self.after(500, self.onMouseWatch)

        elif cbname == "收藏色值":
            cHex = self.colorValues['HEX'].get()
            if not cHex:
                self.addToState("请输入要保存的色值，按回车确认")
                return
            elif len(cHex) == 7 and cHex[0] == "#":
                if cHex not in colors:
                    colors.append(cHex)
                    l = tk.Label(self.colorGroup, text=cHex, width=10, bg=cHex, relief="groove")
                    self.colorGroup.window_create(tk.END, window=l)

                    l.bind("<Enter>", lambda event, arg=cHex, obj=l: self.onColorMoveIn(event, arg, obj))
                    l.bind("<Leave>", lambda event, arg=cHex, obj=l: self.onColorMoveOut(event, arg, obj))

                    # 绑定左键键鼠标事件
                    l.bind("<Button-1>", lambda event, arg=cHex: self.onColorClicked(event, arg))
                    # 绑定右键鼠标事件
                    l.bind("<Button-3>", lambda event, lable=l, arg=cHex: self.createMenuItem(event, lable, arg))
                    with open('color.data', 'w') as f:
                        f.write(str(colors))
                else:
                    self.addToState("该色值已经收藏过了")
            else:
                self.addToState("HEX色值格式不对，请确认")
                return
        # elif cbname == '线程信息':
        #     logger.info(taskList)
        #
        # elif cbname == '终止多线程':
        #     global stopApp
        #     stopApp = True

        elif cbname == '今日天气':
            self.updateWeather()

    def onColorClicked(self, e, HEX):
        self.colorValues["HEX"].set(HEX)
        self.onColorEditEnter(e=None, w="HEX")

    def onEditChange(self, var):
        if not var.get():
            self.qListFilter()
            self.canvas["width"] = 0
        else:
            self.canvas["width"] = 22

    def onClearEnter(self, e=None):
        self.entry_var.set('')
        self.qListFilter()

    def onColorEditEnter(self, e, w):
        item = self.colorValues[w].get()
        c_rgb, c_dec, c_hex = [None] * 3
        if w == "RGB":
            c_rgb = item.split(",")
            R, G, B = [int(x) for x in c_rgb]
            c_dec = Rgb2Int(R, G, B)
            c_hex = "#%s" % Rgb2Hex(R, G, B)
            self.colorValues["DEC"].set(str(c_dec))
            self.colorValues["HEX"].set(c_hex)
        elif w == "DEC":
            c_dec = int(item)
            R, B, G = Int2Rgb(c_dec)
            c_rgb = "%s,%s,%s" % (R, B, G)
            c_hex = "#%s" % Rgb2Hex(R, B, G)
            self.colorValues["RGB"].set(c_rgb)
            self.colorValues["HEX"].set(c_hex)
        else:
            c_hex = item
            R, B, G = Hex2Rgb(c_hex)
            c_rgb = "%s,%s,%s" % (R, B, G)
            c_dec = Rgb2Int(R, B, G)
            self.colorValues["DEC"].set(str(c_dec))
            self.colorValues["RGB"].set(c_rgb)
        s = ttk.Style()
        s.configure('showcolor.TLabel', background=c_hex)

    def onEditEnter(self, e=None):
        item = self.entry_var.get()
        if item[:4] == "page":
            # 搜索输入框，输入 page前缀 启动列表更新
            try:
                pn = int(item[4:])
                self.threadUpdateInfo.cancel()
                self.updateInfo(pn)
                self.entry_var.set('')
            except BaseException as e:
                logger.info(e)
        else:
            self.qListFilter()

    # def onCheckButtonClicked(self):
    #     if self.checkbuttonState.get():
    #         self.isSave = True
    #     else:
    #         self.isSave = False
    #
    #     with open(self.configFileName, 'w') as f:
    #         f.write("{'issave':%s}" % (str(self.isSave)))

    def onMouseIn(self, e):
        self.addToOutput('鼠标移入')

    def onMouseOut(self, e):
        logger.info("onMouseOut")

    def updateMsgCount(self):
        # 刷新消息数
        url = "https://zhidao.baidu.com/notice/get/unreadcount?iswrap=0&t=%s" % StampOfNow()
        response = requests.get(url, cookies=self.cookie_jar)
        reslis = response.json()
        self.msgcount = reslis['data']['total']
        if self.msgcount > 0: playsound(self.wavfile1)

    def updateWeather(self):
        # 刷新天气
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "http://www.weather.com.cn/weather1d/101250401.shtml",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
        }

        url = "http://d1.weather.com.cn/weather_index/101250401.html?_=%s" % StampOfNow()
        rep = requests.get(url, headers=headers)
        rep.encoding = "utf-8"
        trans = rep.text.split("var ")
        infos = [eval(x.strip(";").split("=")[1]) for x in trans[1:]]
        T = infos[0]['weatherinfo']
        W = (T['cityname'], T['temp'], T['tempn'], T['weather'], T['wd'], T['ws'])
        self.addToState("城市：%s 最高气温：%s 最低气温：%s 天气：%s 风向：%s 风力：%s" % W)

    def updateInfo(self, pn=1):
        # runing.put("updateInfo")
        # 更新消息数
        self.addToState("%s: 开始更新问题列表" % TimeOfNow())
        self.updateMsgCount()
        self.pushPostData['pn'] = pn
        self.pushPostData['t'] = StampOfNow()

        try:
            response = requests.post(self.pushUrl, self.pushPostData, cookies=self.cookie_jar)
        except BaseException as e:
            logger.info(e)
            # runing.get()
            return

        try:
            reslis = response.json()['data']['detail']
        except BaseException as e:
            logger.info(e)
            # runing.get()
            return

        # 无拉取信息
        if not reslis:
            # runing.get()
            return

        # 处理信息
        # 按创建日期排序

        try:
            reslis.sort(key=lambda x: x['createTimeOrg'])
        except BaseException as e:
            logger.info(e)
            # runing.get()
            return

        # 去重
        isadd = False
        for x in reslis:
            if x["qid"] not in self.qlist:
                isadd = True
                self.qlist[x["qid"]] = x
                time_local = time.localtime(x["createTimeOrg"])  # 格式化时间戳为本地时间
                self.qlist[x["qid"]]["createTimeOrg"] = time.strftime("%m-%d %H:%M", time_local)
                var = [x[col['col']] for col in self.listBind]
                self.tree_qlist.insert("", 0, text=x["qid"], values=var)
                self.qfiltered.append([x["qid"]] + var)
        # 有新问题，音效提示
        if isadd:
            playsound(self.wavfile2)
            if self.isSave:
                try:
                    with open(self.dataFileName, 'w') as f:
                        content = f.write(str(self.qlist))
                except BaseException as e:
                    logger.info("update", e)
        self.showLisUpdate()
        # runing.get()

    def qListClear(self):
        x = self.tree_qlist.get_children()
        for item in x:
            self.tree_qlist.delete(item)

    def qListFilter(self, e=None):
        self.qListClear()
        self.qfiltered = []

        def filterRule(x):
            kw = self.Entry_query.get()
            return True if kw in x["title"] or kw in x["uname"] else False

        reslis = filter(filterRule, self.qlist.values())

        for item in reslis:
            var = [item[col['col']] for col in self.listBind]
            self.tree_qlist.insert("", 0, text=item["qid"], values=var)
            self.qfiltered.append([item["qid"]] + var)

        self.showLisUpdate()

    def qListSort(self, kw):
        self.qListClear()
        self.head[kw]['sort'] = False if self.head[kw]['sort'] else True
        self.qfiltered.sort(key=lambda x: x[self.head[kw]['inx']], reverse=self.head[kw]['sort'])
        for item in self.qfiltered:
            self.tree_qlist.insert("", 0, text=item[0], values=item[1:])


# class ConfigFrame(tk.Frame):
#     # 配置界面
#     def __init__(self, master):
#         super().__init__(master)
#         master.rowconfigure(0, weight=1)
#         master.columnconfigure(0, weight=1)
#         self.ft = tkFont.Font(family='微软雅黑', size=10, weight='bold')  # 创建字体
#         configs = {
#             "autoqlist": {"value": True, "note": "加载百度知道问题列表自动刷新模块"},
#             "issave": {"value": True, "note": "是否保存问题列表"},
#             "translate": {"value": True, "note": "加载百度翻译模块"},
#             "air": {"value": True, "note": "加载天气查询模块"},
#             "base64": {"value": True, "note": "加载Base64编码生成模块"},
#             "colormanage": {"value": True, "note": "加载颜色值管理模块"}
#         }
#
#         self.grid(row=0, column=0, sticky=tk.NSEW)
#         self.stateValues = {}
#         self.checkbuttonState = tk.IntVar()
#         row = 0
#         for item in configs:
#             self.stateValues.setdefault(item, tk.IntVar())
#             self.stateValues[item].set(configs[item]["value"])
#             rb = ttk.Checkbutton(self, onvalue=1, offvalue=0)
#             rb["variable"] = self.stateValues[item]
#             rb["text"] = configs[item]["note"]
#             rb["command"] = self.onCheckButtonClicked
#             rb.grid(row=row, column=0)
#             row += 1
#
#     def onCheckButtonClicked(self):
#         pass


if (__name__ == '__main__'):

    note = """
    tkinter GUI实例程序
    作者: xiaox
    联系: 18627472125

    1、自动拉取百度知道个人中心的,待回答问题列表。并且在发现有新问题的时候，进行音效提醒。
    2、对已拉取的数据进行增删改查。
    3、生成提问人信息（这个网页本身是无法查看的）、问题详情的URL地址，并自动打开浏览器查看。
    4、调用百度翻译接口，翻译输入的文本。
    5、查看本地天气情况（爬取信息来源http://www.weather.com.cn/）
    6、颜色值的管理：颜色吸管、保存常用色值、不同类型色值互查
    7、资源文件转Base64编码
    """
    # 隐藏控制台交互界面
    whnd = windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        windll.user32.ShowWindow(whnd, 0)
        windll.kernel32.CloseHandle(whnd)

    # 控制台信息输出到log.txt
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler("log.txt")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(console)

    # 主程序关闭标记，提示多线程管理，终止未启动线程
    stopApp = False

    # 更新频率
    coolDown = 0

    taskList = []

    # 多线程执行状态
    # runing = Queue()
    # 查询按钮图片
    imageQuery = None

    # 颜色收藏数据读取
    with open("color.data", 'r') as f:
        content = f.read()
    colors = eval(content) if content else {}
    main = App()
