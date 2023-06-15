import random

idx = 0
ts = 0
total = 120 # sec
totalSamples = total * 1000 / 20
avg = 5
rng = 5

while idx < totalSamples:
    print(ts)
    ts += random.randint(avg - rng, avg + rng)
    idx += 1
