import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np


import const


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

def get_data():
    apps = pd.read_csv('./data/applications_cleaned.csv')
    # San Joaquin appears to be causing colliniarities - my guess is there just aren't any or many
    # installations in the county.
    apps = apps[apps['service_county'] != "San Joaquin"]
    apps = apps[apps['service_county'] != "Yuba"]
    apps = apps[apps['mounting_method'] == "Rooftop"]
    # apps = apps[apps['size_dc'] >= 1]
    apps = apps.astype(const.TYPE_DICT)
    # Limit received to just 2022 - this way we don't have
    apps = apps[apps['app_received'] >= pd.to_datetime('2021-01-01')]
    apps = apps[apps['self_install'] == False]
    # apps = apps[apps['is_preceeded'] == False]
    return apps

def nem2_and_3():
    apps = get_data()
    model = smf.ols(
        'total_cost ~ size_dc + battery_storage + pio_TF + output_monitoring + C(service_county)  + ccci + is_NEM2' ,
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
    apps = apps[apps['NEM_tariff'] == '2.0']


    # Run the regression using statsmodels with fixed effects
    # Using formula interface to make it easy to add fixed effects

    model = smf.ols(
        'total_cost ~ size_dc + battery_storage + pio_TF*days_to_completion + output_monitoring + C(service_county)  + ccci + has_battery',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

    # print("Total Size -- no anticipation")
    # model = smf.ols(
    #     'size_dc ~ + electric_vehicle + pio_TF + output_monitoring + C(service_county)',
    #     data=apps
    # ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    # print(model.summary())

def nem2_only_aniticpation():
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    print("Total Cost -- anticipation")
    model = smf.ols(
        'total_cost ~ size_dc + battery_storage + pio_TF + output_monitoring + C(service_county) + ccci +  anticipation_period' ,
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

    print("Total Size -- anticipation")
    model = smf.ols(
        'size_dc ~ electric_vehicle + pio_TF + C(service_county) + output_monitoring + anticipation_period',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

    # diffs = apps.set_index(['app_id','service_zip').groupby(level='service_zip')\
    #     .transform(lambda x: x.sort_index().diff())\
    #     .reset_index()

    # model = smf.ols(
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
    model = smf.ols(
        'total_cost ~ size_dc + battery_storage + output_monitoring + HHI_city*anticipation_period + ccci + C(service_county)',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

    # apps_after = apps[apps['pio_TF'] == True]
    # model = smf.ols(
    #     'total_cost ~ size_dc + electric_vehicle + output_monitoring + HHI_city + C(mounting_method) ',
    #     data=apps_after
    # ).fit()
    # print(model.summary())

    # apps_before = apps[apps['pio_TF'] == False]
    # model = smf.ols(
    #     'total_cost ~ size_dc + electric_vehicle + output_monitoring + HHI_city + C(mounting_method) + C(service_county)',
    #     data=apps_before
    # ).fit()
    # print(model.summary())

    # check_for_correlations(apps)

def market_share():
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    model = smf.ols(
        'total_cost ~ size_dc + battery_storage + market_share*pio_TF + output_monitoring + ccci + days_to_completion + C(service_county)',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())


def market_share__count():
    apps = get_data()
    apps = apps[apps['NEM_tariff'] == '2.0']
    model = smf.ols(
        'total_cost ~ size_dc + battery_storage + ms_count*pio_TF + output_monitoring + days_to_completion+ C(service_county) + ccci',
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

def simple_compare_NEM2_3():
    apps = get_data()
    model = smf.ols(
        'total_cost ~ C(NEM_tariff) + size_dc + C(service_county) + battery_storage + ccci + output_monitoring',
        data=apps
    ).fit(cov_type='cluster', cov_kwds={'groups': apps['service_county']})
    print(model.summary())

nem2_only()
# market_share()
# hhi()
# nem2_and_3()
# nem2_only_aniticpation()
# ms_and_days_to_comp()
# market_share__count()
# simple_compare_NEM2_3()
