import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt
import collections

import pyfixest as pf

import const

def print_length(df):
    print(len(df))

def check_for_correlations(apps):
    df_encoded = pd.get_dummies(apps[['total_cost','size_dc', 'electric_vehicle', 'pio_TF', 'output_monitoring', 'mounting_method', 'service_county', 'days_to_completion']], drop_first=True)
    correlation_matrix = df_encoded.corr()

    threshold = 0.1
    high_corr_pairs = np.where(np.abs(correlation_matrix) > threshold)

    # Extract the pairs
    high_corr_indices = [(correlation_matrix.index[x], correlation_matrix.columns[y]) for x, y in zip(*high_corr_pairs) if x != y and x < y]

    # Display the results
    print(f"\nPairs with correlation greater than {threshold}:")
    for var1, var2 in high_corr_indices:
        print(f"{var1} and {var2}: {correlation_matrix.loc[var1, var2]}")

def get_data(is_nem2=True, self_install=False):
    if self_install:
        apps = pd.read_csv('./data/self_installed_cleaned_12_24.csv')
    else:
        apps = pd.read_csv('./data/applications_cleaned_12_24.csv')
    # San Joaquin appears to be causing colliniarities - my guess is there just aren't any or many
    # installations in the county.
    print_length(apps)
    # apps = apps[apps['service_county'] != "San Joaquin"]
    # apps = apps[apps['service_county'] != "Yuba"]
    apps = apps[apps['mounting_method'] == "Rooftop"]
    apps = apps.drop_duplicates(['app_id'], keep='last')
    # apps = apps[apps['iou'] != 'sdge']

    apps = apps[apps['app_complete'].notnull()]
    print_length(apps)

    apps = apps.astype(const.TYPE_DICT)
    apps['month'] = (apps['app_received'].dt.year - 2020)*12 + (apps['app_received'].dt.month -1)
    # Limit received to just 2022 - this way we don't have
    apps = apps[apps['app_received'] >= pd.to_datetime('2021-01-01')]
    # apps = apps[apps['self_install'] == False]
    apps = apps[apps['size_dc'] >= 1]
    apps = apps[apps['size_dc'] <= 12]
    apps = apps[apps['total_cost'] <= 500000]
    apps = apps[apps['total_cost'] >= 1000]
    if is_nem2:
        apps = apps[apps['is_NEM2']== True]

    print("size and cost reduction")
    print_length(apps)

    apps = apps[apps['is_preceeded'] == False]
    apps = apps[apps['app_complete'] >= pd.to_datetime('2021-01-01')]
    print("app not preceded, 2021 or later")
    print_length(apps)
    apps['survived_one_year'] = apps['firm_exit_date'] >= '2024-04-14'
    return apps

