import sys
import os
import re
import math
import matplotlib.pyplot as plt
import numpy as np

def prepare_plot(acc):
    t = []
    v = []
    for i in range(0,len(acc)):
        rateMbps = acc[i]/1.0e6
        t.append(i)
        v.append(rateMbps)
        print(i,"\t",rateMbps); # in mbps
    return (t, v)

ppsSrc = sys.argv[1]
os.system("cat %s | ./vbrssp > vbrssp.log 2>&1" % ppsSrc)

# convert log to pps
matchRe = re.compile("(\d+\.?(?:\d+)?) : packet delivered", re.DOTALL)
matchReStatus = re.compile("(\d+\.?(?:\d+)?), sent = \d+, dpr = \d+, fc = (\d+), cur est = (\d+), cum dev forecast = (\d+), to send = (\d+)", re.DOTALL)
start = None
deliverTimeSecs = []
status = []

with open('vbrssp.log', 'r') as f:
    for line in f.readlines():
        match = matchRe.search(line)
        if match is not None:
            if start is not None:
                curr = float(match.groups()[0])
                deliverTimeSecs.append(curr - start)
            else:
                start = float(match.groups()[0])
                deliverTimeSecs.append(0)
            continue

        match = matchReStatus.search(line)
        if match is not None:
            status.append(match.groups())

totalSecs = math.ceil(deliverTimeSecs[-1])
acc = [0] * totalSecs
print('total sec: %d' % totalSecs)

for timeSec in deliverTimeSecs:
    timeSecInt = int(timeSec // 1)
    acc[timeSecInt] = acc[timeSecInt] + 8 * 1500


fig = plt.figure(figsize =(20, 8))

t, v = prepare_plot(acc)
ax1 = fig.add_subplot(2, 1, 1)
ax1.plot(t, v, 'x', color='green', label='delivered')
#ax.plot(t, v, color='green', label='delivered')

# sent
acc = [0] * totalSecs
start = None
for item in status:
    if start is None:
        start = float(item[0])
    sent = int(item[4])
    now = float(item[0])
    timeSecInt = int( (now - start) // 1)
    acc[timeSecInt] = acc[timeSecInt] + sent * 8 * 1500
ax1.plot(t, v, '^', color='blue', label='sent')

acc = [0] * totalSecs
with open(ppsSrc, 'r') as f:
    for line in f.readlines():
        time=int(float(line.split()[0]));
        timeSecInt = time//1000
        acc[timeSecInt]=acc[timeSecInt]+8*1500; # ms to sec

t, v = prepare_plot(acc)
ax1.plot(t, v, color='red', label='measured', alpha=0.5)
#ax1.fill_between(t, v, color='red', label='measured', alpha=0.5)
ax1.grid(True)
ax1.set_xlabel('sec')
ax1.set_ylabel('mbps')
ax1.legend()

ax2 = fig.add_subplot(2, 1, 2, sharex = ax1)
ax2.plot([float(item[0]) for item in status], [int(item[1]) for item in status], 'x', label='fc')
ax2.plot([float(item[0]) for item in status], [int(item[2]) for item in status], '*', label='est')
ax2.plot([float(item[0]) for item in status], [int(item[3]) for item in status], '^', label='cum')
ax2.plot([float(item[0]) for item in status], [int(item[4]) for item in status], 'o', label='sent')
ax2.grid(True)
ax2.set_xlabel('sec')
ax2.set_ylabel('cnt')
ax2.legend()

fig.tight_layout()
plt.show()