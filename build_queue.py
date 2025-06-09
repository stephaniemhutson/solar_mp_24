import pandas as pd
import warnings

import const


DATES_RAW = [
    '2021-01', '2021-02', '2021-03', '2021-04', '2021-05', '2021-06', '2021-07', '2021-08', '2021-09', '2021-10', '2021-11', '2021-12',
    '2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-06', '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2022-12',
    '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2023-12',
    '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
]


def run(df_ts, save=False):

    # aggreate!
    df_ts_copy = df_ts.copy()
    df_ts_copy = df_ts_copy.reset_index()

    df_ts.set_index(['service_city', 'cslb_num', 'year_month'], inplace=True)

    cities = df_ts_copy['service_city'].unique()

    dates = pd.DataFrame({'date': [pd.to_datetime(date) for date in DATES_RAW]})

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
        'cslb_num',
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
        installers = city_df['cslb_num'].unique()

        for installer in installers:
            installer_df = city_df[city_df['cslb_num'] == installer]
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
                    row['cslb_num'] = installer
                    row['service_city'] = city

                if last:
                    row['queue'] = max(last_row['queue'] + row['app_received'] - row['app_complete'], 0)
                else:
                    row['queue'] = max(row['app_received'] - row['app_complete'], 0)
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


def run_non_aggreagate():
    # TODO: finish making the queue for individual installers in an individual county

    apps = pd.read_csv('./data/applications_cleaned.csv')

    apps = apps.astype(const.TYPE_DICT)
    apps_copy = apps.copy()
    apps_copy = apps_copy.reset_index()

    apps_copy = apps_copy[apps_copy['year_month'] >= '2021-01']
    apps_copy = apps_copy[apps_copy['year_month'] <= '2024-06']

    COLUMNS = columns=[
        'app_received',
        'app_complete',
        'cslb_num',
        'service_city',
        'service_county',
        'app_id'
    ]
    DEFAULT_ROW = {
        'queue_county': 0,
        'entered_date': None,
        'exit_date': None,
        'count_received': 0,
        'count_complete': 0
    }
    # apps_copy = apps_copy[COLUMNS]

    # cities = apps_copy['service_city'].unique()

    apps = apps[COLUMNS]

    apps.reset_index()
    app_agg_rec = apps.groupby(['service_county', 'app_received', 'cslb_num'])[['app_id']].aggregate('count')
    app_agg_comp = apps.groupby(['service_county', 'app_complete', 'cslb_num'])[['app_id']].aggregate('count')
    app_agg_comp = app_agg_comp.rename(columns={'app_id': 'count_complete'})
    app_agg_rec = app_agg_rec.rename(columns={'app_id': 'count_received'})



    app_agg = app_agg_rec.join(app_agg_comp, on=['service_county', 'app_received', 'cslb_num'], how="left")
    app_agg['count_received'] = app_agg['count_received'].fillna(0)
    app_agg['count_complete'] = app_agg['count_complete'].fillna(0)
    apps_copy = app_agg.copy()

    apps_copy = apps_copy.reset_index()

    DAYS = pd.date_range(start='2021-01-01', end='2024-06-30', freq='D').to_list()

    new_df = pd.DataFrame(columns=['service_county', 'cslb_num', 'date'] + list(DEFAULT_ROW.keys()))
    # new_df = new_df.astype(const.TYPE_DICT_QUEUE_COUNTY)
    new_df.to_csv('./data/queue_county.csv', index=False)
    counties = apps_copy['service_county'].unique()
    for county in counties:
        county_df = apps_copy[apps_copy['service_county'] == county]
        installers = county_df['cslb_num'].unique()
        for installer in installers:
            installer_df = county_df[county_df['cslb_num'] == installer]
            entered_date = installer_df['app_received'].aggregate('min')
            exit_date = installer_df['app_received'].aggregate('max')
            installer_df.set_index('app_received', inplace=True)
            installer_dict = installer_df.to_dict('index')
            last_row = None
            for date in DAYS:
                add=False
                row = installer_dict.get(date)

                if row is None:
                    row = {k:v for k,v in DEFAULT_ROW.items()}
                    row['cslb_num'] = installer
                    row['service_county'] = county

                else:
                    add=True

                if last_row:
                    row['queue_county'] = max(last_row['queue_county'] + row['count_received'] - row['count_complete'], 0)
                else:
                    row['queue_county'] = max(row['count_received'] - row['count_complete'], 0)
                row['date'] = date
                row['entered_date'] = entered_date
                row['exit_date'] = exit_date

                last_row = {k:v for k,v in row.items()}
                if add:
                    installer_dict[date] = row

            installer_df = pd.DataFrame(installer_dict.values())
            new_df = pd.concat([new_df, installer_df], ignore_index=True)
            new_df = new_df[new_df['date'].notnull()]
        print(county)
        new_df.to_csv('./data/queue_county.csv', mode='a', index=False, header=False)


            # installer_df = installer_df.sort_values(['app_received'])
            # installer_projects = installer_df.to_dict('records')
            # queue = 0
            # date = pd.to_datetime('2000-01-01')
            # completed_dates












if __name__ == "__main__":

    # df_ts = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
    # df_ts['queue'] = df_ts['queue'].fillna(0)
    # df_ts = df_ts.astype(const.TYPE_DICT_AGG)

    # run(df_ts)
    run_non_aggreagate()