def nem2_and_3():
    apps = get_data()
    model = smf.ols(
        'total_cost ~ size_dc + battery_storage + pio_TF + output_monitoring + C(service_county)  + ccci + is_NEM2 + has_battery' ,
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

    print("Total Size -- no anticipation")
    model = smf.ols(
        'size_dc ~ + electric_vehicle + pio_TF + output_monitoring + is_NEM2 + C(service_county) ',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

def nem2_only():
    apps = get_data()
    # apps = apps[apps['app_received'] >= pd.to_datetime('2021-01-01')]
    apps = apps[apps['NEM_tariff'] == '2.0']
    apps = apps[apps['market_share'].notnull()]


    # Run the regression using statsmodels with fixed effects
    # Using formula interface to make it easy to add fixed effects

    model = smf.ols(
        'tc_log ~ size_dc + battery_storage + anticipation_period+ pio_TF + output_monitoring + C(service_county) + has_battery',
        # 'tc_log__c_fe ~ size_dc + battery_storage + pio_TF + output_monitoring + has_battery',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())
    # model = smf.ols(
    #     # 'total_cost ~ size_dc + battery_storage + pio_TF + output_monitoring + C(service_county)  + ccci + has_battery',
    #     'tc_log ~ size_dc + battery_storage + pio_TF + output_monitoring + C(service_county) + has_battery',
    #     data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    # print(model.summary())

    # print("Total Size -- no anticipation")
    # model = smf.ols(
    #     'size_dc ~ + electric_vehicle + pio_TF + output_monitoring + C(service_county)',
    #     data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    # print(model.summary())

def nem2_only_aniticpation():
    apps = get_data()
    apps = apps[apps['market_share'].notnull()]
    apps = apps[apps['NEM_tariff'] == '2.0']
    # apps['tc_log'] = np.log(apps['total_cost']/apps['CPI'])
    apps['ccci_cpi'] = apps['ccci']/apps['CPI']
    print("Total Cost -- anticipation")
    model = smf.ols(
        # 'total_cost ~ size_dc + battery_storage + pio_TF + output_monitoring + C(service_county) + ccci + has_battery + anticipation_period' ,
        'tc_log ~ size_dc + battery_storage + pio_TF + output_monitoring + C(service_county) + has_battery + ccci_cpi + anticipation_period' ,
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

def year_month():
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    apps = apps[apps['app_received'] >= '2021-01-01']
    apps = apps[apps['app_received'] < '2023-05-01'] # giving some leigh way for late arrivals BUT NOT MUCH
    apps = apps[apps['size_dc'] >= 1]
    apps = apps[apps['size_dc'] <= 12]

    apps['log_ccci'] = np.log(apps['ccci_cpi'] + 0.00001)

    apps['log_tc_ccci'] = apps['tc_log'] - apps['log_ccci']
    print("Total Cost -- year_month")
    model = smf.ols(
        # 'tc_2022 ~ size_dc + battery_storage + output_monitoring + C(service_county) + has_battery + C(year_month) + ccci_cpi' ,
        'tc_log ~ size_dc + C(year_month) + battery_storage + output_monitoring + has_battery + C(service_county)',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    # model_pf = pf.feols(
    #     'tc_log ~ size_dc + battery_storage + output_monitoring + has_battery +C(year_month) + ccci_cpi | service_county' ,
    #     data=apps
    # )
    print(model.summary())

    # model_pf = pf.feols(
    #     'tc_log ~ size_dc + battery_storage + output_monitoring + has_battery +C(year_month) + ccci_cpi ' ,
    #     data=apps
    # )
    # print(model_pf.summary())


    df = pd.read_html(model.summary().tables[1].as_html(),header=0,index_col=0)[0]
    df = df.reset_index()
    df.to_csv('./regressions/year_month_rec_trunc.csv')
    # apps['weeks_to_completion'] = apps['days_to_completion'] / 28
    # print("Total Cost -- year_month DTCxPOI")
    # model = smf.ols(

    #     # 'tc_2022 ~ size_dc + battery_storage + output_monitoring + C(service_county) + has_battery + days_to_completion*C(year_month) + ccci_cpi' ,
    #     'tc_log ~ size_dc + battery_storage + output_monitoring + has_battery + weeks_to_completion*C(year_month) + C(service_county)' ,
    #     data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    # print(model.summary())

    # df1 = pd.read_html(model.summary().tables[1].as_html(),header=0,index_col=0)[0]
    # df1 = df1.reset_index()
    # df1.to_csv('./regressions/year_month_rec_trunc_dtc_x_ym.csv')

    def get_df(file_name):
        df = pd.read_csv(f'./regressions/{file_name}.csv')
        return df

    def show_plot(df, file_name, tablename):
        print(f"Plot: {file_name}")
        df = df[df['index'].str.startswith("C(year_month")]
        df['year_month'] = df['index'].astype('str').str.extract(r'(\d{4}-\d{2})')[0].astype("datetime64[ns]")

        dummy_value = df[df['year_month'] == '2022-05-01']['coef'].values[0]

        df['coef'] -= dummy_value
        df['ci_lower'] = df['[0.025'] - dummy_value
        df['ci_upper'] = df['0.975]'] - dummy_value
        # Plot


        x = df['year_month']
        fig, ax = plt.subplots()
        ax.plot(x, df['coef'])
        ax.fill_between(
            x, df['ci_lower'], df['ci_upper'], color='b', alpha=.15)
        fig.autofmt_xdate(rotation=45)



        # plt.figure(figsize=(10, 6))
        # plt.errorbar(df['year_month'], df['coef'],
                     # yerr=[df['coef'] - df['ci_lower'], df['ci_upper'] - df['coef']],
                     # fmt='o', ecolor='gray', capsize=5, label='Coefficient')

        # Add labels and title
        plt.xlabel('Year-Month')
        plt.ylabel('Percent Change')
        plt.title(tablename)
        # plt.xticks(rotation=45)
        # plt.grid(axis='y')
        plt.axhline(y=0, color='black')
        # plt.tight_layout()
        plt.axvline(x=pd.to_datetime('2022-12-15'))
        plt.axvline(x=pd.to_datetime('2022-05-15'))
        # Show the plot
        plt.savefig(f'./price_{file_name}.png')
        plt.show()

    # df1 = get_df('year_month_rec_trunc')
    show_plot(df, 'year_month_rec_trunc', 'Received Year-Month Coefficients')


def year_month_comp():
    # completed
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    apps = apps[apps['app_complete'] >= '2021-01-01']

    apps = apps[apps['size_dc'] >= 1]
    apps = apps[apps['size_dc'] <= 12]
    # print("Total Cost -- year_month")

    model = smf.ols(
        # 'tc_2022 ~ size_dc + battery_storage + output_monitoring + C(year_month_comp) + C(service_county) + ccci + has_battery' ,
        'tc_log ~ size_dc + battery_storage + output_monitoring + C(year_month_comp) + has_battery + C(service_county)' ,
        # 'tc_log__fc_fe ~ size_dc + battery_storage + output_monitoring + has_battery + fifo_score_c_backwards*C(year_month_comp)' ,
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

    df = pd.read_html(model.summary().tables[1].as_html(),header=0,index_col=0)[0]
    df = df.reset_index()



    df.to_csv('./regressions/year_month_comp.csv')








    # import pdb
    # pdb.set_trace()

    # print("Total Size -- anticipation")
    # model = smf.ols(
    #     'size_dc ~ electric_vehicle + pio_TF + C(service_county) + output_monitoring + anticipation_period',
    #     data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    # print(model.summary())

    # diffs = apps.set_index(['app_id','service_zip').groupby(level='service_zip')\
    #     .transform(lambda x: x.sort_index().diff())\
    #     .reset_index()

    # model = smf.ols(touch
    #     'total_cost ~ size_dc + electric_vehicle + pio_TF + output_monitoring + C(mounting_method) + ccci',
    #     data=diffs
    # ).fit(cov_type='cluster', cov_kwds={'groups': diffs['service_city']})
    # print(model.summary())

    # Days to completion is strongly correlated with pio_TF, if you just ask days to completion, the pio effect goes statistically
    # to zero. If you look at days_to_completion*pio_TF, the effect gets larger. We also see that there is a reasonably
    # strong correlation between days_to_completion and size, which makes sense, a bigger project is likely to
    # have more to do, and therefore will take longer to get done.

    # The reason to beg this question is because I am unsure if there is a higher time to completion due to increased
    # demand if part of the price increase is to cover to risk of lost customers.


    # model = smf.ols(
    #     'total_cost ~ size_dc + electric_vehicle + pio_TF + output_monitoring + C(service_county) + C(mounting_method) + days_to_completion*pio_TF + days_to_completion',
    #     data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    # print(model.summary())



    # What about HHI by county + year?
def hhi():
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    apps['HHI_city'] = apps['HHI_city'] / 10000
    model = smf.ols(
        'tc_log ~ HHI_city + size_dc + battery_storage + has_battery+ output_monitoring + C(service_county)',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())


def market_share():
    apps = get_data()
    apps = apps[apps['market_share'].notnull()]
    apps = apps[apps['NEM_tariff'] == '2.0']
    apps['tc_log'] = np.log(apps['total_cost'])
    model = smf.ols(
        'tc_log ~ size_dc + battery_storage + has_battery + market_share + pio_TF + output_monitoring + ccci  + C(service_county)',
        # 'tc_2022 ~ size_dc + battery_storage + has_battery + market_share + pio_TF + output_monitoring + ccci  + C(service_county)',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())
    model = smf.ols(
        'tc_log ~ size_dc + battery_storage + has_battery + market_share + pio_TF + output_monitoring + ccci  + C(service_county) + anticipation_period',
        # 'tc_2022 ~ size_dc + battery_storage + has_battery + market_share + pio_TF + output_monitoring + ccci  + C(service_county) + anticipation_period',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())


def market_share__count():
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    model = smf.ols(
        'tc_2022 ~ size_dc + battery_storage + ms_count*pio_TF + output_monitoring + days_to_completion+ C(service_county) + ccci',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

def delta_market_share():

    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    firms = apps.groupby(['service_city', 'year', 'quarter', 'installer_name'])[['market_share', 'HHI_city']].aggregate('min')


def ms_and_days_to_comp():
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    # apps = apps[apps['pio_TF'] == True]
    model = smf.ols(
        'days_to_completion ~ ms_count*pio_TF + C(service_county) ',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

def days_to_comp():
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    # apps = apps[apps['pio_TF'] == True]
    apps = apps[apps['app_received'] >= '2022-01-01']
    apps = apps[apps['app_received'] <= '2023-4-14']
    model = smf.ols(
        'days_to_completion ~ pio_TF + C(service_county) ',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

    model = smf.ols(
        'days_to_completion ~ anticipation_period + pio_TF + C(service_county) ',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

def simple_compare_NEM2_3():
    apps = get_data()
    model = smf.ols(
        'total_cost ~ C(NEM_tariff) + size_dc + C(service_county) + battery_storage + ccci + output_monitoring',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

def queue_length():
    agg_apps = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
    agg_apps['queue'] = agg_apps['queue'].fillna(0)
    agg_apps = agg_apps.astype(const.TYPE_DICT_AGG)
    agg_apps = agg_apps[agg_apps['year_month'] >= pd.to_datetime('2021-01')]
    agg_apps = agg_apps[agg_apps['year_month'] <= pd.to_datetime('2023-05')]
    agg_apps = agg_apps[agg_apps['service_county'].notnull()]

    # model = smf.ols(
    #     'total_cost ~ size_dc + C(service_county) + battery_storage + ccci + queue',
    #     data=agg_apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': agg_apps['service_county']})
    def cluster_fit(formula, data, group_var):
        fit = smf.ols(formula, data=data).fit()
        to_keep = pd.RangeIndex(len(data)).difference(pd.Index(fit.model.data.missing_row_idx))
        robust = fit.get_robustcov_results(cov_type='cluster',
                                           groups=data.iloc[to_keep][group_var])
        return robust

    model = cluster_fit('tc_2022 ~ size_dc + C(service_county) + battery_storage + ccci + queue', agg_apps, 'service_county')
    print(model.summary())

    # model = smf.ols(
    #     'total_cost ~ C(NEM_tariff) + size_dc + C(service_county) + battery_storage + ccci + output_monitoring',
    #     data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})


def price_time_to_completion():
    apps = get_data()

    # import pdb
    # pdb.set_trace()
    # apps = apps[apps['app_received'] >= pd.to_datetime('2021-01-01')]
    # apps['tc_log'] = 100*apps['tc_log']
    apps['months_to_completion'] = apps['days_to_completion'] / 30
    apps = apps[apps['is_NEM2'] == True]
    apps = apps[apps['year_month'] <= '2023-05']

    # remove slowest installers based on how fast they were before the poi
    ### THIS DOES BASICALLY NOTHING

    installers_by_speed = apps[~apps['pio_TF']].groupby(['installer_name'])['days_to_completion'].aggregate('mean')
    slowest_installers = installers_by_speed[installers_by_speed > 6*installers_by_speed.std()]
    slowest_installers = slowest_installers.reset_index()

    # remove most expensive installers based on how expensive they were before the poi

    installers_by_price = apps[~apps['pio_TF']].groupby(['installer_name'])['total_cost'].aggregate('mean')
    most_expensive_installers = installers_by_price[installers_by_price > 6*installers_by_price.std()]
    most_expensive_installers = most_expensive_installers.reset_index()


    equipment_by_speed = apps[~apps['pio_TF']].groupby(['manufacturer'])['days_to_completion'].aggregate('mean')
    # slowest_equipment = equipment_by_speed[equipment_by_speed > 6*equipment_by_speed.std()]
    # slowest_equipment = slowest_equipment.reset_index()


    #**** THESE MAKE NO DIFFERENCE ****#
    # apps = apps[~apps['manufacturer'].isin(slowest_equipment['manufacturer'])]
    # apps = apps[~apps['installer_name'].isin(slowest_installers['installer_name'])]
    # apps = apps[~apps['installer_name'].isin(most_expensive_installers['installer_name'])]

    # apps = apps[apps['total_cost'] <= 500000]
    # apps = apps[apps['size_dc'] >= 1]
    # apps = apps[apps['size_dc'] <= 8]

    # agg_apps= pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
    # agg_apps['queue'] = agg_apps['queue'].fillna(0)
    # agg_apps = agg_apps.astype(const.TYPE_DICT_AGG)
    # agg_apps = agg_apps[agg_apps['year_month'] >= pd.to_datetime('2021-01')]
    # agg_apps = agg_apps[agg_apps['year_month'] <= pd.to_datetime('2023-05')]
    # agg_apps = agg_apps[agg_apps['year_month'] <= pd.to_datetime('2023-05')]
    # apps = apps[apps['pio_TF'] == True]
    # apps = apps[apps['app_complete'] <= '2023-04-15']



    # model = smf.ols(
    #     'total_cost ~ C(year_month)*days_to_completion + size_dc + C(service_county) + battery_storage + ccci', data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})

    # print(model.summary())
    # model = smf.ols(
    #     'total_cost ~ C(year_month) + days_to_completion + size_dc + C(service_county) + battery_storage + ccci', data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})

    # print(model.summary())
    obs = []
    print("*******Just days to Completion*******")

    model1 = pf.feols(
        # 'tc_2022 ~ days_to_completion + size_dc + has_battery + C(service_county) + ccci + output_monitoring + battery_storage',
        'tc_log ~ months_to_completion + size_dc + has_battery + output_monitoring + battery_storage | service_county',
        # 'tc_log ~ fifo_score_c_backwards + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        data=apps


    )
    # print(model1.summary())
    obs.append(apps['app_id'].count())
    print("*******DTC + POI*******")
    model2 = pf.feols(
        'tc_log ~ months_to_completion + pio_TF + anticipation_period + size_dc + has_battery + output_monitoring + battery_storage | service_county',
        # 'tc_log ~ fifo_score_c_backwards  + pio_TF + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        # 'tc_2022 ~ days_to_completion + pio_TF + size_dc + has_battery + C(service_county) + output_monitoring + battery_storage',
        data=apps


    )
    # print(model2.summary())
    obs.append(apps['app_id'].count())

    print("*******DTC x POI*******")
    model3 = pf.feols(
        'tc_log ~ months_to_completion*pio_TF + months_to_completion*anticipation_period+ size_dc + has_battery + output_monitoring + battery_storage | service_county',
        # 'tc_log ~ fifo_score_c_backwards*pio_TF + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        # 'tc_2022 ~ days_to_completion*pio_TF + size_dc + has_battery + C(service_county) + output_monitoring + battery_storage',
        data=apps
    )
    # print(model3.summary())
    obs.append(apps['app_id'].count())

    model4 = pf.feols(
        # 'tc_2022 ~ days_to_completion + size_dc + has_battery + C(service_county) + ccci + output_monitoring + battery_storage',
        'tc_log ~ months_to_completion + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        # 'tc_log ~ fifo_score_c_backwards + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        data=apps
    )
    # print(model1.summary())
    obs.append(apps['app_id'].count())
    print("*******DTC + POI*******")
    model5 = pf.feols(
        'tc_log ~ months_to_completion  + pio_TF + anticipation_period + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        # 'tc_log ~ fifo_score_c_backwards  + pio_TF + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        # 'tc_2022 ~ days_to_completion + pio_TF + size_dc + has_battery + C(service_county) + output_monitoring + battery_storage',
        data=apps


    )
    # print(model2.summary())
    obs.append(apps['app_id'].count())

    print("*******DTC x POI*******")
    model6 = pf.feols(
        'tc_log ~ months_to_completion*pio_TF + months_to_completion*anticipation_period+ size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        # 'tc_log ~ fifo_score_c_backwards*pio_TF + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
        # 'tc_2022 ~ days_to_completion*pio_TF + size_dc + has_battery + C(service_county) + output_monitoring + battery_storage',
        data=apps
    )
    # print(model3.summary())
    obs.append(apps['app_id'].count())

    # print("*******DTC _before_ POI*******")
    # apps_pre = apps[apps['app_received'] <= '2022-12-15']
    # apps_anticipation = apps_pre[apps_pre['app_received'] >= '2022-05-15']
    # apps_pre = apps_pre[apps['app_received'] < '2022-05-15']
    # model4 = pf.feols(
    #     'tc_log ~ months_to_completion + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
    #     # 'tc_log ~ fifo_score_c_backwards + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
    #     # 'tc_2022 ~ days_to_completion + size_dc + has_battery + C(service_county) + output_monitoring + battery_storage',
    #     data=apps_pre
    # )
    # # print(model5.summary())

    # # obs.append(apps_pre['app_id'].count())

    # model5 = pf.feols(
    #     'tc_log ~ months_to_completion + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
    #     # 'tc_log ~ fifo_score_c_backwards + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
    #     # 'tc_2022 ~ days_to_completion + size_dc + has_battery + C(service_county) + output_monitoring + battery_storage',
    #     data=apps_anticipation
    # )
    # # print(model5.summary())

    # # obs.append(apps_pre['app_id'].count())

    # print("*******DTC _during_ POI*******")
    # apps_post = apps[apps['app_received'] >= '2022-12-15']
    # model6 = pf.feols(
    #     'tc_log ~ months_to_completion + size_dc + has_battery  + output_monitoring + battery_storage | county_lic',
    #     # 'tc_log ~ fifo_score_c_backwards + size_dc + has_battery + output_monitoring + battery_storage | county_lic',
    #     # 'tc_2022 ~ days_to_completion + size_dc + has_battery + C(service_county) + output_monitoring + battery_storage',
    #     data=apps_post,
    #     vcov = {'CRV1':'service_county'}
    # )
    # # print(dir(model6))
    print(pf.etable(
        [model1, model2, model3, model4, model5, model6],
        type='tex',
        felabels={'county_lic': 'Firm-County', 'service_county': 'county'},
        labels={
            'months_to_completion': 'Months to Completion',
            'pio_TF': 'Treatment',
            'anticipation_period': 'Anticipation',
            'months_to_completion:pio_TF': 'MTC x Treatment',
            'months_to_completion:anticipation_period': 'MTC x Anticipation',
        },
        signif_code=[0.01, 0.05, 0.1],
    ))
    # # print(model4.summary())
    # # obs.append(apps_post['app_id'].count())

    # # fig = plt.figure(figsize=(12,8))

    # # #produce regression plots
    # # fig = sm.graphics.plot_regress_exog(model, 'days_to_completion', fig=fig)
    # # plt.show()


    # model_to_latex(
    #     [model1, model2, model3],
    #     {
    #         'months_to_completion': 'Months to Completion',
    #         'pio_TF': 'Treatment',
    #         'anticipation_period': 'Anticipation',
    #         'months_to_completion:pio_TF': 'MTC x Treatment',
    #         'months_to_completion:anticipation_period': 'MTC x Anticipation',
    #     },
    #     ['(1)', '(2)', '(3)'],
    #     obs
    # )

def business_type():
    apps=get_data()
    apps_pre = apps[apps['app_received'] <= '2022-12-15']
    apps_post = apps[apps['app_received'] >= '2023-04-15']
    apps_dur = apps[apps['app_received'] > '2022-12-15'][apps['app_received'] < '2023-04-15']
    # apps.count_lic = apps.licenses

    # apps.loc[:, 'count_lic'] = len(apps.loc[:, 'licenses'].split("|"))
    print("***All***")
    print(apps.groupby('business_type')['app_id'].count())
    print(apps.groupby(['business_type', 'cslb_num'])['app_id'].max().reset_index().groupby('business_type')['cslb_num'].count())
    print("***Pre***")

    print(apps_pre.groupby('business_type')['app_id'].count())
    print(apps_pre.groupby(['business_type', 'cslb_num'])['app_id'].max().reset_index().groupby('business_type')['cslb_num'].count())
    print("***During***")

    print(apps_dur.groupby('business_type')['app_id'].count())
    print(apps_dur.groupby(['business_type', 'cslb_num'])['app_id'].max().reset_index().groupby('business_type')['cslb_num'].count())
    print("***Post***")

    print(apps_post.groupby('business_type')['app_id'].count())
    print(apps_post.groupby(['business_type', 'cslb_num'])['app_id'].max().reset_index().groupby('business_type')['cslb_num'].count())


    model = smf.ols(
        'tc_log ~ C(business_type)*pio_TF*days_to_completion + size_dc + battery_storage + has_battery+ output_monitoring + C(service_county)',
        data=apps
    ).fit()
    print(model.summary())

    model = smf.ols(
        'fifo_score_c_backwards ~ C(business_type)*pio_TF + size_dc + battery_storage + has_battery+ output_monitoring + C(service_county)',
        data=apps
    ).fit()
    print(model.summary())

def price_num_lic():
    apps=get_data()

    model = smf.ols(
        'tc_log__c_fe ~ num_lic*pio_TF*days_to_completion + size_dc + battery_storage + has_battery+ output_monitoring',
        data=apps
    ).fit()
    print(model.summary())
    # df = pd.read_html(model.summary().tables[1].as_html(),header=0,index_col=0)[0]
    # df = df.reset_index()

    # print("\n\n*********\n\n")
    # print("mean price:")
    # mean = apps['total_cost'].aggregate('mean')
    # print(mean)
    # df.to_csv('./regressions/price_time_to_completion.csv')

    # # report elasticity of time wrt price
    # beta_time = -21.6177

    # apps['estimated_wo_dtc'] = apps['total_cost'] - apps['days_to_completion']*(beta_time)
    # apps['(tc-est/tc)/dtc'] = 30*(apps['total_cost'] - apps['estimated_wo_dtc'])/(apps['total_cost']*apps['days_to_completion'])

    # print(apps['(tc-est/tc)/dtc'].mean())

def fifo_score(fixed_effect):
    apps=get_data()


    print("Looking backward")
    model = pf.feols(
        f'tc_log ~ fifo_score_{fixed_effect}_backwards*pio_TF + anticipation_period*fifo_score_{fixed_effect}_backwards + size_dc + battery_storage + has_battery + output_monitoring | { "county_lic"  if fixed_effect == "fc" else "service_county"}',
        data=apps
    )
    print(model.summary())
    return model, apps['tc_log'].count()


# def corr_firm_size_fifo_score():
#     # Number of projects a firm completes in a county in a month
#     apps = get_data()
#     firm_county_count = apps.groupby(['service_county', 'cslb_num', 'year_month'])['app_id'].count().reset_index()
#     firm_county_count = firm_county_count.rename(columns={'app_id': 'app_received_count'})
#     firm_county_count['over_10'] = firm_county_count['app_received_count']


# def __firm_entry_data(apps):
#     apps['firm_enter_date'] = apps['firm_enter_date'].astype('datetime64[ns]')
#     apps['firm_exit_date'] = apps['firm_exit_date'].astype('datetime64[ns]')
#     apps['found_license'] = apps['num_lic'] > 0
#     apps = apps[apps['is_NEM2'] == True]
#     apps['entrant_week'] = apps['firm_enter_date'].dt.strftime("%Y-%W")
#     apps['exit_week'] = apps['firm_exit_date'].dt.strftime("%Y-%W")
#     apps = apps.sort_values('firm_enter_date')
#     apps['months_to_completion'] = apps['days_to_completion'] / 30

#     apps['last_two_weeks'] = apps['year_month'] == '2023-04'

#     # print(apps[apps['anticipation_period'] == True]['app_received'].dt.strftime("%Y-%W").min())
#     # population
#     collected_firm_entrants = apps.groupby(['service_county', 'entrant_week', 'pio_TF', 'pop', 'last_two_weeks', 'year',  'anticipation_period'])['cslb_num'].nunique().reset_index()
#     # add zeroes:
#     copy = collected_firm_entrants.copy()
#     new_weeks = []
#     for county in copy['service_county'].unique():
#         county_weeks = copy[copy['service_county'] == county]
#         pio = False
#         last_two_weeks = False
#         anticipation = False
#         for year in [2020, 2021, 2022, 2023, 2024]:
#             for week in range(52):
#                 if year == 2022 and week == 19:
#                     anticipation = True
#                 if week == 50 and year == 2022:
#                     pio = True
#                     anticipation = False
#                 if pio is True and week == 13:
#                     last_two_weeks = True
#                 year_week = f"{year}-{week}"
#                 if len(county_weeks[county_weeks['entrant_week'] == year_week]) == 0:
#                     pop = county_weeks[county_weeks['year']== year]['pop'].max()
#                     new_weeks .append({'service_county': county, 'entrant_week': week, 'pio_TF':pio, 'pop': pop, 'last_two_weeks': last_two_weeks, 'anticipation_period': anticipation, 'cslb_num': 0})

#     collected_firm_entrants = pd.concat([collected_firm_entrants, pd.DataFrame(new_weeks)])
#     collected_firm_entrants['count_mils'] = collected_firm_entrants['cslb_num'] / collected_firm_entrants['pop'] * 1000000

#     apps['installer_months_age__county'] = ((apps['app_received']-apps['firm_enter_date']).dt.days +1)/30
#     apps = apps[apps['installer_months_age__county'].notnull()]
#     return apps

def firm_entry():
    apps = get_data()
    # apps = __firm_entry_data(apps)
    # print(apps['installer_months_age__county'])

    apps['log_months_age'] = np.log(apps['installer_months_age__county'])
    observations = []
    model1 = pf.feols(
        'tc_log ~ pio_TF*log_months_age + anticipation_period*log_months_age  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps
    )
    observations.append(apps['tc_log'].count())

    model2 = pf.feols(
        'tc_log ~ pio_TF*log_months_age*months_to_completion +anticipation_period*log_months_age*months_to_completion + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data = apps
    )
    observations.append(apps['tc_log'].count())
    # print(model2.summary())
    model3 = pf.feols(
        'tc_log ~ pio_TF*log_months_age + anticipation_period*log_months_age + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data = apps
    )
    observations.append(apps['tc_log'].count())
    # print(model3.summary())
    model4 = pf.feols(
        'tc_log ~ pio_TF*log_months_age*months_to_completion + anticipation_period*log_months_age*months_to_completion + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data = apps
    )
    observations.append(apps['tc_log'].count())
    # print(model4.summary())

    print(pf.etable(
        [model1, model2, model3, model4],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'log_months_age': 'Log Age',
            'pio_TF:log_months_age': 'Treat x Age',
            'anticipation_period:log_months_age': 'Anticipation x Age',
            'months_to_completion': 'Months to Completion',
            'pio_TF:months_to_completion': 'Treat x MTC',
            'anticipation_period:months_to_completion': 'Anticipation x MTC',
            'log_months_age:months_to_completion': 'Age x MTC',
            'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
            'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC'
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

    print(pf.etable(
        [model1, model3],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'log_months_age': 'Log Age',
            'pio_TF:log_months_age': 'Treat x Age',
            'anticipation_period:log_months_age': 'Anticipation x Age',
            'months_to_completion': 'Months to Completion',
            'pio_TF:months_to_completion': 'Treat x MTC',
            'anticipation_period:months_to_completion': 'Anticipation x MTC',
            'log_months_age:months_to_completion': 'Age x MTC',
            'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
            'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC'
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))


    # model_to_latex([model1, model2, model3, model4],
    #     {
    #         'pio_TF' : 'Treatment',
    #         'anticipation_period' : 'Anticipation',
    #         'log_months_age': 'Log Age',
    #         'pio_TF:log_months_age': 'Treat x Age',
    #         'anticipation_period:log_months_age': 'Anticipation x Age',
    #         'days_to_completion': 'Days to Completion',
    #         'pio_TF:days_to_completion': 'Treat x DTC',
    #         'anticipation_period:days_to_completion': 'Anticipation x DTC',
    #         'log_months_age:days_to_completion': 'Age x DTC',
    #         'pio_TF:log_months_age:days_to_completion': 'Treat x Age x DTC',
    #         'anticipation_period:log_months_age:days_to_completion': 'Anticipation x Age x DTC'
    #     },
    #     ["poi*age c FE", "poi*age*dtc c FE", "pio*age fc FE", "poi*age*dtc fc FE"],
    #     observations)


def model_to_latex(models, coefs, model_names, obs):

    def get_stars(p_val):
        if abs(p_val) < 0.01:
            return "^{***}"
        elif abs(p_val) < 0.05:
            return "^{**}"
        elif abs(p_val) < 0.1:
            return "^*"
        else:
            return ""
    collected_terms = collections.defaultdict(list)
    # obs = []

    for model in models:
        # print(dir(model))
        # print(model.coef)
        # print(model.pvalue)
        # print(model.se)
        # import pdb
        # pdb.set_trace()
        # df = pd.read_html(model.summary().tables[1].as_html(),header=0,index_col=0)[0]
        # df = df.reset_index()

        # values = df[df['index'] in coefs]

        for coef, label in coefs.items():
            try:
                val = round(model.coef()[coef], 5)
                std = round(model.se()[coef], 5)
                # val = df[df['index'] == coef]['coef'].max()
                # std = df[df['index'] == coef]['std err'].max()
                stars = get_stars(model.pvalue()[coef].max())
                collected_terms[coef].append([f"${str(val)}{stars}$", "( "+ str(std) + ")"])
            except KeyError:
                collected_terms[coef].append(['', ''])
        # table_0 = pd.read_html(model.summary().tables[0].as_html(),header=0,index_col=0)
        # table_2 = pd.read_html(model.summary().tables[2].as_html(),header=0,index_col=0)[0]
        # obs.append(str(int(model.nobs)))
    # collect latex:
    latex_interior = " & " + " & ".join(model_names) + "\\\\ \n \\hline \\hline \n"
    for coef, label in coefs.items():
        latex_interior += label + " & " + " & ".join(co[0] for co in collected_terms[coef]) +  "\\\\ \n"

        latex_interior += " & " + " & ".join(co[1] for co in collected_terms[coef]) +  "\\\\ \n "

    latex_interior += " obs & " + " & ".join([str(ob) for ob in obs]) + "\\\\ \n"
    print(latex_interior)

def nem2_only_fixest():
    apps = get_data(is_nem2=True)

    # apps = apps[apps['NEM_tariff'] == '2.0']
    # apps = apps[apps['pio_TF'] == True]

    apps = apps[apps['market_share'].notnull()]


    # fit a model via OLS
    fit = pf.feols('tc_log ~ size_dc + battery_storage + pio_TF + anticipation_period + output_monitoring + has_battery | service_county', data=apps)
    print(fit.summary())

def get_fifo_scores():
    fc_model, obs_fc = fifo_score('fc')
    c_model, obs_c = fifo_score('c')
    print(pf.etable([c_model, fc_model], type='tex',
        felabels={'county_lic': 'Firm-County', 'service_county': 'County'},
        labels={
            'fifo_score_c_backwards': 'FIFO Score',
            'fifo_score_fc_backwards': 'FIFO Score',
            'pio_TF': 'Treatment',
            'anticipation_period': 'Anticipation',
            'fifo_score_c_backwards:pio_TF': 'FIFO x Treatment',
            'fifo_score_fc_backwards:pio_TF': 'FIFO x Treatment',
            'fifo_score_c_backwards:anticipation_period': 'FIFO x Anticipation',
            'fifo_score_fc_backwards:anticipation_period': 'FIFO x Anticipation',
        },
        signif_code=[0.01, 0.05, 0.1]
    ))
    # model_to_latex(
    #     [c_model, fc_model],
    #     {
    #         'fifo_score_fc_backwards': 'FIFO Score',
    #         'fifo_score_c_backwards': 'FIFO Score',
    #         'pio_TF': 'Treatment',
    #         'anticipation_period': 'Anticipation',
    #         'fifo_score_c_backwards:pio_TF': 'FIFO x Treatment',
    #         'fifo_score_fc_backwards:pio_TF': 'FIFO x Treatment',
    #         'anticipation_period:fifo_score_c_backwards': 'Anticipation x FIFO',
    #         'anticipation_period:fifo_score_fc_backwards': 'Anticipation x FIFO',
    #     },
    #     ['(1)', '(2)'],
    #     [obs_c, obs_fc]
    # )

def diffndiff():
    self_install = get_data(self_install=True)
    apps = get_data()
    apps = pd.concat([apps, self_install])
    apps = apps[apps['app_received'] >= '2021-01-01']
    apps = apps[apps['app_received'] <= '2023-04-13']
    # apps['log_ccci'] = np.log(apps['ccci_cpi'])
    model = pf.feols('tc_log ~ self_install*C(year_month)*days_to_completion + size_dc + battery_storage + self_install*output_monitoring + has_battery | service_county', data = apps)

    print(pf.etable(model, type='tex'))

    df = model.coef().reset_index()
    std_err = model.se().reset_index()

    df = pd.merge(df, std_err, on='Coefficient')


    df['year_month'] = df['Coefficient'].astype('str').str.extract(r'(\d{4}-\d{2})')[0].astype("datetime64[ns]")
    df = df[df['year_month'] >= '2021-01-01']

    df = df[df['Coefficient'].astype('str').str[-4:] != 'tion']

    self_df = df[df['Coefficient'].astype('str').str[0:4] == 'self']
    df = df[df['Coefficient'].astype('str').str[0:4] != 'self']

    self_df = self_df[['Estimate', 'year_month', 'Std. Error']]
    df = df[['Estimate', 'year_month',  'Std. Error']]
    self_df = self_df.rename(columns={'Estimate': 'Self Install', 'Std. Error': 'se_self'})
    df = df.rename(columns={'Estimate': 'Firm Install', 'Std. Error': 'se_firm'})

    df = pd.merge(df, self_df, on='year_month')

    fig, ax = plt.subplots()
    ax.plot(df['year_month'], df['Firm Install'], label="Firm Install")
    ax.plot(df['year_month'], df['Self Install'], label='Self Install')

    ax.fill_between(df['year_month'], df['Self Install'] - df['se_self']*(1.96), df['Self Install'] + df['se_self']*(1.96), color='r', alpha=.15)
    ax.fill_between(df['year_month'], df['Firm Install'] - df['se_firm']*(1.96), df['Firm Install'] + df['se_firm']*(1.96), color='b', alpha=.15)

    ax.legend()
    plt.show()


def firm_entry_bins():
    apps = get_data()
    # apps = __firm_entry_data(apps)

    bins = [1, 3, 6, 12, 24]

    old_bin = 0
    for b in bins:
        apps[f'bin_{b}'] = (apps['installer_months_age__county'].between(old_bin, b, inclusive='left'))
        old_bin = b

    bins_str = " + ".join(f"bin_{b}" for b in bins)
    # apps['tc_log'] = np.log(apps['tc_2022']/apps['ccci_cpi'])

    model1 = pf.feols(
        f'tc_log ~ pio_TF*({bins_str}) + anticipation_period*({bins_str})  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps
    )


    model2 = pf.feols(
        f'tc_log ~ pio_TF*({bins_str})*months_to_completion +anticipation_period*({bins_str})*months_to_completion + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data = apps
    )

    model3 = pf.feols(
        f'tc_log ~ pio_TF*({bins_str}) + anticipation_period*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data = apps
    )

    model4 = pf.feols(
        f'tc_log ~ pio_TF*({bins_str})*months_to_completion + anticipation_period*({bins_str})*months_to_completion + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data = apps
    )


    print(pf.etable(
        [model1, model2, model3, model4],
        # [model1, model3],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'log_months_age': 'Log Age',
            'pio_TF:log_months_age': 'Treat x Age',
            'anticipation_period:log_months_age': 'Anticipation x Age',
            'months_to_completion': 'Months to Completion',
            'pio_TF:months_to_completion': 'Treat x MTC',
            'anticipation_period:months_to_completion': 'Anticipation x MTC',
            'log_months_age:months_to_completion': 'Age x MTC',
            'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
            'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC'
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

    print(pf.etable(
        # [model1, model2, model3, model4],
        [model1, model3],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'log_months_age': 'Log Age',
            'pio_TF:log_months_age': 'Treat x Age',
            'anticipation_period:log_months_age': 'Anticipation x Age',
            'months_to_completion': 'Months to Completion',
            'pio_TF:months_to_completion': 'Treat x MTC',
            'anticipation_period:months_to_completion': 'Anticipation x MTC',
            'log_months_age:months_to_completion': 'Age x MTC',
            'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
            'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC'
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

    fig, ax = plt.subplots(1)
    coefs = model1.coef().reset_index()
    fields = [f'pio_TF:bin_{b}' for b in bins]

    model1_df = coefs[coefs['Coefficient'].isin(fields)]
    model1_df2 = coefs[coefs['Coefficient'].isin([f"bin_{b}" for b in bins])]
    ses = model1.se().reset_index()


    se1_df = ses[ses['Coefficient'].isin(fields)]
    se1_df2 = ses[ses['Coefficient'].isin([f"bin_{b}" for b in bins])]

    model1_df = pd.merge(model1_df, se1_df, on="Coefficient")
    model1_df2 = pd.merge(model1_df2, se1_df2, on="Coefficient")

    coef_matching = {f'bin_{b}': f"{'<=' if i == 0 else f'{bins[i-1]} -'} {b} mo." for i, b in enumerate(bins)}
    def apply_coef_matching(val):
        if f"bin_48" in val:
            return coef_matching['bin_48']
        if f"bin_24" in val:
            return coef_matching['bin_24']
        elif f'bin_12' in val:
            return coef_matching['bin_12']
        elif f'bin_1' in val:
            return coef_matching['bin_1']
        elif f'bin_3' in val:
            return coef_matching['bin_3']
        elif f'bin_6' in val:
            return coef_matching['bin_6']
        else:
            return val


    # coef_matching = {f'pio_TF:bin_{b}': f"{'<=' if i == 0 else f'{bins[i-1]} -'} {b} mo." for i, b in enumerate(bins)}

    # print(coef_matching)

    model1_df['Coefficient_'] = model1_df['Coefficient'].apply(apply_coef_matching)
    model1_df2['Coefficient_'] = model1_df2['Coefficient'].apply(apply_coef_matching)
    # model1_df2.loc[:, 'Coefficient_'] = coef_matching2[model1_df2.loc[: ,'Coefficient']]
    x = np.arange(len(model1_df['Coefficient_']))
    ax.errorbar(x - 0.1, model1_df['Estimate'],
            yerr=[1.92*model1_df['Std. Error'], 1.92*model1_df['Std. Error']],
                     fmt='o', ecolor='gray', capsize=5, label='Treatment Effect')
    ax.errorbar(x + 0.1, model1_df2['Estimate'],
            yerr=[1.92*model1_df2['Std. Error'], 1.92*model1_df2['Std. Error']],
                     fmt='o', ecolor='gray', capsize=5, label='Whole Sample')
    ax.set_xticks(x, coef_matching.values())
    plt.legend(fontsize=12)
    plt.axhline(linewidth=2, color='black')
    ax.set_xlabel("Firm Age (Months)", fontsize=16)
    ax.set_ylabel("Log Installation Costs", fontsize=16)
    fig.suptitle("Impact of Age on Price", fontsize=20)
    plt.savefig("./firm_age_bins.png")
    plt.show()

    apps_treatment = apps[apps['pio_TF'] == True]
    model1 = pf.feols(
        f'tc_log ~ ({bins_str})  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps_treatment
    )


    model2 = pf.feols(
        f'tc_log ~ ({bins_str})+ months_to_completion + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data = apps_treatment
    )

    model3 = pf.feols(
        f'tc_log ~ ({bins_str})*months_to_completion + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data = apps_treatment
    )

    # model3 = pf.feols(
    #     f'tc_log ~ ({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
    #     data = apps_treatment
    # )

    # model4 = pf.feols(
    #     f'tc_log ~ ({bins_str})*months_to_completion +  size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
    #     data = apps_treatment
    # )

    # model2 = pf.feols(
    #     f'tc_log ~ ({bins_str})*months_to_completion + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
    #     data = apps_treatment
    # )

    print("Treatment period only!")
    print(pf.etable(
        # [model1, model2, model3, model4],
        [model1, model2],
        # [model1, model2, model3],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'log_months_age': 'Log Age',
            'pio_TF:log_months_age': 'Treat x Age',
            'anticipation_period:log_months_age': 'Anticipation x Age',
            'months_to_completion': 'Months to Completion',
            'pio_TF:months_to_completion': 'Treat x MTC',
            'anticipation_period:months_to_completion': 'Anticipation x MTC',
            'log_months_age:months_to_completion': 'Age x MTC',
            'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
            'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC'
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

def firm_entry_dtc_bins():
    apps = get_data()
    # apps = __firm_entry_data(apps)

    apps, bins_str = __age_bins(apps)

    model1 = pf.feols(
        f'days_to_completion ~ pio_TF*({bins_str})*survived_one_year + anticipation_period*({bins_str})*survived_one_year  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps
    )


    model2 = pf.feols(
        f'days_to_completion ~ pio_TF*({bins_str}) +anticipation_period*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data = apps
    )

    # model3 = pf.feols(
    #     f'days_to_completion ~ pio_TF*({bins_str})*survived_one_year + anticipation_period*({bins_str})*survived_one_year + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
    #     data = apps
    # )

    # model4 = pf.feols(
    #     f'days_to_completion ~ pio_TF*({bins_str})*months_to_completion + anticipation_period*({bins_str})*months_to_completion + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
    #     data = apps
    # )


    # print(pf.etable(
    #     [model1, model2, model3, model4],
    #     # [model1, model3],
    #     labels={
    #         'pio_TF' : 'Treatment',
    #         'anticipation_period' : 'Anticipation',
    #         'log_months_age': 'Log Age',
    #         'pio_TF:log_months_age': 'Treat x Age',
    #         'anticipation_period:log_months_age': 'Anticipation x Age',
    #         'months_to_completion': 'Months to Completion',
    #         'pio_TF:months_to_completion': 'Treat x MTC',
    #         'anticipation_period:months_to_completion': 'Anticipation x MTC',
    #         'log_months_age:months_to_completion': 'Age x MTC',
    #         'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
    #         'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC'
    #     },
    #     type='tex',
    #     print_tex=True,
    #     signif_code=[0.01, 0.05, 0.1],
    # ))

    print(pf.etable(
        # [model1, model2, model3, model4],
        [model1, model2],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'log_months_age': 'Log Age',
            'pio_TF:log_months_age': 'Treat x Age',
            'anticipation_period:log_months_age': 'Anticipation x Age',
            'months_to_completion': 'Months to Completion',
            'pio_TF:months_to_completion': 'Treat x MTC',
            'anticipation_period:months_to_completion': 'Anticipation x MTC',
            'log_months_age:months_to_completion': 'Age x MTC',
            'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
            'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC'
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

    fig, ax = plt.subplots(1)
    coefs = model1.coef().reset_index()
    bins = [1, 3, 6, 12, 24]
    fields = [f'pio_TF:bin_{b}' for b in bins]

    model1_df = coefs[coefs['Coefficient'].isin(fields)]
    model1_df2 = coefs[coefs['Coefficient'].isin([f"bin_{b}" for b in bins])]
    ses = model1.se().reset_index()


    se1_df = ses[ses['Coefficient'].isin(fields)]
    se1_df2 = ses[ses['Coefficient'].isin([f"bin_{b}" for b in bins])]

    model1_df = pd.merge(model1_df, se1_df, on="Coefficient")
    model1_df2 = pd.merge(model1_df2, se1_df2, on="Coefficient")

    coef_matching = {f'bin_{b}': f"{'<=' if i == 0 else f'{bins[i-1]} -'} {b} mo." for i, b in enumerate(bins)}
    def apply_coef_matching(val):
        # if f"bin_48" in val:
        #     return coef_matching['bin_48']
        if f"bin_24" in val:
            return coef_matching['bin_24']
        elif f'bin_12' in val:
            return coef_matching['bin_12']
        elif f'bin_1' in val:
            return coef_matching['bin_1']
        elif f'bin_3' in val:
            return coef_matching['bin_3']
        elif f'bin_6' in val:
            return coef_matching['bin_6']
        else:
            return val


    # coef_matching = {f'pio_TF:bin_{b}': f"{'<=' if i == 0 else f'{bins[i-1]} -'} {b} mo." for i, b in enumerate(bins)}

    # print(coef_matching)

    # model1_df['Coefficient_'] = model1_df['Coefficient'].apply(apply_coef_matching)
    # model1_df2['Coefficient_'] = model1_df2['Coefficient'].apply(apply_coef_matching)
    # # model1_df2.loc[:, 'Coefficient_'] = coef_matching2[model1_df2.loc[: ,'Coefficient']]
    # x = np.arange(len(model1_df['Coefficient_']))
    # ax.errorbar(x - 0.1, model1_df['Estimate'],
    #         yerr=[1.92*model1_df['Std. Error'], 1.92*model1_df['Std. Error']],
    #                  fmt='o', ecolor='gray', capsize=5, label='Treatment Effect')
    # ax.errorbar(x + 0.1, model1_df2['Estimate'],
    #         yerr=[1.92*model1_df2['Std. Error'], 1.92*model1_df2['Std. Error']],
    #                  fmt='o', ecolor='gray', capsize=5, label='Whole Sample')
    # ax.set_xticks(x, coef_matching.values())
    # plt.legend()
    # plt.axhline(linewidth=2, color='black')
    # ax.set_xlabel("Firm Age (Months)")
    # ax.set_ylabel("Log Installation Costs")
    # fig.suptitle("Impact of Age on Price")
    # plt.savefig("./firm_age_bins.png")
    # plt.show()

def __age_bins(apps, county=True):
    bins = [1, 3, 6, 12, 24]

    # old_bin = 0
    # for b in bins:
    #     apps[f'bin_{b}'] = (apps[f'installer_months_age{"__county" if county else ""}'].between(old_bin, b, inclusive='left'))
    #     old_bin = b

    bins_str = " + ".join(f"bin_{b}__age_{'county' if county else 'state'}" for b in bins)
    return apps, bins_str


def mtc_vs_installs():
    apps=get_data()
    apps, bins_str = __age_bins(apps)
    apps, bins_state_str = __age_bins(apps, False)
    apps, cum_installs_str = __cumulative_installs(apps)
    apps, cum_installs_state_str = __cumulative_installs(apps, False)

    model1 = pf.feols(
    #     f'fifo_score_c_backwards ~ pio_TF*({bins_str}) + anticipation_period*({bins_str})  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        f'months_to_completion ~ pio_TF*({cum_installs_str}) + anticipation_period*({cum_installs_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps
    )
    model2 = pf.feols(
        f'months_to_completion ~ pio_TF*({cum_installs_state_str}) + anticipation_period*({cum_installs_state_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps
    )

    model3 = pf.feols(
    #     f'fifo_score_c_backwards ~ pio_TF*({bins_str}) + anticipation_period*({bins_str})  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        f'months_to_completion ~ pio_TF*({cum_installs_str}) + anticipation_period*({cum_installs_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps
    )
    model4 = pf.feols(
        f'months_to_completion ~ pio_TF*({cum_installs_state_str}) + anticipation_period*({cum_installs_state_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps
    )

    # model3 = pf.feols(
    #     f'fifo_score_c_backwards ~ pio_TF*({cum_installs_str}) + anticipation_period*({cum_installs_str})  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
    #     data=apps
    # )
    # model4 = pf.feols(
    #     f'fifo_score_c_backwards ~ pio_TF*({cum_installs_str})*survived_one_year + anticipation_period*({cum_installs_str})*survived_one_year  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
    #     data=apps
    # )




    print(pf.etable(
        [model1, model2, model3, model4],
        # [model1, model2],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'log_months_age': 'Log Age',
            'pio_TF:log_months_age': 'Treat x Age',
            'anticipation_period:log_months_age': 'Anticipation x Age',
            'months_to_completion': 'Months to Completion',
            'pio_TF:months_to_completion': 'Treat x MTC',
            'anticipation_period:months_to_completion': 'Anticipation x MTC',
            'log_months_age:months_to_completion': 'Age x MTC',
            'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
            'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC',
            'survived_one_year': "Survived"
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

    apps_treatment = apps[apps['pio_TF'] == True]

    model1 = pf.feols(
    #     f'fifo_score_c_backwards ~ pio_TF*({bins_str}) + anticipation_period*({bins_str})  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        f'months_to_completion ~ ({cum_installs_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps_treatment
    )
    model2 = pf.feols(
        f'months_to_completion ~ ({cum_installs_state_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps_treatment
    )

    model3 = pf.feols(
    #     f'fifo_score_c_backwards ~ ({bins_str}) + anticipation_period*({bins_str})  + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        f'months_to_completion ~ ({cum_installs_str})  + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps_treatment
    )
    model4 = pf.feols(
        f'months_to_completion ~ ({cum_installs_state_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps_treatment
    )

    print("Treatment ONLY")
    print(pf.etable(
        [model1, model2, model3, model4],
        # [model1, model2],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'log_months_age': 'Log Age',
            'pio_TF:log_months_age': 'Treat x Age',
            'anticipation_period:log_months_age': 'Anticipation x Age',
            'months_to_completion': 'Months to Completion',
            'pio_TF:months_to_completion': 'Treat x MTC',
            'anticipation_period:months_to_completion': 'Anticipation x MTC',
            'log_months_age:months_to_completion': 'Age x MTC',
            'pio_TF:log_months_age:months_to_completion': 'Treat x Age x MTC',
            'anticipation_period:log_months_age:months_to_completion': 'Anticipation x Age x MTC',
            'survived_one_year': "Survived"
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))



def time_series_prices():
    apps = get_data(False)
    apps = apps[apps['year_month'] <= '2023-05']
    apps, bins_str = __age_bins(apps)

    model = pf.feols(
        f'tc_log ~ C(year_month)*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps,
    )
    print(pf.etable(
        model,
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'tc_log': 'Log Installation Price',
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

def __cumulative_installs(apps, county=True):
    # apps = apps.sort_values('app_complete')
    # apps['nth_complete__county'] = apps.groupby('county_lic')['app_complete'].rank(method='min') / 100
    # apps['nth_complete__state'] = apps.groupby('cslb_num')['app_complete'].rank(method='min') / 100
    # apps['log_nth_complete__county'] = np.log(apps['nth_complete__county'])
    # apps['log_nth_complete__state'] = np.log(apps['nth_complete__state'])

    bins = [10, 20, 50, 100, 1000]

    # total_complete = apps.groupby('county_lic' if county else 'cslb_num')[f'nth_complete__{"county" if county else "state"}'].max().reset_index()
    # total_complete[f'exits_under_50_installs__{"county" if county else "state"}'] = total_complete[f'nth_complete__{"county" if county else "state"}'] < 50
    # total_complete[f'exits_under_10_installs__{"county" if county else "state"}'] = total_complete[f'nth_complete__{"county" if county else "state"}'] < 10
    # total_complete = total_complete.rename(columns={f'nth_complete__{"county" if county else "state"}': 'total_complete'})

    # apps = pd.merge(apps, total_complete, on='county_lic', how='left')

    # print(apps[f'exits_under_50_installs__{"county" if county else "state"}'])
    old_bin = 0
    for b in bins:
        apps[f'bin_{b}__nth_complete_{"county" if county else "state"}'] = (apps[f'nth_complete__{"county" if county else "state"}'].between(old_bin, b, inclusive='left'))
        old_bin = b

    bins_str = " + ".join(f"bin_{b}__nth_complete_{'county' if county else 'state'}" for b in bins)
    return apps, bins_str

def cum_installs_price():
    apps = get_data(True)
    apps = apps[apps['year_month'] <= '2023-05']
    apps, bins_str = __cumulative_installs(apps)
    apps, bins_str_state = __cumulative_installs(apps, False)


    model1 = pf.feols(
        f'tc_log ~ pio_TF*({bins_str}) + anticipation_period*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        # f'tc_log ~ C(year_month)*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps,
    )
    model2 = pf.feols(
        f'tc_log ~ pio_TF*({bins_str_state}) + anticipation_period*({bins_str_state}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        # f'tc_log ~ C(year_month)*(nth_complete__state) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps,
    )
    model3 = pf.feols(
        f'tc_log ~ pio_TF*({bins_str}) + anticipation_period*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        # f'tc_log ~ C(year_month)*(nth_complete__county) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps,
    )
    model4 = pf.feols(
        f'tc_log ~ pio_TF*({bins_str_state}) + anticipation_period*({bins_str_state}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        # f'tc_log ~ C(year_month)*(nth_complete__state) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps,
    )
    print(pf.etable(
        [model1, model3, model2, model4],
        # [model1],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'tc_log': 'Log Installation Price',
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

    apps_treatment = apps[apps['pio_TF'] == True]
    model1 = pf.feols(
        f'tc_log ~ ({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        # f'tc_log ~ C(year_month)*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps_treatment,
    )
    model2 = pf.feols(
        f'tc_log ~ ({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        # f'tc_log ~ C(year_month)*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps_treatment,
    )
    model4 = pf.feols(
        f'tc_log ~ ({bins_str_state}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        # f'tc_log ~ C(year_month)*(nth_complete__state) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps_treatment,
    )
    model3 = pf.feols(
        f'tc_log ~ ({bins_str_state}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        # f'tc_log ~ C(year_month)*(nth_complete__state) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps_treatment,
    )

    print(pf.etable(
        [model1, model2, model3, model4],
        # [model1],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'tc_log': 'Log Installation Price',
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

def completion_rate():
    apps = get_data()
    apps, bins_str = __age_bins(apps)

    rate = apps.groupby(['county_lic', 'year_month_comp'])['app_id'].count().reset_index()
    rate = rate.sort_values(['county_lic', 'year_month_comp'])

    # Add Zeros:
    unique_year_months = rate['year_month_comp'].unique()

    unique_county_lic = rate['county_lic'].unique()

    rate = rate.set_index(['county_lic', 'year_month_comp'])

    default_rows = [
        [county_lic, year_month, 0]
        for i, year_month in enumerate(unique_year_months)
        for j, county_lic in enumerate(unique_county_lic)
    ]

    default_rate = pd.DataFrame(default_rows, columns=['county_lic', 'year_month_comp', 'rate'])
    default_rate = default_rate.set_index(['county_lic', 'year_month_comp'])

    rate = pd.merge(default_rate, rate, how="left", left_index=True, right_index=True)
    rate = rate.fillna(0)

    rate['rate'] = np.maximum(rate['app_id'], rate['rate'])
    rate = rate.sort_values(['county_lic', 'year_month_comp'])
    rate = rate['rate'].reset_index()
    # rate = rate.sort_values(['county_lic', 'year_month'])

    min_month = min(unique_year_months)
    rate['rate_t-1'] = rate['rate'].shift(-1)
    rate['rate_t-2'] = rate['rate'].shift(-2)
    rate['rate_t-3'] = rate['rate'].shift(-3)
    rate['rate_t-4'] = rate['rate'].shift(-4)
    rate['rate_t-5'] = rate['rate'].shift(-5)
    rate['rate_t-6'] = rate['rate'].shift(-6)

    rate['rate_cum_6_months'] = np.log(rate['rate_t-1'] + rate['rate_t-2'] + rate['rate_t-3'] + rate['rate_t-4'] + rate['rate_t-5'] + rate['rate_t-6'] + .00001)

    apps = apps[apps['year_month_comp'] > '2021-06']
    apps = apps[apps['year_month_comp'] < '2024-10']
    rate['rate_change'] = ((rate['rate'] - rate['rate_t-1'])/rate['rate_t-1'])

    apps = pd.merge(apps, rate, on=['county_lic', 'year_month_comp'], how='left')

    model1 = pf.feols(
        f'tc_log ~ pio_TF*(rate_cum_6_months)*({bins_str}) + anticipation_period*(rate_cum_6_months)*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps,
    )
    model2 = pf.feols(
        f'tc_log ~ pio_TF*(rate_cum_6_months)*({bins_str}) + anticipation_period*(rate_cum_6_months)*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps,
    )
    model3 = pf.feols(
        f'tc_log ~ pio_TF*(rate_cum_6_months) + anticipation_period*(rate_cum_6_months) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps,
    )
    model4 = pf.feols(
        f'tc_log ~ pio_TF*(rate_cum_6_months) + anticipation_period*(rate_cum_6_months) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps,
    )

    print(pf.etable(
        [model3, model4, model1, model2],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'tc_log': 'Log Installation Price',
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))

    apps['log_rate'] = np.log(apps['rate'] + 0.00001)
    model5 = pf.feols(
        f'log_rate ~ pio_TF*(survived_one_year)*({bins_str}) + anticipation_period*(survived_one_year)*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | county_lic',
        data=apps,
    )
    model6 = pf.feols(
        f'log_rate ~ pio_TF*(survived_one_year)*({bins_str}) + anticipation_period*(survived_one_year)*({bins_str}) + size_dc + battery_storage + has_battery+ output_monitoring | service_county',
        data=apps,
    )

    print(pf.etable(
        [model6, model5],
        labels={
            'pio_TF' : 'Treatment',
            'anticipation_period' : 'Anticipation',
            'tc_log': 'Log Installation Price',
            'rate_cum_6_months': 'Last 6 mos.',
            'size_dc': 'Size',
            'battery_storage': 'Battery Size'
        },
        type='tex',
        print_tex=True,
        signif_code=[0.01, 0.05, 0.1],
    ))


# nem2_only()
# nem2_only_fixest()
# market_share()
# hhi()

# nem2_and_3()
# nem2_only_aniticpation()
# ms_and_days_to_comp()
# market_share__count()
# simple_compare_NEM2_3()
# queue_length()
# year_month_comp()
# days_to_comp()
# business_type()
# price_num_lic()
# firm_entry_dtc_bins()
# time_series_prices()
# firm_entry()

# Main regressions
# year_month()
# price_time_to_completion() # *
get_fifo_scores() # *
# firm_entry_bins() # *
# completion_rate()
# mtc_vs_installs()
# cum_installs_price()

# diffndiff()
