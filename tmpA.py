from random import randint

# 用于判断输入的字符，是否合法
nums = [str(x) for x in range(10)]
symbol = ["+", "-", "*", "/", "(", ")"]

# 获取字符类型
def getType(s):
    return "Num" if s in nums else "Symbol" if s in symbol else "illegal"

def genNums():
    res = [randint(1, 13) for x in range(4)]
    res.sort()
    return res

def checkInput(s, randLis):
    # 替换掉（）
    if not s:
        print("注意：输入为空")
        return False
    numLis = []
    s = s.replace("(", "").replace(")", "")
    if s[0] in symbol or s[-1] in symbol:
        print("注意：不能以运算符开头和结尾")
        return False
    elif [x for x in s if getType(x) == "illegal"]:
        print("注意：发现无效字符")
        return False
    else:
        lastType, lastStr = "Num", ""
        for x in s:
            if getType(x) == "Symbol" == lastType:
                print("注意：发现连续多个运算符")
                return False
            elif getType(x) == "Num" == lastType:
                lastStr += x
            elif getType(x) == "Symbol" and lastType == "Num":
                numLis.append(lastStr)
                lastStr = ""
            else:
                lastStr += x
            lastType = getType(x)
        numLis.append(lastStr)
    res = [int(x) for x in numLis]
    res.sort()
    if randLis == res:
        return True
    else:
        print("注意：输入的数字不匹配")
        return False

if __name__ == '__main__':
    f = 1
    while True:
        randLis = genNums()
        a, b, c, d = randLis
        print("请使用%d，%d，%d，%d和加减乘除的运算来算出24吧！" % (a, b, c, d))
        while True:
            h = input("请输入算式:")
            if checkInput(h, randLis):break
        g = eval(h)
        if g == 24:
            print("完成！目前是第%d关，进入下一关！" % (f))
        else:
            print("%s=%s" % (h, g))
            print("真遗憾，您答错了，目前是第%d关，游戏结束。" % (f))
            break
