import pandas as pd
import numpy as np

import const

def print_length(df):
    print(len(df))

def truncate(df, third_party=False):
    # Limiting to Photovoltaic and Photovoltaic with Battery - there are about 10 rows of other
    # Photovoltaic in the 5 year data pulled Aug 28 2024, but these seem irregular enoguh that
    # they should not be included.
    df = df[df['Technology Type'].isin(["Photovoltaic", "Photovoltaic, Battery Energy Storage"])]

    # Third party ownership is a different animal and pricing is weird
    if third_party:
        df = df[df['Third Party Owned'] == "Yes"]
    else:
        df = df[df['Third Party Owned'] == "No"]

    df = df[df['NEM Tariff'].isin([2, 'NBT'])]
    # There are rows that have a total system cost as zero, blank or 1. They also seem to be
    # correlated with other strange features, and should be removed
    df = df[df['Total System Cost'].notnull()]
    df = df[df['Total System Cost'] > 0]
    df = df[df['Service Zip'].notnull()]
    df = df[df['Customer Sector'] == "Residential"]
    print_length(df)
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
        'iou'
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
        'Generator Model 1': 'model'
    }

    df.rename(columns=rename, inplace=True)

    def __to_lower(df):
        # df = pd.read_csv('./data/applications_cleaned.csv')
        df['service_city'] = df['service_city'].str.lower()
        df['service_county'] = df['service_county'].str.lower()
        df['tracking'] = df['tracking'].str.lower()
        df['installer_name'] = df['installer_name'].str.lower()
        df['installer_city'] = df['installer_city'].str.lower()
        df['installer_city'] = df['installer_city'].str.lower()
        df['manufacturer'] = df['manufacturer'].str.lower()
        ## you DEFINITELY need to go through an clean these. There are a lot of variations on the same manufacturer ##
        ## eg. Canadian Solar and Canadian Solar Inc.
        return df


    def __yes_to_bool(df):

        print(df[['self_install', 'electric_vehicle', 'output_monitoring']])
        df['self_install'] = df['self_install'].str.lower() == "yes"
        df['electric_vehicle'] = df['electric_vehicle'].str.lower() == "yes"
        df['output_monitoring'] = df['output_monitoring'].str.lower() == "yes"
        df['is_preceeded'] = df['pre_id'].notnull()
        df['battery_storage'] = df['battery_storage'].fillna(0)
        df.loc[:,'has_battery'] = df.loc[:, 'battery_storage'] > 0
        return df

    # df['app_received'] = pd.to_datetime(df['app_received']).dt.date
    # df['app_complete'] = pd.to_datetime(df['app_complete']).dt.date
    # df['app_approved'] = pd.to_datetime(df['app_approved']).dt.dater

    def __dates_fields(df):
        df['days_to_completion'] = (df['app_approved'] - df['app_received']).dt.days
        df['dt_appoval'] = (df['app_approved'] - df['app_complete']).dt.days
        # Application after Dec 15 2022 and still NEM 2.0 (don't make assumptions about how leniant the uilities were)
        anticipation_date = pd.to_datetime('2022-05-09')
        pre_date = pd.to_datetime('2022-12-15')
        post_date = pd.to_datetime('2023-04-14')
        df['after_approval'] = (df['app_received'] > pre_date)
        df['year'] = df['app_received'].dt.year
        df['month'] = df['app_received'].dt.month
        df['quarter'] = df['app_received'].dt.quarter
        df['year_month'] = pd.to_datetime(df['app_received'], format='%Y-%m-%d').dt.strftime('%Y-%m')
        df['year_month_comp'] = pd.to_datetime(df['app_complete'], format='%Y-%m-%d').dt.strftime('%Y-%m')
        df['year_month_approved'] = pd.to_datetime(df['app_approved'], format='%Y-%m-%d').dt.strftime('%Y-%m')
        # There are for instance hundreds of NEM 2.0 projects where the received date is in 2024.
        # Many of these have a preceeding ID that connects them to an application from before the cutoff
        # This late NEM 2 appears to be highly correlated with System monitoring, and seperately the
        # addition of small amounts of wattage.
        df['is_NEM2'] = df['NEM_tariff'] == '2.0'
        df.loc[:,'pio_TF'] = (df.loc[:,'after_approval'] & df.loc[:,'is_NEM2'])
        df['after_anticipated_date'] = df['app_received'] > anticipation_date
        df.loc[:, 'anticipation_period'] = (df.loc[:,'after_anticipated_date'] == True) & (df.loc[:,'after_approval'] == False)
        return df




    def __market_info(df):
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

    # add entered/exit dates

    def __lic_info(df):
        df['cslb_num'] = df['cslb_num'].astype(str)
        df = add_entered_exit(df) # takes a few minutes


        license = pd.read_csv('./data/MasterLicenseData.csv')
        license['LicenseNumber'] = license['LicenseNumber'].astype(str)
        license = license.rename(columns={
            'LicenseNumber': 'cslb_num',
            'IssueDate': 'lic_issue_date',
            'ExpirationDate': 'lic_exp_date',
            'BusinessType': 'business_type',
            'Classifications(s)': 'licenses'
        })

        license['lic_issue_date'] = pd.to_datetime(license['lic_issue_date'], format='%m/%d/%y')
        license['lic_exp_date'] = pd.to_datetime(license['lic_exp_date'], format='%m/%d/%y')
        license = license[['cslb_num', 'lic_issue_date', 'lic_exp_date', 'business_type', 'licenses']]
        df = pd.merge(df, license, how='left', on='cslb_num')
        df = df.fillna({'business_type': 'Unknown'})
        df['licenses'] = df['licenses'].fillna("")
        df['num_lic'] = df.licenses.str.split('|', expand=False).apply(len)
        df.loc[df['licenses'] == "", "num_lic"] = 0
        return df


    df = __to_lower(df)
    print_length(df)
    print("__to_lower")
    df = __yes_to_bool(df)
    print_length(df)
    print("__yes_to_bool")
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
    df = __dates_fields(df)
    print_length(df)
    print("__dates_fields")
    # df = __market_info(df)
    df = __lic_info(df)
    print_length(df)
    print("__lic_info")

    df = add_population(df)
    print_length(df)
    print("added population")
    df = add_ccci(df)
    print_length(df)
    print("added ccci")
    # add population

    # add FIFO score
    df = firm_county_FIFO_score(df)
    print_length(df)
    print("firm_county_FIFO_score")
    df = county_FIFO_score(df)
    print_length(df)
    print("county_FIFO_score")
    df = firm_county_FIFO_score_backwards(df)
    print_length(df)
    print("firm_county_FIFO_score_backwards")
    df = county_FIFO_score_backwards(df)
    print_length(df)
    print("county_FIFO_score_backwards")

    # df['tc_log'] = np.log(df['tc_2022'])

    # add firm country fixed effects
    firm_county_fe = df.groupby(['cslb_num', 'service_county'])['tc_log'].mean()
    firm_county_fe = firm_county_fe.reset_index().rename(columns={'tc_log': 'firm_county_fe'})
    df = pd.merge(df, firm_county_fe, how='left', on=['cslb_num', 'service_county'])
    df['tc_log__fc_fe'] = df['tc_log'] - df['firm_county_fe']
    print_length(df)
    print("firm county fixed effects")
    # add county fixed effects
    county_fe = df.groupby(['service_county'])['tc_log'].mean()
    county_fe = county_fe.reset_index().rename(columns={'tc_log': 'county_fe'})
    df = pd.merge(df, county_fe, how='left', on=['service_county'])
    df['tc_log__c_fe'] = df['tc_log'] - df['county_fe']
    print_length(df)
    print("county fixed effects")
    # add firm fixed effects
    firm_fe = df.groupby('cslb_num')['tc_log'].mean()
    firm_fe = firm_fe.reset_index().rename(columns={'tc_log': 'firm_fe'})
    df = pd.merge(df, firm_fe, how='left', on=['cslb_num'])
    df['tc_log__f_fe'] = df['tc_log'] - df['firm_fe']
    print_length(df)
    print("firm fixed effects")

    print_length(df)
    df = __firm_entry_data(df)
    print_length(df)
    print("Firm Age bins")
    print("Made it to the end")

    return df

