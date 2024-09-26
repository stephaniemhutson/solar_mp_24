import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

import const

# From running NEM2_only from 2021 forward.
# 'total_cost ~ size_dc + battery_storage + pio_TF*days_to_completion + output_monitoring + C(service_county)  + ccci + has_battery'
price_per_kw = 1951.0652
price_battery_fixed = 8375.1875
price_battery_adjust = 2.6158

df = pd.read_csv('./data/applications_cleaned.csv')
df = df.astype(const.TYPE_DICT)
columns = [
    "app_id",
    "pre_id",
    "service_city",
    "service_county",
    "service_zip",
    "size_dc",
    # "size_ac",
    "battery_storage",
    "mounting_method",
    "tracking",
    "app_received",
    "app_complete",
    # "app_approved",
    "self_install",
    "installer_name",
    "installer_city",
    "cslb_num",
    "output_monitoring",
    "total_cost",
    "cost_per_watt",
    # "NEM_tariff",
    "technology_type",
    "electric_vehicle",
    "manufacturer",
    "days_to_completion",
    "is_NEM2",
    # "after_approval",
    # "pio_TF",
    # "year",
    # "month",
    "year_month",
    # "quarter",
    "market_share",
    # "ms_count",
    "market_share_squared",
    "HHI_city",
    "is_largest_firm",
    # "is_preceeded",
    # "after_anticipated_date",
    # "anticipation_period",
    "ccci",
    "year_month_comp",
    "has_battery"
]
df = df[columns]


early_date = pd.to_datetime('2020-12-31')
late_date = pd.to_datetime('2024-05-01')

df = df[df['year_month'] > early_date]
df = df[df['year_month'] < late_date]


df['mean'] = df.groupby(['year_month'])['total_cost'].transform('mean')
df['mean_city_month'] = df.groupby(['service_city', 'year_month'])['total_cost'].transform('mean')

# print(mean)
# print(mean_city_month)


# mean = mean_city_month.join(mean, on="year_month")

df["delta_mean_city_month"] = df['mean'] - df['mean_city_month']


df.loc[:, 'adjusted_price'] = (
    df.loc[:,'total_cost'] - df.loc[:,'battery_storage']*price_battery_adjust - df.loc[:,"has_battery"]*price_battery_fixed
    - df.loc[:, "delta_mean_city_month"]
)/df.loc[:,'ccci']


df_mean = df.groupby(
    ['service_city', 'installer_name', 'year_month']
)[
    ['size_dc', 'battery_storage', 'total_cost', 'is_largest_firm', 'days_to_completion', 'adjusted_price']
].aggregate('mean')

# df_mean.set_index(['service_city', 'installer_name', 'year_month'], inplace=True)

df_count = df.groupby(['service_city', 'installer_name', 'year_month'])[['app_received']].aggregate('count')
df_count_comp = df.groupby(['service_city', 'installer_name', 'year_month_comp'])[['app_complete']].aggregate('count')
# df_count.set_index(['service_city', 'installer_name', 'year_month'], inplace=True)

df_ts = df_mean.join(df_count, on=['service_city', 'installer_name', 'year_month'], how="left")
# df_ts = df_ts.merge(df_count_comp, left_on=['service_city', 'installer_name', 'year_month'], right_index=True)

df_ts = pd.concat([df_ts, df_count_comp], axis=1)

df_ts = df_ts.reset_index()
df_ts = df_ts.rename(columns={'level_2': 'year_month'})


# fill in empty rows
df_ts['size_dc'] = df_ts['size_dc'].fillna(0)
df_ts['battery_storage'] = df_ts['battery_storage'].fillna(0)
df_ts['total_cost'] = df_ts['total_cost'].fillna(0)
df_ts['days_to_completion'] = df_ts['days_to_completion'].fillna(0)
df_ts['adjusted_price'] = df_ts['adjusted_price'].fillna(0)
# df_ts['days_to_completion'] = df_ts['days_to_completion'].fillna(0)
df_ts['is_largest_firm'] = df_ts['is_largest_firm'].fillna(0)
df_ts['app_received'] = df_ts['app_received'].fillna(0)
df_ts['app_complete'] = df_ts['app_complete'].fillna(0)
# set queue to zero for all. build queue later.
df_ts.loc[:,'queue'] = 0


df_ts.reset_index()
df_ts.to_csv('./data/aggregate_by_city_installer_ts.csv')

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


# print(avg_cost_adjusted[avg_cost_adjusted['adjusted_price'] < 0])
# plt.scatter(avg_cost_adjusted['year_month'], avg_cost_adjusted['adjusted_price'])
# plt.suptitle("Average Adjusted Cost by month, city, installer")
# plt.show()
