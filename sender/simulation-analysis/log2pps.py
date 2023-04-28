import sys

start = None
with open(sys.argv[1], 'r') as f:
    for item in f.readlines():
        group = item.split()
        if len(group) != 4 or group[0] != "send": continue
        ts = int(group[3])
        if start is not None:
            print(ts - start)
        else:
            start = ts
            print(0)
