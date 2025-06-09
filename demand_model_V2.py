import numpy as np
import matplotlib.pyplot as plt

TECH = 1.002

KW_MO = 9000/12 # eia 2022 https://www.eia.gov/tools/faqs/faq.php?id=97&t=3
RATE_INCR = 1.001
SOLAR_OFFSET = 12000/12 # monthly
BETA = 0.997
PKW = 0.42
PRICE = 20000*.7
N =100
MU = N*.1
T = 50

RVs = list(np.random.gumbel(size=N*T*int(1.1**T)))

def get_tau(t):
    if t > 25:
        return .08
    else:
        return .32

def get_benefit(s, w, current_period):
    # assumes no change in electricity consumption
    tau = get_tau(s)
    return sum([BETA**(n+w) * ((SOLAR_OFFSET*TECH**s - KW_MO*RATE_INCR**(s+n+w))* tau)
        for n in range(20*12)
    ]) - KW_MO * w * PKW

def get_price(s):
    return PRICE

def get_value(s, w, current_period):
    return get_benefit(s, w, current_period) - get_price(s)

def get_inaction_benefit(s, w):
    return  sum(max(BETA**(s+n+1) *get_value(s+n+1, max(w - n, 0), s), 0) for n in range(100))

def demanded(s, w):
    v = get_value(s,w, s) + 1000*RVs.pop()
    vi = get_inaction_benefit(s, w) + 1000*RVs.pop()
    return v> vi

flow = []
people =N
for t in range(T):
    print(t)
    count = 0
    for n in range(people):
        count += demanded(t, 0)
    flow.append(count)
    people = int(people - count + MU)

print(flow)

fig, ax = plt.subplots(1, 1, figsize=(10, 6))

ax.plot(flow)
fig.suptitle("Model demand for a given price taking into account anticipated change in tariff.")
ax.set_yticklabels([])
ax.set_xlabel("Time periods")
ax.set_ylabel("Demand")
plt.savefig("./demand_model_V2.png")
plt.show()
