import pandas as pd
import warnings

import const


def run(df_ts, save=False):
    df_ts_copy = df_ts.copy()
    df_ts_copy = df_ts_copy.reset_index()

    df_ts.set_index(['service_city', 'installer_name', 'year_month'], inplace=True)

    cities = df_ts_copy['service_city'].unique()

    dates_raw = [
        '2021-01', '2021-02', '2021-03', '2021-04', '2021-05', '2021-06', '2021-07', '2021-08', '2021-09', '2021-10', '2021-11', '2021-12',
        '2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-06', '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2022-12',
        '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2023-12',
        '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', #'2024-06', '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
    ]
    dates = pd.DataFrame({'date': [pd.to_datetime(date) for date in dates_raw]})

    DEFAULT_ROW = {
        'app_received': 0,
        'app_complete': 0,
        'queue': 0,
        'entered_date': None,
        'exit_date': None,
        'active_sales_months': 0,
        'count_sales': 0,
    }

    COLUMNS = columns=[
        'app_received',
        'app_complete',
        'queue',
        'installer_name',
        'service_city',
        'year_month',
    ]

    new_df = pd.DataFrame(columns=const.TYPE_DICT_QUEUE.keys())

    df_ts_copy = df_ts_copy[COLUMNS]
    df_ts_copy = df_ts_copy[df_ts_copy['year_month'] >= '2021-01']
    df_ts_copy = df_ts_copy[df_ts_copy['year_month'] <= '2024-06']

    new_df = new_df.astype(const.TYPE_DICT_QUEUE)
    new_df.to_csv('./data/queue.csv', index=False)

    for city in cities:
        new_df = pd.DataFrame(columns=const.TYPE_DICT_QUEUE.keys())
        new_df = new_df.astype(const.TYPE_DICT_QUEUE)
        city_df = df_ts_copy[df_ts_copy['service_city'] == city]
        installers = city_df['installer_name'].unique()

        for installer in installers:
            installer_df = city_df[city_df['installer_name'] == installer]
            entered_date = installer_df['year_month'].aggregate('min')
            exit_date = installer_df['year_month'].aggregate('max')
            active_sales_months = installer_df[installer_df['app_received'] >0]['app_received'].aggregate('count')
            count_sales = installer_df['app_received'].sum()

            installer_df.set_index('year_month', inplace=True)
            installer_dict = installer_df.to_dict('index')

            last = None
            for date in dates['date']:
                add=False
                row = installer_dict.get(date)
                if row is None:
                    row = {k:v for k,v in DEFAULT_ROW.items()}
                    row['installer_name'] = installer
                    row['service_city'] = city

                if last:
                    row['queue'] = max(last_row['queue'] + row['app_received'] - row['app_complete'], 0)
                row['year_month'] = date
                row['entered_date'] = entered_date
                row['exit_date'] = exit_date
                row['active_sales_months'] = max(active_sales_months, 0)
                row['count_sales'] = count_sales

                last = date
                last_row = row
                installer_dict[date] = row

            installer_df = pd.DataFrame(installer_dict.values())
            new_df = pd.concat([new_df, installer_df], ignore_index=True)
            new_df = new_df[new_df['year_month'].notnull()]
        print(city)
        new_df.to_csv('./data/queue.csv', mode='a', index=False, header=False)



if __name__ == "__main__":

    df_ts = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
    df_ts = df_ts.astype(const.TYPE_DICT_AGG)

    run(df_ts)
