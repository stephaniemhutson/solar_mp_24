import numpy as np
import collections


total_N = 200000
N = 2000
mu = N*.3

T = 100
t = 0
BETA = 0.98
P = 2000

def get_tau(t, current_period):
    if current_period > -1:
        if t > 65:
            return .08
        else:
            return .32
    else:
        return .32

def get_benefit(tau, s):
    return sum([BETA**(n+s) * (1000*12 + tau*500*12)
        for n in range(20)
    ])

def demanded(p, t, w):
    tau = get_tau(t, t)

    cost = p + 5000

    benefit = get_benefit(tau, t) + 1000*np.random.gumbel()

    value = benefit - cost


    delay_value = sum( (0.5**(n+1))*(get_benefit(get_tau(t+n+1, t), t+n+1) -p) for n in range(20)) + 1000*np.random.gumbel()

    return value > delay_value


def get_period(p, people, t):
    demand = 0
    for i in range(people):
        demand += demanded(p, t, 0)
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

for t in range(T):

    demand = get_period(P, people, t)
    # people = people + int(0.01*(total_N)) - demand
    total_N -= int(0.01*(total_N))
    people = int(people + mu - demand)
    # print(people)
    flow.append(demand)

print(flow)

# buys = collections.Counter()
# for i in range(N):
#     instance = get_instance()
#     for j, tf in enumerate(instance):
#         buys[j] += tf

# print(buys)
