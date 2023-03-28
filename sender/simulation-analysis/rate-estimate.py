import sys
import matplotlib.pyplot as plt

fh=open(sys.argv[1])
acc=[0]*3700 # 1 hour of data
start = end = None
for line in fh.readlines() :
    time=int(float(line.split()[0]));
    acc[(time//1000)]=acc[(time//1000)]+8*1500; # ms to sec
    if start is None:
        start = time//1000
    end = time//1000

secs = end - start + 1
t = []
v = []
for i in range(0,secs) :
    t.append(i)
    v.append(acc[i]/1.0e6)
    print(i,"\t",(acc[i]/1.0e6)); # in mbps

fig, axs = plt.subplots(1, 1)
axs.plot(t, v)
axs.grid(True)
axs.set_xlabel('sec')
axs.set_ylabel('mbps')

fig.tight_layout()
plt.show()
