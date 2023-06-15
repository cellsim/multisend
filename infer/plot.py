import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.pyplot import cm
import re

def plot_process_evolv():
    # [56]midpoint 1765.625000, value = 0.009959
    match_re = re.compile("midpoint (\d+\.?(?:\d+)?), value = (\d+\.?(?:\d+)?)", re.DOTALL)

    recList = []
    rec = []
    idx = 0
    TOTAL = 65
    with open('process.log', 'r') as f:
        for line in f.readlines():
            match = match_re.search(line)
            if match is None: continue
            if idx == 0:
                if len(rec) == TOTAL:
                    recList.append(rec)
                    rec = []
            rec.append([float(item) for item in match.groups()])
            idx = (idx + 1) % TOTAL

        if len(rec) == TOTAL:
            recList.append(rec)

        for idx, rec in enumerate(recList):
            print('\n#rec %d\n%s' % (idx, rec))

    barWidth = 3
    fig = plt.subplots(figsize =(12, 8))
    color = cm.rainbow(np.linspace(0, 1, len(recList)))

    for idx, rec in enumerate(recList):
        rates = [item[0] for item in rec]
        br = [x + barWidth * idx for x in rates]
        vals = [item[1] for item in rec]
        plt.bar(br, vals, color=color[idx], width = barWidth, label='[%d]'%idx)
    plt.legend()
    plt.show()

def plot_predict_components():
    # component 0, count for 29, prob = 0.000000, total = 1.000000
    match_re = re.compile("component (\d+), count for (\d+), prob = (\d+\.?(?:\d+)?)", re.DOTALL)
    
    recList = []
    rec = []
    with open('process.log', 'r') as f:
        for line in f.readlines():
            match = match_re.search(line)
            if match is None: continue
            items = match.groups()
            idx, cnt, prob = int(items[0]), int(items[1]), float(items[2])
            if cnt == 0:
                if len(rec) > 0:
                    recList.append(rec)
                    rec = []
            rec.append((idx, cnt, prob))

        if len(rec) > 0:
            recList.append(rec)

        for idx, rec in enumerate(recList):
            print('\n#rec %d\n%s' % (idx, rec))

    fig = plt.figure(figsize =(12, 8))
    ax = fig.add_subplot(projection='3d')
    color = cm.rainbow(np.linspace(0, 1, len(recList)))

    for idx, rec in enumerate(recList):
        rateIdxes = [item[0] for item in rec]
        pkts = [item[1] for item in rec]
        probs = [item[2] for item in rec]
        bottom = [0]*len(probs)
        width = 0.1
        depth = 0.5
        ax.bar3d(rateIdxes, pkts, bottom, width, depth, probs, color=color[idx], shade=True)
        # if idx == 2:
        #     break

    ax.set_xlabel('rate idx')
    ax.set_ylabel('pkt/sec')
    ax.set_zlabel('probability')

    plt.legend()
    plt.show()

def plot_component_count_prob():
    # [64] this_component_count_probability size: 88, 
    match_re = re.compile("\[(\d+)\] this_component_count_probability size: \d+, (.*)", re.DOTALL)

    recList = []
    with open('process.log', 'r') as f:
        for line in f.readlines():
            match = match_re.search(line)
            if match is None: continue
            items = match.groups()
            idx, prob = int(items[0]), items[1]
            items = [float(x) for x in prob.split()]
            recList.append(items)

        for idx, rec in enumerate(recList):
            print('\n#rec %d\n%s' % (idx, rec))

    fig = plt.figure(figsize =(12, 8))
    ax = fig.add_subplot(projection='3d')
    color = cm.rainbow(np.linspace(0, 1, len(recList)))

    for idx, probs in enumerate(recList):
        rateIdxes = [idx] * len(probs)
        pkts = [i for i in range(len(probs))]
        bottom = [0]*len(probs)
        width = 0.1
        depth = 0.5
        ax.bar3d(rateIdxes, pkts, bottom, width, depth, probs, color=color[idx], shade=True)
        # if idx == 2:
        #     break

    ax.set_xlabel('rate idx')
    ax.set_ylabel('pkt count')
    ax.set_zlabel('probability')

    plt.legend()
    plt.show()

def plot_predict_count_prob():
    # predict for count 0, prob = 0.000000 
    match_re = re.compile("predict for count (\d+), prob = (\d+\.?(?:\d+)?), percentile = (\d+\.?(?:\d+)?)", re.DOTALL)
    match_re1 = re.compile("predict: (\d+)", re.DOTALL)

    recList = []
    rec = []
    predicts = []
    with open('process.log', 'r') as f:
        for line in f.readlines():
            match = match_re.search(line)
            if match is not None:
                items = match.groups()
                cnt, prob, pct = int(items[0]), float(items[1]), float(items[2])
                if cnt == 0:
                    if len(rec) > 0:
                        recList.append(rec)
                    rec = []
                rec.append((cnt, prob, pct))
            
            match = match_re1.search(line)
            if match is not None:
                predicts.append(int(match.groups()[0]))
        
        if len(rec) > 0:
            recList.append(rec)

        for idx, rec in enumerate(recList):
            print('\n#rec %d\n%s' % (idx, rec))

        print(predicts)

    fig = plt.figure(figsize =(24, 8))
    color = cm.rainbow(np.linspace(0, 1, len(recList)))

    ax = fig.add_subplot(1, 2, 1, projection='3d')
    for idx, items in enumerate(recList):
        intervals = [idx] * len(items)
        pkts = [item[0] for item in items]
        probs = [item[1] for item in items]
        bottom = [0]*len(items)
        width = 0.1
        depth = 0.5
        ax.bar3d(intervals, pkts, bottom, width, depth, probs, color=color[idx], shade=True)
    ax.set_xlabel('interval#')
    ax.set_ylabel('pkt count')
    ax.set_zlabel('probability')

    ax = fig.add_subplot(1, 2, 2, projection='3d')
    for idx, items in enumerate(recList):
        intervals = [idx] * len(items)
        pkts = [item[0] for item in items]
        pcts = [item[2] for item in items]
        bottom = [0]*len(items)
        width = 0.1
        depth = 0.5
        ax.bar3d(intervals, pkts, bottom, width, depth, pcts, color=color[idx], shade=True)
    ax.set_xlabel('interval#')
    ax.set_ylabel('pkt count')
    ax.set_zlabel('percentile')

    plt.legend()
    plt.show()

# plot_process_evolv()
# plot_predict_components()
# plot_component_count_prob()
plot_predict_count_prob()