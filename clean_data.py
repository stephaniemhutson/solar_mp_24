import pandas as pd
import numpy as np

import const

def truncate(df):
    # Limiting to Photovoltaic and Photovoltaic with Battery - there are about 10 rows of other
    # Photovoltaic in the 5 year data pulled Aug 28 2024, but these seem irregular enoguh that
    # they should not be included.
    df = df[df['Technology Type'].isin(["Photovoltaic", "Photovoltaic, Battery Energy Storage"])]

    # Third party ownership is a different animal and pricing is weird
    df = df[df['Third Party Owned'] == "No"]

    df = df[df['NEM Tariff'].isin([2, 'NBT'])]
    # There are rows that have a total system cost as zero, blank or 1. They also seem to be
    # correlated with other strange features, and should be removed
    df = df[df['Total System Cost'].notnull()]
    df = df[df['Total System Cost'] > 10]
    df = df[df['Service Zip'].notnull()]
    return df

def clean(df):
    df = df[[
        'Application Id',
        'Preceding Id',
        'Service City',
        'Service County',
        'Service Zip',
        'System Size DC',
        'System Size AC',
        'Storage Capacity (kWh)',
        'Mounting Method',
        'Tracking',
        'App Received Date',
        'App Complete Date',
        'App Approved Date',
        'Self Installer',
        'Installer Name',
        'Installer City',
        'CSLB Number',
        'System Output Monitoring',
        'Total System Cost',
        'Cost/Watt',
        'NEM Tariff',
        'Technology Type',
        'Electric Vehicle',
        'Generator Manufacturer 1',
    ]]

    rename = {
        'Application Id': 'app_id',
        'Preceding Id': 'pre_id',
        'Service City': 'service_city',
        'Service County': 'service_county',
        'Service Zip': 'service_zip',
        'System Size DC': 'size_dc',
        'System Size AC': 'size_ac',
        'Storage Capacity (kWh)': 'battery_storage',
        'Mounting Method': 'mounting_method',
        'Tracking': 'tracking',
        'App Received Date': 'app_received',
        'App Complete Date': 'app_complete',
        'App Approved Date': 'app_approved',
        'Self Installer': 'self_install',
        'Installer Name': 'installer_name',
        'Installer City': 'installer_city',
        'CSLB Number': 'cslb_num',
        'System Output Monitoring': 'output_monitoring',
        'Total System Cost': 'total_cost',
        'Cost/Watt': 'cost_per_watt',
        'NEM Tariff': 'NEM_tariff',
        'Technology Type': 'technology_type',
        'Electric Vehicle': 'electric_vehicle',
        'Generator Manufacturer 1': 'manufacturer',
    }

    df.rename(columns=rename, inplace=True)
    # df = pd.read_csv('./data/applications_cleaned.csv')
    df['service_city'] = df['service_city'].str.lower()
    df['tracking'] = df['tracking'].str.lower()
    df['installer_name'] = df['installer_name'].str.lower()
    df['installer_city'] = df['installer_city'].str.lower()
    df['installer_city'] = df['installer_city'].str.lower()
    df['manufacturer'] = df['manufacturer'].str.lower()
    ## you DEFINITELY need to go through an clean these. There are a lot of variations on the same manufacturer ##
    ## eg. Canadian Solar and Canadian Solar Inc.


    df['self_install'] = df['self_install'].str.lower() == "yes"
    df['electric_vehicle'] = df['electric_vehicle'].str.lower() == "yes"
    df['output_monitoring'] = df['output_monitoring'].str.lower() == "yes"


    # df['app_received'] = pd.to_datetime(df['app_received']).dt.date
    # df['app_complete'] = pd.to_datetime(df['app_complete']).dt.date
    # df['app_approved'] = pd.to_datetime(df['app_approved']).dt.date


    df = df.astype(
        {
            'app_approved': 'datetime64[ns]',
            'app_complete': 'datetime64[ns]',
            'app_received': 'datetime64[ns]',
            'size_dc': 'float64',
            'size_ac': 'float64',
            'cost_per_watt': 'float64',
            'battery_storage': 'float64',
            'self_install': 'bool',
            'NEM_tariff': 'str',
            'electric_vehicle': 'bool',
            'output_monitoring': 'bool',
            'service_zip': 'str',
            'app_id': 'str',
            'pre_id': 'str',
        })

    df['days_to_completion'] = (df['app_approved'] - df['app_received']).dt.days
    df['battery_storage'] = df['battery_storage'].fillna(0)
    # df['NEM_tariff'] = df['NEM_tariff'].astype(str)

    # Application after Dec 15 2022 and still NEM 2.0 (don't make assumptions about how leniant the uilities were)
    anticipation_date = pd.to_datetime('2022-05-09')
    pre_date = pd.to_datetime('2022-12-15')
    post_date = pd.to_datetime('2023-04-14')
    df['is_NEM2'] = df['NEM_tariff'] == '2.0'
    df['after_approval'] = (df['app_received'] > pre_date)
    df.loc[:,'pio_TF'] = (df.loc[:,'after_approval'] & df.loc[:,'is_NEM2'])
    df['year'] = df['app_received'].dt.year
    df['month'] = df['app_received'].dt.month
    df['quarter'] = df['app_received'].dt.quarter
    df['year_month'] = pd.to_datetime(df['app_received'], format='%Y-%m-%d').dt.strftime('%Y-%m')
    df['year_month_comp'] = pd.to_datetime(df['app_complete'], format='%Y-%m-%d').dt.strftime('%Y-%m')

    # df.set_index()

    installer_rev = df.groupby(['service_city', 'quarter', 'year', 'installer_name'])['total_cost'].transform('sum')
    city_rev = df.groupby(['service_city', 'quarter', 'year'])['total_cost'].transform('sum')

    installer_count = df.groupby(['service_city', 'quarter', 'year', 'installer_name'])['total_cost'].transform('count')
    city_count = df.groupby(['service_city', 'quarter', 'year'])['total_cost'].transform('count')

    df['market_share'] = (installer_rev / city_rev)* 100
    df['ms_count'] = (installer_count / city_count)*100

    df['market_share_squared'] = (df['market_share']) ** 2
    df['HHI_city'] = df.groupby(['service_city', 'quarter', 'year'])['market_share_squared'].transform('sum')

    # find the largest firm in the service_city
    df['is_largest_firm'] = df.groupby('service_city')['market_share'].transform(lambda x: x == x.max())

    # There are for instance hundreds of NEM 2.0 projects where the received date is in 2024.
    # Many of these have a preceeding ID that connects them to an application from before the cutoff
    # This late NEM 2 appears to be highly correlated with System monitoring, and seperately the
    # addition of small amounts of wattage.
    df['is_preceeded'] = df['pre_id'].notnull()
    df['after_anticipated_date'] = df['app_received'] > anticipation_date
    df.loc[:, 'anticipation_period'] = (df.loc[:,'after_anticipated_date'] == True) & (df.loc[:,'after_approval'] == False)
    df.loc[:,'has_battery'] = df.loc[:, 'battery_storage'] > 0
    return df

def add_ccci(df):
    ccci = pd.read_csv('./data/CCCI_08_24.csv')

    df = pd.merge(left=df, right=ccci, left_on=['year', 'month'], right_on=['year', 'month'])

    return df

# with pd.read_csv('./data/applications_sdge_5_year.csv', chunksize=800000) as reader:
#     for chunk in reader:
#         sdge = truncate(chunk)

# with pd.read_csv('./data/applications_pge_5_year.csv', chunksize=800000) as reader:
#     for chunk in reader:
#         pge = truncate(chunk)

# with pd.read_csv('./data/applications_sce_5_year.csv', chunksize=800000) as reader:
#     for chunk in reader:
#         sce = truncate(chunk)

# joint = pd.concat([pge, sce, sdge])
# joint.to_csv('./data/truncated_concated_applications.csv')

apps = pd.read_csv('./data/truncated_concated_applications.csv')
apps = clean(apps)
apps.to_csv('./data/temp.csv')
# apps = pd.read_csv('./data/temp.csv')
apps = add_ccci(apps)
apps.to_csv('./data/applications_cleaned.csv')

