import tkinter, win32api, win32con, pywintypes

root = tkinter.Tk()
root.overrideredirect(True)
root.geometry("+1100+450")  # 设置窗口位置或大小
root.lift()
root.wm_attributes("-topmost", True)
root.wm_attributes("-disabled", True)
root.wm_attributes("-transparentcolor", "white")  # 白色背景透明
hWindow = pywintypes.HANDLE(int(root.frame(), 16))
exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
framenum = 30  # gif 的帧数需要确定下来
giffile = 'D:/Python35/mypy/timg.gif'  # 找一张白色背景的gif，设置白色为透明
frames = [tkinter.PhotoImage(file=giffile, format='gif -index %s' % i) for i in range(framenum)]


def update(ind):
    if (ind == framenum - 1):  #
        ind = 0
    frame = frames[ind]
    ind += 1
    label.configure(image=frame)
    root.after(100, timer, ind)


label = tkinter.Label(root, bg='white')  # 设置白色为透明
label.pack()  # 显示
root.after(0, timer, 0)
root.mainloop()  # 循环