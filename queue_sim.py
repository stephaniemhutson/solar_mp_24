import numpy as np
import collections


T = 2
d_T = [
    lambda p: 50 - p,
    lambda p: 30 - p,
]

ALPHA = 2/3
W = 5
CQ = 0
# DELTA = .1
# FC = 50

# y = lambda l: l**ALPHA

# q = collections.defaultdict(int)
# p = collections.defaultdict(float)

# def update_queue_get_to_do(y, q, d, period):
#     to_do = {}
#     for t, count in q.items():
#         if y > 0:
#             sub = min(y, count)
#             to_do[t] = sub
#             q[t] = count - sub
#             y -= count
#     to_do[period] = min(y, d)
#     q[period] = max(d - y, 0)

    return q, to_do

def attrophie_queue(q):
    for t, count in q.items():
        if count >0:
            q[t] = count - random.binomial(count, DELTA)
    return q

# def preiod_profit(q, p):
#     rev = 0
#     period = max(q.keys(), 0)
#     d = d_T[period](p)
#     # ... I need y. I need l


#     q, to_do = update_queue_get_to_do(y, q, d, period)
#     for t, count in to_do.items():
#         rev += count*p[t]

#     pi = rev - y**(1/ALPHA)*W


class Firm():

    def __init__(self, demand, alpha=ALPHA, fixed_cost=0, wage=W, queue_cost=0):
        self.ALPHA = alpha
        self.fc = fixed_cost
        self.w = wage
        self.qc = queue_cost
        self.d_T = demand
        self.__initialize_queue()

    def __initialize_objects(self):
        self._q = collections.defaultdict(int)
        self._q[0] = 0
        self._prices = collections.defaultdict(float)

    @property
    def q(self):
        return self._q

    @property
    def prices(self):
        return self._prices

    def period_profit(self, period, l):
        rev = 0
        d = self.d_T[period](self.prices[period])

        # ... I need y. I need l
        y = l**self.ALPHA

        q, to_do = self.update_queue_get_to_do(y, d, period)
        for t, count in to_do.items():
            rev += count*self.prices[t]

        pi = rev - y**(1/self.ALPHA)*self.q
        return pi

    def update_queue_get_to_do(self, y, d, period):
        to_do = {}
        for t, count in self.q.items():
            if y > 0:
                sub = min(y, count)
                to_do[t] = sub
                self.q[t] = count - sub
                y -= count
        to_do[period] = min(y, d)
        self.q[period] = max(d - y, 0)

        return to_do

    def choose_p(self, period):
        demand = self.d_T[period]
        queue = self.q






