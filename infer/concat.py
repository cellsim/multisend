import sys

ts = 0
with open(sys.argv[1], 'r') as f:
    for line in f.readlines():
        ts = int(line)
        print(ts)

with open(sys.argv[2], 'r') as f:
    for line in f.readlines():
        newTs = ts + int(line)
        print(newTs)