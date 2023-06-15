import sys
import os
import re
import math
import matplotlib.pyplot as plt
import numpy as np

# From tick 1(2) => 6(11), 4512 bytes to send with 8448 already sent
matchRe = re.compile("From tick (\d+)\((\d+)\) => (\d+)\((\d+)\), (\d+) bytes to send with (\d+) already sent", re.DOTALL)

ts = 0
t = []
v = []
with open(sys.argv[1], 'r') as f:
    for line in f.readlines():
        match = matchRe.search(line)
        if match is not None:
            items = match.groups()
            ts += 20
            t.append(ts//1000)
            v.append(items)

fig = plt.figure(figsize =(10, 8))

ax1 = fig.add_subplot(2, 2, 1)

# ax1.plot(t, [int(i[4])+int(i[5]) for i in v], color='yellow', label='fc')
ax1.fill_between(t, [int(i[4])+int(i[5]) for i in v], color='yellow', label='fc', alpha=0.9)

# ax1.plot(t, [int(i[4]) for i in v], 'x', color='green', label='sent')
ax1.fill_between(t, [int(i[4]) for i in v], color='green', label='sent', alpha=0.8)

# ax1.plot(t, [int(i[5]) for i in v], 'o', color='red', label='est')
ax1.fill_between(t, [int(i[5]) for i in v], color='red', label='est', alpha=0.2)

ax1.grid(True)
ax1.set_xlabel('sec')
ax1.set_ylabel('bytes')
ax1.legend()

ax2 = fig.add_subplot(2, 2, 2)
ax2.hist([int(i[4])+int(i[5]) for i in v], color='yellow', label='fc')
ax2.legend()

ax3 = fig.add_subplot(2, 2, 3)
ax3.hist([int(i[4]) for i in v], color='green', label='sent', alpha=0.8)
ax3.legend()

ax4 = fig.add_subplot(2, 2, 4)
ax4.hist([int(i[5]) for i in v], color='red', label='est', alpha=0.2)
ax4.legend()

fig.tight_layout()
plt.show()