def add_ccci(df):
    ccci = pd.read_csv('./data/CCCI_03_25.csv')
    cpi = pd.read_csv('./data/BLS_CPIU_04_2025.csv')
    cpi = pd.read_csv('./data/CPIAUCSL.csv')
    cpi = cpi.astype({'observation_date': 'datetime64[ns]'})
    cpi['year'] = cpi['observation_date'].dt.year

    cpi['month'] = cpi['observation_date'].dt.month
    may_2022 = cpi[(cpi['month'] == 5) & (cpi['year'] == 2022)]['CPIAUCSL'].values[0]
    cpi['CPI_5_22'] = cpi['CPIAUCSL'] / may_2022


    df = pd.merge(left=df, right=ccci, left_on=['year', 'month'], right_on=['year', 'month'])
    df = pd.merge(left=df, right=cpi, left_on=['year', 'month'], right_on=['year', 'month'])
    df['ccci_cpi'] = df['ccci']/df['CPI_5_22']
    df['tc_2022'] = df['total_cost']/df['CPI_5_22']
    df['tc_log'] = np.log(df['tc_2022'])
    return df

def add_entered_exit(df):
    df = df.copy()
    df['cslb_num'] = df['cslb_num'].astype(str)
    df['county_lic'] = df[['service_county', 'cslb_num']].agg('-'.join, axis=1)

    print("Add num apps complete")
    df = df.sort_values(['county_lic','app_approved'])
    df['nth_complete__county'] = df.groupby('county_lic')['app_approved'].rank(method='min')
    df['nth_complete__state'] = df.groupby('cslb_num')['app_approved'].rank(method='min')
    # df['nth_complete__county_under_tariff'] = df.groupby(['county_lic', 'NEM_tariff'])['app_approved'].rank(method='min')
    # df['nth_complete__state_under_tariff'] = df.groupby(['cslb_num', 'NEM_tariff'])['app_approved'].rank(method='min')
    df['log_nth_complete__county'] = np.log(df['nth_complete__county'])
    df['log_nth_complete__state'] = np.log(df['nth_complete__state'])

    def __exits_and_entrances(df, county):
        total_complete = df.groupby('county_lic' if county else 'cslb_num')[f'nth_complete__{"county" if county else "state"}'].max().reset_index()
        total_complete = total_complete.rename(columns={f'nth_complete__{"county" if county else "state"}': 'total_complete'})


        df = pd.merge(df, total_complete, on='county_lic' if county else 'cslb_num', how='left')
        return df

    df = __exits_and_entrances(df, True)
    df = __exits_and_entrances(df, False)
    # print(df[['exits_under_50_installs__county', 'exits_under_50_installs__state', 'immediate_NBT_exit__county', 'immediate_NBT_exit__state']])
    # With Business Licenses
    groups = df[['app_id', 'county_lic', 'app_received', 'app_approved', 'installer_name', 'cslb_num']].groupby('county_lic')

    print("Adding firm entry exit by county lic")
    new_df = pd.DataFrame(columns=['app_id', 'county_lic', 'app_received', 'app_approved', 'installer_name', 'firm_enter_date', 'firm_exit_date', 'firm_identifier'])
    dfs = [new_df]
    for _, group in groups:
        lic_num = group['county_lic'].values[0]

        if lic_num[-3:] == "nan" or lic_num[-4:] == "-0.0":
            enter = None
            exit = None
        else:
            enter = group['app_received'].values.min()
            exit = group['app_approved'].values.max()

        group['firm_enter_date'] = enter
        group['firm_exit_date'] = exit
        group['firm_identifier'] = lic_num
        dfs.append(group)
    new_df = pd.concat(dfs)

    no_lic_groups = new_df[new_df['firm_enter_date'].isna()][['app_id', 'county_lic', 'app_received', 'app_approved', 'installer_name', 'cslb_num']].groupby(['county_lic', 'installer_name'])
    new_df = new_df[new_df['firm_enter_date'].notnull()]
    print("Adding firm entry exit by county installer")
    dfs = [new_df]
    for _, group in no_lic_groups:
        county = group['county_lic'].values[0].split("-")[0]
        # print(county)
        enter = group['app_received'].values.min()
        exit = group['app_approved'].values.max()
        group['firm_enter_date'] = enter
        group['firm_exit_date'] = exit
        group['firm_identifier'] = f"{county}_{group['installer_name']}"
        dfs.append(group)
    new_df = pd.concat(dfs)



    # df = pd.merge(df, new_df, how='left', on=['app_id', 'county_lic', 'app_received', 'app_approved'])


    # # Remaining with installer name
    # groups = df[df['firm_enter_date'].isna()][['app_id', 'installer_name', 'app_received', 'county_lic', 'app_approved', 'cslb_num']].groupby('installer_name')
    # # new_df = pd.DataFrame(columns=['app_id', 'installer_name', 'app_received', 'app_approved', 'firm_enter_date', 'firm_exit_date'])
    # for _, group in groups:
    #     enter = group['app_received'].values.min()
    #     exit = group['app_approved'].values.max()

    #     group['firm_enter_date'] = enter
    #     group['firm_exit_date'] = exit
    #     group['firm_identifier'] = group['installer_name']

    #     new_df = pd.concat([new_df, group])

    df = pd.merge(df, new_df, how='left', on=['app_id', 'installer_name', 'app_received', 'app_approved', 'cslb_num'])
    print("Enter Exit Date County")
    print(len(df))
    # print(new_df)
    # print(df[{'cslb_num', 'firm_enter_date'}])
    entered_date_state = df.groupby('firm_identifier')['firm_enter_date'].min().reset_index().rename(columns={'firm_enter_date': 'entered_state_date'})
    exit_date_state = df.groupby('firm_identifier')['firm_exit_date'].max().reset_index().rename(columns={'firm_exit_date': 'exit_state_date'})
    # print(exit_date_state[['cslb_num', 'entered_state_date']])
    df = pd.merge(df, entered_date_state, how='left', on='firm_identifier')
    df = pd.merge(df, exit_date_state, how='left', on='firm_identifier')
    print("Enter Exit Date County")
    print(len(df))
    return df


