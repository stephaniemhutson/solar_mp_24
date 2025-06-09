import pandas as pd
import matplotlib.pyplot as plt
import const

def hhi():
    apps = pd.read_csv('./data/applications_cleaned.csv')
    apps = apps[apps['service_county'] != "San Joaquin"]
    apps = apps[apps['service_county'] != "Yuba"]
    apps = apps[apps['mounting_method'] == "Rooftop"]

    apps = apps.astype(const.TYPE_DICT)


    # Limit received to just 2022 - this way we don't have
    apps = apps[apps['app_received'] > pd.to_datetime('2022-01-01')]
    apps = apps[apps['app_received'] < pd.to_datetime('2023-01-01')]
    apps = apps[apps['NEM_tariff'] == '2.0']
    apps = apps[apps['self_install'] == False]


    plt.hist(apps['HHI_city'], bins=20)
    plt.show()



def model_demand():
    """
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
    """
    y = [
       477, 481, 489, 470, 461, 491, 451, 464, 438, 472, 467, 417, 469, 416, 439, 466, 429, 467,
       498, 583, 764, 1275, 2485, 1868, 27, 69, 78, 116, 131, 150, 185, 184, 166, 203, 217, 193,
       197, 230, 219, 248, 246, 232, 241, 236, 263, 242, 246,
    ]


    fig, ax = plt.subplots(1)
    ax.plot(y)
    fig.suptitle("Model demand for a given price taking into account anticipated change in tariff.")
    ax.set_yticklabels([])
    ax.set_xlabel("Time periods")
    ax.set_ylabel("Demand")
    plt.show()

model_demand()
# print((apps[apps['is_largest_firm'] == True][['installer_name', 'service_city']]))
# print(apps['service_city'].nunique())

