import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

import const

# From running NEM2_only from 2021 forward.
# 'total_cost ~ size_dc + battery_storage + pio_TF*days_to_completion + output_monitoring + C(service_county)  + ccci + has_battery'
price_per_kw = 1951.0652
price_battery_fixed = 8375.1875
price_battery_adjust = 2.6158

def run():
    df = pd.read_csv('./data/applications_cleaned.csv')
    df = df.astype(const.TYPE_DICT)
    columns = [
        "app_id",
        "pre_id",
        "service_city",
        "service_county",
        "service_zip",
        "size_dc",
        "battery_storage",
        "mounting_method",
        "tracking",
        "app_received",
        "app_complete",
        "self_install",
        "installer_name",
        "installer_city",
        "cslb_num",
        "output_monitoring",
        "total_cost",
        "cost_per_watt",
        "technology_type",
        "electric_vehicle",
        "manufacturer",
        "days_to_completion",
        "is_NEM2",
        "year_month",
        "market_share",
        "market_share_squared",
        "HHI_city",
        "is_largest_firm",
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


    df["delta_mean_city_month"] = df['mean'] - df['mean_city_month']

    df.loc[:, 'adjusted_price'] = (
        df.loc[:,'total_cost'] - df.loc[:,'battery_storage']*price_battery_adjust - df.loc[:,"has_battery"]*price_battery_fixed
    )/df.loc[:,'ccci']

    df_mean = df.groupby(
        ['service_city', 'installer_name', 'year_month']
    )[
        ['size_dc', 'battery_storage', 'total_cost', 'is_largest_firm', 'days_to_completion', 'adjusted_price']
    ].aggregate('mean')


    df_count = df.groupby(['service_city', 'installer_name', 'year_month'])[['app_received']].aggregate('count')
    df_count_comp = df.groupby(['service_city', 'installer_name', 'year_month_comp'])[['app_complete']].aggregate('count')

    df_ts = df_mean.join(df_count, on=['service_city', 'installer_name', 'year_month'], how="left")

    df_ts = pd.concat([df_ts, df_count_comp], axis=1)

    df_ts = df_ts.reset_index()
    df_ts = df_ts.rename(columns={'level_2': 'year_month'})

    df_ts['simultaneous_markets'] = df_ts.groupby(['installer_name', 'year_month'])['app_received'].transform(lambda x: sum(x > 0))


    # fill in empty rows
    df_ts['size_dc'] = df_ts['size_dc'].fillna(0)
    df_ts['battery_storage'] = df_ts['battery_storage'].fillna(0)
    df_ts['total_cost'] = df_ts['total_cost'].fillna(0)
    df_ts['days_to_completion'] = df_ts['days_to_completion'].fillna(0)
    df_ts['adjusted_price'] = df_ts['adjusted_price'].fillna(0)
    df_ts['is_largest_firm'] = df_ts['is_largest_firm'].fillna(0)
    df_ts['app_received'] = df_ts['app_received'].fillna(0)
    df_ts['app_complete'] = df_ts['app_complete'].fillna(0)
    df_ts['simultaneous_markets'] = df_ts['simultaneous_markets'].fillna(0)

    queue_df = pd.read_csv('./data/queue.csv')

    queue_df = queue_df.astype(const.TYPE_DICT_QUEUE)[['service_city', 'installer_name', 'year_month', 'queue']]
    queue_df.set_index(['service_city', 'installer_name', 'year_month'], inplace=True)

    df_ts.set_index(['service_city', 'installer_name', 'year_month'], inplace=True)
    df_ts = df_ts.join(queue_df)

    df_ts.reset_index()



    df_ts.to_csv('./data/aggregate_by_city_installer_ts.csv')


if __name__ == "__main__":
    run()