def firm_county_FIFO_score(df):
    df = df.copy()
    df['cslb_num'] = df['cslb_num'].astype(str)
    df['county_lic'] = df[['service_county', 'cslb_num']].agg('-'.join, axis=1)

    # Sort data for efficient computation
    df = df.sort_values(by=['county_lic', 'app_approved', 'app_received'])

    # Group by 'county_lic' for efficient processing
    groups = df.groupby('county_lic')

    fifo_scores = np.zeros(len(df))

    for _, group in groups:
        app_approved = group['app_approved'].values
        app_received = group['app_received'].values

        # Count total applications approved before each row
        count_total = np.arange(len(group))

        # Given any app that was approved by the time i was approved, how many were received after
        # the time i was received? subtract from the total count.
        count_fifo = count_total-np.array([
            (app_received[:i+1] >= app_received[i]).sum() - 1 for i in range(len(group))
        ])

        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            score = np.where(count_total == 0, 1, count_fifo / count_total)

        fifo_scores[group.index] = score

    df['fifo_score_fc'] = fifo_scores
    return df

def firm_county_FIFO_score_backwards(df):
    df = df.copy()
    df['cslb_num'] = df['cslb_num'].astype(str)
    df['county_lic'] = df[['service_county', 'cslb_num']].agg('-'.join, axis=1)

    # Sort data for efficient computation
    df = df.sort_values(by=['county_lic', 'app_received', 'app_approved'])

    # Group by 'county_lic' for efficient processing
    groups = df.groupby('county_lic')

    fifo_scores = np.zeros(len(df))

    for _, group in groups:
        app_approved = group['app_approved'].values
        app_received = group['app_received'].values

        # Count total applications approved before each row
        count_total = np.arange(len(group))

        # Given the app was recieved before i was received, how many were approved after
        # the time i was approved? subtract from the total count.
        count_fifo = count_total-np.array([
            (app_approved[:i+1] >= app_approved[i]).sum() - 1 for i in range(len(group))
        ])

        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            score = np.where(count_total == 0, 1, count_fifo / count_total)

        fifo_scores[group.index] = score

    df['fifo_score_fc_backwards'] = fifo_scores
    return df

