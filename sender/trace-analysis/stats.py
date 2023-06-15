import sys
import os
import re
import math
import matplotlib.pyplot as plt
import numpy as np

# OUTGOING ACK RECEIVED senderid=1686669162, seq=0, send_time=1686669162654182321,  recv_time=1686669162862354557, rtt=0.2082
matchReOut = re.compile("OUTGOING ACK RECEIVED senderid=\d+, seq=\d+, send_time=(\d+),  recv_time=\d+, rtt=(\d+\.?(?:\d+)?)", re.DOTALL)

# INCOMING DATA RECEIVED senderid=1686669162, seq=987584, send_time=1686669702870858920, recv_time=1686669701778144025, 1delay=-1.0927
matchReIn = re.compile("INCOMING DATA RECEIVED senderid=\d+, seq=(\d+), send_time=\d+, recv_time=(\d+), 1delay=", re.DOTALL)

startTs = None
# lastTs = None
ackTs = []
rttLst = []

lastSeq = None
lostTs = []
lostLst = []

oooTs = []
oooLst = []

preLine = None

with open(sys.argv[1], 'r') as f:
    for line in f.readlines():
        match = matchReOut.search(line)
        if match is not None:
            items = match.groups()
            ts = int(items[0])
            rtt = float(items[1])
            if startTs is None:
                startTs = ts
            ts -= startTs

            # if lastTs is not None and ts - lastTs > 10000 * 1e6:
            #     print(line)
            # lastTs = ts

            ackTs.append(ts//1e9) # sec
            rttLst.append(rtt*100) # ms
            continue

        match = matchReIn.search(line)
        if match is not None:
            items = match.groups()
            ts = int(items[1])
            seq = int(items[0])

            if startTs is None:
                startTs = ts
            ts -= startTs

            if lastSeq is None:
                lastSeq = seq

            if  seq > lastSeq + 1:
                lostTs.append(ts//1e9)
                lost = seq - lastSeq - 1
                if lost > 500:
                    print(preLine)
                    print(line)
                    print("===> lost %d" % lost)
                lostLst.append(lost)
            elif seq < lastSeq:
                oooTs.append(ts//1e9)
                oooLst.append(1)

            lastSeq = seq
            preLine = line

fig = plt.figure(figsize =(10, 8))

ax1 = fig.add_subplot(1, 3, 1)
ax1.plot(ackTs, rttLst, color='yellow', label='rtt')

ax1.grid(True)
ax1.set_xlabel('time (ms)')
ax1.set_ylabel('rtt (ms)')
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.plot(lostTs, lostLst, color='red', label='lost')
ax2.set_xlabel('time (ms)')
ax2.set_ylabel('lost (#)')
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.plot(oooTs, oooLst, 'x', color='blue', label='ooo')
ax3.set_xlabel('time (ms)')
ax3.set_ylabel('ooo')
ax3.legend()

fig.tight_layout()
plt.show()
