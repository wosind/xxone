import os


def ReadFile(fname):
    try:
        with open(fname, 'r') as f:
            res = f.read()
    except BaseException as e:
        print(e)
        print(fname)
        print(f)
        res = ""
    return res


def find(key):
    res = []
    for x in files:
        if not x[2]: continue
        for f in x[2]:
            if f[-3:] == "bin": continue
            path = "%s\\%s" % (x[0], f)
            content = ReadFile(path)
            if key in content: res.append(path)
    return res


if __name__ == '__main__':
    files = os.walk("d:\\srout\\")
    files = [i for i in files][1:]
    res = find("临检工作")
    print()
    print("result:\n")
    for x in res:
        print(x)