def county_FIFO_score_backwards(df):
    df = df.copy()
    # df['cslb_num'] = df['cslb_num'].astype(str)
    # df['county_lic'] = df[['service_county', 'cslb_num']].agg('-'.join, axis=1)

    # Sort data for efficient computation
    df = df.sort_values(by=['service_county', 'app_received', 'app_approved'])

    # Group by 'county_lic' for efficient processing
    groups = df.groupby('service_county')

    fifo_scores = np.zeros(len(df))

    for _, group in groups:
        app_approved = group['app_approved'].values
        app_received = group['app_received'].values

        # Count total applications approved before each row
        count_total = np.arange(len(group))

        # Given the app was recieved before i was received, how many were approved after
        # the time i was approved? subtract from the total count.
        count_fifo = count_total-np.array([
            (app_approved[:i+1] >= app_approved[i]).sum() - 1 for i in range(len(group))
        ])

        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            score = np.where(count_total == 0, 1, count_fifo / count_total)

        fifo_scores[group.index] = score

    df['fifo_score_c_backwards'] = fifo_scores
    return df



def county_FIFO_score(df):
    df = df.copy()
    # df['cslb_num'] = df['cslb_num'].astype(str)
    # df['county_lic'] = df[['service_county', 'cslb_num']].agg('-'.join, axis=1)

    # Sort data for efficient computation
    df = df.sort_values(by=['service_county', 'app_approved', 'app_received'])

    # Group by 'county_lic' for efficient processing
    groups = df.groupby('county_lic')

    fifo_scores = np.zeros(len(df))

    for _, group in groups:
        app_approved = group['app_approved'].values
        app_received = group['app_received'].values

        # Count total applications approved before each row
        count_total = np.arange(len(group))

        # Count applications received before each row within the approved ones
        count_fifo = np.array([
            (app_received[:i+1] <= app_received[i]).sum() - 1 for i in range(len(group))
        ])

        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            score = np.where(count_total == 0, 1, count_fifo / count_total)

        fifo_scores[group.index] = score

    df['fifo_score_c'] = fifo_scores
    return df

