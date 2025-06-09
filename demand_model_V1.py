import numpy as np
import collections
import matplotlib.pyplot as plt

# total_N = 200000
N = 2000
mu = N*.37

throughput = int(mu*1.1)


T = 150
t = 0
BETA = 0.98
P = 2000
# disutility from waiting
OMEGA = 1.1

def get_tau(t, current_period):

    if t > 65:
        return .08
    else:
        return .32


def get_benefit(tau, s, w):
    return sum([BETA**(n+s) * (1000*12 + tau*500*12)
        for n in range(20)
    ]) - 100*w**OMEGA


def demanded(p, t, w):
    tau = get_tau(t, t)


    cost = p + 5000

    benefit = get_benefit(tau, t, w) + 1000*np.random.gumbel()

    value = benefit - cost

    # expected delay is current delay less the throughput of one additional preiod. Agents do not internalize the idea that waiting may result in
    # increased wait time.
    delay_value = sum( (0.5**(n+1))*(get_benefit(get_tau(t+n+1, t), t+n+1, max(w-(n+1), 0)) -p) for n in range(20)) + 1000*np.random.gumbel()

    return value > delay_value


def get_period(p, people, t, w):
    demand = 0
    for i in range(people):
        demand += demanded(p, t, w)
    return demand

# def get_instance():
#     counter = 0
#     periods = []
#     while counter < T:
#         buy = demanded(P, counter, 0)
#         counter += 1
#         periods.append(buy)
#     return periods

flow = []
people = N
queue = 0

for t in range(T):
    demand = get_period(P, people, t, queue/throughput)
    queue = max(queue + demand - throughput, 0)

    # people = people + int(0.01*(total_N)) - demand
    # total_N -= int(0.01*(total_N))
    people = int(people + mu - demand)
    # print(people)
    flow.append(demand)

print(flow)

fig, ax = plt.subplots(1, 1, figsize=(10, 6))

ax.plot(flow[40:90])
fig.suptitle("Model demand for a given price taking into account anticipated change in tariff.")
ax.set_yticklabels([])
ax.set_xlabel("Time periods")
ax.set_ylabel("Demand")
plt.savefig("./demand_model.png")
# plt.show()

# buys = collections.Counter()
# for i in range(N):
#     instance = get_instance()
#     for j, tf in enumerate(instance):
#         buys[j] += tf

# print(buys)
