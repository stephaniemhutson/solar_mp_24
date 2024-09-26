import pandas as pd
import matplotlib.pyplot as plt
import const

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

# print((apps[apps['is_largest_firm'] == True][['installer_name', 'service_city']]))
# print(apps['service_city'].nunique())