def add_population(df):
    # groups = df.groupby(['service_city', 'year'])['app_id'].count().reset_index().drop_column('app_id')

    city_populations = pd.read_csv('./data/cities_popultion.csv')
    city_populations = city_populations.groupby(['county'])[['pop2020', 'pop2022', 'pop2023', 'pop2024']].sum().reset_index()
    # remove the word " county" from the county name
    city_populations['county'] = city_populations['county'].str[:-7]

    cpop = pd.DataFrame(columns=['service_county', 'pop', 'year'])

    for year in [2020, 2021, 2022, 2023, 2024]:
        use_year = year if year != 2021 else 2020
        pop = pd.DataFrame({'service_county': city_populations['county'], 'pop': city_populations[f'pop{use_year}'], 'year': year})
        cpop = pd.concat([cpop, pop])

    df = pd.merge(df, cpop, how='left', on=['service_county', 'year'])
    return df


def __firm_entry_data(apps):
    apps['firm_enter_date'] = apps['firm_enter_date'].astype('datetime64[ns]')
    apps['firm_exit_date'] = apps['firm_exit_date'].astype('datetime64[ns]')
    apps['found_license'] = apps['num_lic'] > 0
    # apps = apps[apps['is_NEM2'] == True]
    apps['entrant_week'] = apps['firm_enter_date'].dt.strftime("%Y-%W")
    apps['exit_week'] = apps['firm_exit_date'].dt.strftime("%Y-%W")
    apps = apps.sort_values('firm_enter_date')
    apps['months_to_completion'] = apps['days_to_completion'] / 30

    apps['last_two_weeks'] = apps['year_month'] == '2023-04'

    # print(apps[apps['anticipation_period'] == True]['app_received'].dt.strftime("%Y-%W").min())
    # population
    collected_firm_entrants = apps.groupby(['service_county', 'entrant_week', 'pio_TF', 'pop', 'last_two_weeks', 'year',  'anticipation_period'])['cslb_num'].nunique().reset_index()
    # add zeroes:
    copy = collected_firm_entrants.copy()
    new_weeks = []
    for county in copy['service_county'].unique():
        county_weeks = copy[copy['service_county'] == county]
        pio = False
        last_two_weeks = False
        anticipation = False
        for year in [2020, 2021, 2022, 2023, 2024]:
            for week in range(52):
                if year == 2022 and week == 19:
                    anticipation = True
                if week == 50 and year == 2022:
                    pio = True
                    anticipation = False
                if pio is True and week == 13:
                    last_two_weeks = True
                year_week = f"{year}-{week}"
                if len(county_weeks[county_weeks['entrant_week'] == year_week]) == 0:
                    pop = county_weeks[county_weeks['year']== year]['pop'].max()
                    new_weeks .append({'service_county': county, 'entrant_week': week, 'pio_TF':pio, 'pop': pop, 'last_two_weeks': last_two_weeks, 'anticipation_period': anticipation, 'cslb_num': 0})

    collected_firm_entrants = pd.concat([collected_firm_entrants, pd.DataFrame(new_weeks)])
    collected_firm_entrants['count_mils'] = collected_firm_entrants['cslb_num'] / collected_firm_entrants['pop'] * 1000000

    apps['installer_months_age__county'] = ((apps['app_received']-apps['firm_enter_date']).dt.days +1)/30
    # apps = apps[apps['installer_months_age__county'].notnull()]

    print("Age Bins")
    bins = [1, 3, 6, 12, 24]

    old_bin = 0
    for b in bins:
        apps[f'bin_{b}__age_county'] = (apps['installer_months_age__county'].between(old_bin, b, inclusive='left'))
        old_bin = b

    apps['installer_months_age__state'] = ((apps['app_received']-apps['entered_state_date']).dt.days +1)/30
    # apps = apps[apps['installer_months_age__state'].notnull()]

    bins = [1, 3, 6, 12, 24]

    old_bin = 0
    for b in bins:
        apps[f'bin_{b}__age_state'] = (apps['installer_months_age__state'].between(old_bin, b, inclusive='left'))
        old_bin = b

    return apps


