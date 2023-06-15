import sys
import os
import re
import math
import matplotlib.pyplot as plt
import numpy as np

# 10806: tick(0.012857) 1
matchRe = re.compile("(\d+): tick\((\d+\.?(?:\d+)?)\) (\d+)", re.DOTALL)

# 104842: -SKIP- (0.000000)
matchReZero = re.compile("(\d+): -SKIP- \((\d+\.?(?:\d+)?)\)", re.DOTALL)

t = []
v = []
with open(sys.argv[1], 'r') as f:
    for line in f.readlines():
        match = matchRe.search(line)
        if match is not None:
            items = match.groups()
            ts = int(items[0])
            cnt = int(items[2])
            t.append(ts)
            v.append(cnt)
            continue

        match = matchReZero.search(line)
        if match is not None:
            ts = int(match.groups()[0])
            t.append(ts)
            v.append(0)

fig = plt.figure(figsize =(10, 8))

ax1 = fig.add_subplot(2, 1, 1)
ax1.plot(t, v, 'x', color='green', label='cnt')
ax1.grid(True)
ax1.set_xlabel('ms')
ax1.set_ylabel('#')
ax1.legend()

ax2 = fig.add_subplot(2, 1, 2)
ax2.hist(v)

fig.tight_layout()

plt.show()
