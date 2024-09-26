import pandas as pd
import warnings

import const


warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# service_city,installer_name,year_month

df_ts = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
df_ts = df_ts.astype(const.TYPE_DICT_AGG)

df_ts_copy = df_ts.copy()
df_ts_copy = df_ts_copy.reset_index()

df_ts.set_index(['service_city', 'installer_name', 'year_month'], inplace=True)

cities = df_ts_copy['service_city'].unique()

dates_raw = [
    # '2021-01',
    '2021-02', '2021-03', '2021-04', '2021-05', '2021-06', '2021-07', '2021-08', '2021-09', '2021-10', '2021-11', '2021-12',
    '2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-06', '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2022-12',
    '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2023-12',
    '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', #'2024-06', '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
]
dates = pd.DataFrame({'date': [pd.to_datetime(date) for date in dates_raw]})

DEFAULT_ROW = {
    'size_dc': 0,
    'battery_storage': 0,
    'total_cost': 0,
    'days_to_completion': 0,
    'adjusted_price': 0,
    'is_largest_firm': 0,
    'app_received': 0,
    'app_complete': 0,
    'queue': 0
}



def get_row(df, city, date, installer):
    try:
        row = df.loc[(city, installer, date )]
        # print(row)
        # return
    except KeyError as e:
        # new_row = pd.DataFrame([DEFAULT_ROW], index=[(city, installer, date)])
        # df = pd.concat([df, new_row])

        df.loc[(city, installer, date)] = DEFAULT_ROW

        # print(df)
        row = df.loc[(city, installer, date )]
    return row

with open('./data/cities_done.txt', 'r') as f:
    cities_done = f.read()
    f.close()

cities_done = set(cities_done.split('\n'))
for city in cities:
    if city not in cities_done:
        city_df = df_ts_copy[df_ts_copy['service_city'] == city]
        installers = city_df['installer_name'].unique()
        last = None

        for date in dates['date']:
            # print(date)
            if not last:
                # in the first month we leave the queue at 0.
                last = pd.to_datetime('2021-01')

            for installer in installers:
                row = get_row(df_ts, city, date, installer)
                last_row = get_row(df_ts, city, last, installer)

                df_ts.loc[(city, installer, date), 'queue'] = max(last_row['queue'] + row['app_received'] - row['app_complete'], 0)
            last = date
        with open('./data/cities_done.txt', 'a') as f:
            f.write(f'{city}\n')
            f.close()

        print(f"Saving queue data for {city}")
        df_ts.to_csv('./data/aggregate_by_city_installer_ts.csv')