def get_data():
    with pd.read_csv('./data/SDGE_Interconnection_Applications_Dataset_2024-12-31.csv', chunksize=8000000) as reader:
        for chunk in reader:
            sdge = truncate(chunk)
            sdge['iou'] = 'sdge'

    with pd.read_csv('./data/SDGE_Interconnection_Applications_Dataset_2025-03-31.csv', chunksize=8000000) as reader:
        for chunk in reader:
            sdge_03 = truncate(chunk)
            sdge_03['iou'] = 'sdge'

    with pd.read_csv('./data/PGE_Interconnection_Applications_Dataset_2024-12-31.csv', chunksize=8000000) as reader:
        for chunk in reader:
            pge = truncate(chunk)
            pge['iou'] = 'pge'

    with pd.read_csv('./data/PGE_Interconnection_Applications_Dataset_2025-03-31.csv', chunksize=8000000) as reader:
        for chunk in reader:
            pge_03 = truncate(chunk)
            pge_03['iou'] = 'pge'

    with pd.read_csv('./data/SCE_Interconnection_Applications_Dataset_2024-12-31.csv', chunksize=8000000) as reader:
        for chunk in reader:
            sce = truncate(chunk)
            sce['iou'] = 'sce'

    with pd.read_csv('./data/SCE_Interconnection_Applications_Dataset_2025-03-31.csv', chunksize=8000000) as reader:
        for chunk in reader:
            sce_03 = truncate(chunk)
            sce_03['iou'] = 'sce'

    # joint = pd.concat([pge, sce, sdge])
    joint = pd.concat([pge, sce, sdge, pge_03, sce_03, sdge_03])
    joint = joint.drop_duplicates(['Application Id'], keep='last')
    print("Concatinating")
    joint.to_csv('./data/truncated_concated_applications.csv')

# get_data()

apps = pd.read_csv('./data/truncated_concated_applications.csv')
apps = clean(apps)


# print(apps.groupby('iou')['year_month'].min())
# apps.to_csv('./data/temp.csv')
# apps = pd.read_csv('./data/temp.csv')

# apps = add_entered_exit(apps)
# print(apps[apps['pop'].isna()].groupby(['year', 'service_county'])['pop'].max())

paid = apps[apps['self_install'] == False]
paid.to_csv('./data/applications_cleaned_12_24.csv')

self_installed = apps[apps['self_install'] == True]
self_installed.to_csv('./data/self_installed_cleaned_12_24.csv')






