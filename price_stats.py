import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

import const

df_ts = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
df_ts = df_ts.astype(const.TYPE_DICT_AGG)

count_active = df_ts.groupby(['service_city', 'installer_name'])[['year_month']].aggregate('count')

# print(count_active[count_active['year_month'] == 36])

temecula = df_ts[df_ts['service_city'] == 'temecula']
# temecula
# print(temecula[temecula['app_received'] > 3])
# print(temecula[temecula['installer_name']=='tesla energy operations inc'])


temecula_avg_cost = temecula[temecula['total_cost'] > 0].groupby(['year_month'])['total_cost'].aggregate('mean').reset_index()
temecula_avg_cost_adjusted = temecula[temecula['total_cost'] > 0].groupby(['year_month'])['adjusted_price'].aggregate('mean').reset_index()

avg_cost_adjusted = df_ts[df_ts['total_cost']>0].groupby(['year_month', 'service_city', 'installer_name'])['adjusted_price'].aggregate('mean').reset_index()
# avg_cost_adjusted = avg_cost_adjusted[avg_cost_adjusted['installer_name'] == "tesla energy operations inc"]


print(avg_cost_adjusted[avg_cost_adjusted['adjusted_price'] < 0])
plt.scatter(avg_cost_adjusted['year_month'], avg_cost_adjusted['adjusted_price'])
plt.suptitle("Average Adjusted Cost by month, city, installer")
plt.show()
