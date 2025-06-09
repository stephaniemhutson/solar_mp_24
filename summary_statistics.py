import pandas as pd
import collections
import pprint
import datetime as dt
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np
import pendulum

import const
import seaborn as sns


dpi = 80
mpl_styles = {
    'figure.figsize': (10, 8),
    # Up the default resolution for figures.
    'figure.dpi': dpi,
    'savefig.dpi': dpi,
}

# sns.set_theme(context='paper')
plt.rcParams.update(mpl_styles)
# def clean_tts():
#     tts_df = pd.read_csv("./data/TTS_10_2023.csv")

#     tts_df = tts_df[tts_df.total_installed_price > 5]
#     tts_df = tts_df[tts_df.city != -1]
#     tts_df = tts_df[tts_df.city != "-1"]

#     print("Summary Statistics of the Tracking the Sun")



#     pprint.pp(tts_df.columns)
#     # module_manufacturer_1 = collections.Counter(tts_df['module_manufacturer_1'])

#     # pprint.pp(module_manufacturer_1)
#     # module_manufacturer_2 = collections.Counter(tts_df['module_manufacturer_2'])

#     # pprint.pp(module_manufacturer_2)
#     # module_manufacturer_3 = collections.Counter(tts_df['module_manufacturer_3'])

#     # pprint.pp(module_manufacturer_3)
#     print("Total installed price by City, State where count > 4")
#     # state_city_tts = tts_df.groupby(['state', 'city'])

#     # print(state_city_tts.groupby(['state', 'city'])['total_installed_price'].describe())

#     installer_tts = tts_df[tts_df['installer_name'] != -1]
#     installer_tts = installer_tts[installer_tts['installer_name'] != '-1']
#     installer_tts['installer_name'] = installer_tts['installer_name'].str.upper()
#     installer_tts['city'] = installer_tts['city'].str.upper()
#     installer_tts['state'] = installer_tts['state'].str.upper()

#     # print(installer_tts.groupby(['state', 'city', 'installer_name'])['total_installed_price'].describe())

#     grouped_installer = pd.DataFrame(installer_tts.groupby(['state', 'city', 'installer_name', ])['total_installed_price'].describe())

#     grouped_installer.to_csv("./data/aggregate_by_city_installer_ts.csv")

# def handle_grouped_installer():
#     grouped_installer = pd.read_csv("./data/aggregate_by_city_installer_ts.csv")
#     grouped_installer = grouped_installer[grouped_installer['installer_name'] != "UNKNOWN"]


#     # print(collections.Counter(list(grouped_installer["state"])))
#     grouped_installer = grouped_installer.groupby(['state', 'city']).filter(lambda x: x['city'].count() > 50)

#     # state_cities =
#     print(grouped_installer.sort_values("count"))

#     print(grouped_installer[grouped_installer['city'] == "SAN FRANCISCO"].sort_values("count")[350:])

#     # for state, city in state_cities:
#     #     market = grouped_installer[grouped_installer["state"] == state and grouped_installer["city"] == city]
#     #     print(f"{state}, {city}")
#     print(collections.Counter(list(grouped_installer["state"])))

#     print(collections.Counter(list(grouped_installer[grouped_installer['city'] == "SAN DIEGO"][grouped_installer['count'] > 3]["city"])))
#     print(grouped_installer[grouped_installer['city'] == "SAN DIEGO"][grouped_installer['count'] > 3].sort_values("count"))
#     print(collections.Counter(list(grouped_installer[grouped_installer['city'] == "BAKERSFIELD"][grouped_installer['count'] > 3]["city"])))
#     print(grouped_installer[grouped_installer['city'] == "YOLO"][grouped_installer['count'] > 3].sort_values("count"))


#     san_diego = grouped_installer[grouped_installer['city'] == "SAN DIEGO"].to_dict()
#     bakersfield = grouped_installer[grouped_installer['city'] == "BAKERSFIELD"].to_dict()
#     sacramento = grouped_installer[grouped_installer['city'] == "SACRAMENTO"].to_dict()
#     yolo = grouped_installer[grouped_installer['city'] == "YOLO"].to_dict()
#     san_francisco = grouped_installer[grouped_installer['city'] == "SAN FRANCISCO"].to_dict()

#     # print(hhi(san_diego))
#     # print(hhi(bakersfield))
#     # print(hhi(sacramento))
#     # print(hhi(san_francisco))
#     # print(hhi(yolo))
#     hhis = []

#     for city in set(grouped_installer['city']):

#         hhis.append(hhi(grouped_installer[grouped_installer['city'] == city].to_dict()))

#     # print(hhis)
#     print(sum(hhis) / len(hhis))
#     # print(len([h for h in hhis if h > 1000])/len(hhis))
#     plt.hist(hhis)
#     plt.suptitle("HHI Index, California cities with more than 50 projects")

#     plt.show()




# # def hhi(market_data):
# #     income = {}

# #     # for key, value in market_data.items()
# #     count = len(market_data['state'])

# #     for index in market_data['installer_name'].keys():
# #         # print(market_data['installer_name'])
# #         installer = market_data['installer_name'][index]
# #         mean_cost = market_data['mean'][index]
# #         num_proj = market_data['count'][index]

# #         income[installer] = mean_cost * num_proj


# #         # print(installer)
# #         # data = market_data[market_data['installer_name'] == installer]
# #         # income.push(data['count'] * data['mean'])
# #     # print(income)
# #     total_income = sum(income.values())
# #     return sum([(i/total_income)**2 for i in income.values()])

# def hhi_data():
#     grouped_installer = pd.read_csv("./data/aggregate_by_city_installer_ts.csv")
#     grouped_installer = grouped_installer[grouped_installer['installer_name'] != "UNKNOWN"]


#     grouped_installer = grouped_installer.groupby(['state', 'city']).filter(lambda x: x['city'].count() > 50)
#     hhis = []
#     for city in set(grouped_installer['city']):

#         hhis.append(hhi(grouped_installer[grouped_installer['city'] == city].to_dict()))




def ca_projects(tpo=False, self_install=False):
    if self_install:
        projects = pd.read_csv(f'./data/self_installed_cleaned_12_24.csv')
    else:
        projects = pd.read_csv(f'./data/applications_cleaned{"_tpo" if tpo else ""}_12_24.csv')
    projects = projects.astype({"year_month": "datetime64[ns]", "year_month_comp": "datetime64[ns]"})
    # projects = projects[projects['installer_name'] == "tesla energy operations inc"]
    projects_app = projects[projects['year_month'] >= '2020-01']

    projects_1 = projects[['pio_TF', 'is_NEM2', 'app_received', 'app_id', 'total_cost', 'installer_name']]

    print(projects_1)
    projects_1 = projects_1[projects_1['pio_TF'] == True]
    projects_1 = projects_1[projects_1['is_NEM2'] == True]
    # projects_1 =


    # print(projects_1)
    projects_1['service'] = projects_1['app_id'].astype(str).str[0:3]
    print(projects_1.groupby(projects_1['installer_name'])['app_id'].count().sort_values())
    print(projects_1.groupby(projects_1['service'])['total_cost'].sum())
    print(projects_1.groupby(projects_1['service'])['total_cost'].sum()/projects_1.groupby(projects_1['service'])['app_id'].count())

    # return
    # print(dir(projects_app['year_month'].dt))
    # return
    count_df = projects_app.groupby('year_month')['app_id'].aggregate('count')
    fig, ax = plt.subplots(nrows=1, ncols=2)
    ax[0].bar(count_df.index, count_df, width=23)
    ax[0].title.set_text("Applications Received for new solar in California")
    ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=30)

    projects_comp = projects[projects['year_month_comp'] >= '2020-01']


    count_df_comp = projects_comp.groupby('year_month_comp')['app_id'].aggregate('count')

    # count_df.plot(ax = ax[1], kind='bar', label="Num Applications Completed")
    ax[1].bar(count_df_comp.index, count_df_comp, width=23)
    ax[1].title.set_text("Applications Completed for new solar in California")
    ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=30)
    plt.show()


    count_df = count_df.reset_index()
    count_df_comp = count_df_comp.reset_index()
    df = pd.merge(count_df, count_df_comp, left_on='year_month', right_on='year_month_comp')
    df = df.rename(columns={'app_id_x': 'Applications Received', 'app_id_y': 'Interconnections Completed'})
    df['year_month'] = pd.to_datetime(df['year_month'])
    ax = df.plot(x='year_month', y='Interconnections Completed', kind='bar', width=1)
    ax = df.plot(x='year_month', y='Applications Received', kind='bar', width=1, ax=ax, color='r', alpha=0.5)

    project_type = "Firm Install"
    if tpo:
        project_type = "Third Party Owner"
    elif self_install:
        project_type = "Self Install"
    title = f"Applications Received and Completed -- {project_type}"
    ax.set_title(title)

    # Make most of the ticklabels empty so the labels don't get too crowded
    ticklabels = ['']*len(df.year_month)
    # Every 4th ticklable shows the month and day
    ticklabels[::4] = [item.strftime('%b') for item in df.year_month[::4]]
    # Every 12th ticklabel includes the year
    ticklabels[::12] = [item.strftime('%b\n%Y') for item in df.year_month[::12]]
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    plt.gcf().autofmt_xdate()

    # plt.axvline(x=pd.to_datetime('2022-12-15'))
    # plt.axvline(x=pd.to_datetime('2022-05-15'))
    plt.xlabel('Year-Month')
    plt.savefig('./apps_applied_completed.png')
    plt.show()

def prices():
    pass
    # df = pd.read_csv('./regressions/year_month_rec.csv')
    # df = df[df['index'].str.startswith("C(year_month")]

    # df['year_month'] = df['index'].astype('str').str.extract(r'(\d{4}-\d{2})')[0].astype("datetime64[ns]")

    # dummy_value = df[df['year_month'] == '2022-05-01']['coef'].values[0]

    # df['coef'] -= dummy_value
    # df['ci_lower'] = df['[0.025'] - dummy_value
    # df['ci_upper'] = df['0.975]'] - dummy_value
    # # Plot
    # plt.figure(figsize=(10, 6))
    # plt.errorbar(df['year_month'], df['coef'],
    #              yerr=[df['coef'] - df['ci_lower'], df['ci_upper'] - df['coef']],
    #              fmt='o', ecolor='gray', capsize=5, label='Coefficient')

    # # Add labels and title
    # plt.xlabel('Year-Month')
    # plt.ylabel('Dollars')
    # plt.title('Received Year-Month Coefficients with 95% Confidence Intervals')
    # # plt.xticks(rotation=45)
    # plt.axvline(x=pd.to_datetime('2022-12-15'))
    # plt.axvline(x=pd.to_datetime('2023-04-13'))
    # # plt.grid(axis='y')
    # plt.axhline(y=0, color='black')
    # plt.tight_layout()

    # # Show the plot
    # plt.show()

def prices_trunc():
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

    df1 = get_df('year_month_rec_trunc')
    show_plot(df1, 'year_month_rec_trunc', 'Received Year-Month Coefficients')

    # df = get_df('year_month_rec_trunc_dtc_x_ym')
    # show_plot(df, 'year_month_rec_trunc_dtc_x_ym', 'Received Year-Month Coefficients less days to completion effect')

def prices_trunc_dtc():
    def get_df(file_name):
        df = pd.read_csv(f'./regressions/{file_name}.csv')
        return df

    def show_plot(df, file_name):
        print(f"Plot: {file_name}")
        df = df[df['index'].str.startswith("weeks_to_completion:C(year_month)")]
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
        # Add labels and title
        plt.xlabel('Year-Month')
        plt.ylabel('Percent Change')
        plt.title('Impact of days to completion on price')
        # plt.xticks(rotation=45)
        # plt.grid(axis='y')
        plt.axhline(y=0, color='black')
        plt.tight_layout()
        plt.axvline(x=pd.to_datetime('2022-12-15'))
        plt.axvline(x=pd.to_datetime('2022-05-15'))
        # Show the plot
        plt.savefig(f'./price_{file_name}.png')
        plt.show()

    # df1 = get_df('year_month_rec_trunc')
    # show_plot(df1, 'year_month_rec_trunc')

    df = get_df('year_month_rec_trunc_dtc_x_ym')
    show_plot(df, 'year_month_rec_trunc_dtc_x_ym')

def prices_completed():
    dates = [
        '2022-02-01', '2022-03-01', '2022-04-01', '2022-05-01', '2022-06-01',
        '2022-07-01', '2022-08-01', '2022-09-01', '2022-10-01', '2022-11-01',
        '2022-12-01', '2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01',
        '2023-05-01', '2023-06-01', '2023-07-01', '2023-08-01', '2023-09-01',
        '2023-10-01', '2023-11-01', '2023-12-01', '2024-01-01', '2024-02-01',
        '2024-03-01', '2024-04-01', '2024-05-01', '2024-06-01'
    ]


    df = pd.read_csv('./regressions/year_month_comp.csv')

    df = df[df['index'].str.startswith("C(year_month")]

    df['year_month'] = df['index'].astype('str').str.extract(r'(\d{4}-\d{2})')[0].astype("datetime64[ns]")

    dummy_value = df[df['year_month'] == '2022-05-01']['coef'].values[0]

    df['coef'] -= dummy_value
    df['ci_lower'] = df['[0.025'] - dummy_value
    df['ci_upper'] = df['0.975]'] - dummy_value

    x = df['year_month']
    fig, ax = plt.subplots()
    ax.plot(x, df['coef'])
    ax.fill_between(
        x, df['ci_lower'], df['ci_upper'], color='b', alpha=.15)
    fig.autofmt_xdate(rotation=45)

    # Add labels and title
    plt.xlabel('Year-Month')
    plt.ylabel('Dollars')
    plt.title('Completed Year-Month Coefficients with 95% Confidence Intervals')
    # plt.xticks(rotation=45)
    # plt.grid(axis='y')
    plt.axhline(y=0, color='black')
    plt.axvline(x=pd.to_datetime('2022-12-15'))
    plt.axvline(x=pd.to_datetime('2022-05-15'))
    plt.axvline(x=pd.to_datetime('2023-04-15'))
    plt.tight_layout()

    # Show the plot
    plt.show()

def avg_queue():

    df = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
    # df = df[df['app_received'] > 0]

    df = df.astype({'year_month': 'datetime64[ns]'})
    df = df[df['year_month'] > '2020-12']

    qdf = pd.read_csv('./data/queue.csv')
    qdf = qdf.astype({'year_month': 'datetime64[ns]'})
    qdf.set_index(['year_month', 'queue', 'service_city', 'installer_name'], inplace=True)

    df = df.join(qdf, on=['year_month', 'queue', 'service_city', 'installer_name'], how='left', rsuffix='_right')
    # plt.scatter(df['year_month'], df['queue'])
    # plt.show()

    binwidth = 10

    qdf = qdf.reset_index()
    qdf=qdf[qdf['app_received'] >0]
    # print(qdf)
    # print(qdf.loc[qdf[qdf['year_month'] == '2022-04']['queue'].idxmax()])
    # print(qdf.loc[qdf[qdf['year_month'] == '2023-04']['queue'].idxmax()])
    # return
    fig, ax = plt.subplots(2, 1, sharey=True, sharex=True)
    data = qdf[qdf['year_month'] == '2022-04']['queue']
    ax[0].hist(data, bins=range(int(min(data)), int(max(data)+1) + binwidth, binwidth))
    # ax.hist(df[df['year_month'] == '2022-04']['queue'], histtype="step",  bins=50, cumulative=True)
    plt.gca().set_yscale("log")
    # plt.show()
    data = qdf[qdf['year_month'] == '2023-04']['queue']
    ax[1].hist(data, bins=range(int(min(data)), int(max(data)+1) + binwidth, binwidth))
    plt.gca().set_yscale("log")
    plt.show()

    fig, ax = plt.subplots(2, 1, sharey=True)
    data = df[df['year_month'] == '2022-04']['queue']
    ax[0].hist(data, bins=50)
    ax[0].set_title("April 2022")

    plt.gca().set_yscale("log")

    data = df[df['year_month'] == '2023-04']['queue']
    ax[1].hist(data, bins=50)
    ax[1].set_title("April 2023")
    plt.suptitle("Distribution of Queues")
    plt.gca().set_yscale("log")
    plt.show()

    queue = df.groupby(['year_month'])['queue'].aggregate('mean')

    days_to_completion = df.groupby(['year_month'])['days_to_completion'].aggregate('mean')
    print(days_to_completion)
    total_projects = df.groupby(['year_month'])['app_received'].aggregate('sum')

    df_installers_county = df.groupby(['year_month', 'installer_name', 'service_county'])[['app_received', 'app_approved']].aggregate('sum')
    df_installers_county = df_installers_county.reset_index()
    avg_projects_county = df_installers_county[df_installers_county['app_approved'] >0].groupby(['year_month'])['app_approved'].aggregate('mean')



    fig, ax = plt.subplots(2, figsize=(10, 6))
    ax1 = ax[0]
    ax1.set_title('Avg Queues, # Projects, and Avg Days to Completion')
    # ax2 = ax[0].twinx()
    ax1.plot(queue, color='red', label="Queue")

    ax1.plot(avg_projects_county, color='black', label="Avg projects")
    ax2 = ax[1]
    ax2.plot(days_to_completion, label="Days to Completion")
    ax1.legend()
    ax2.legend()


    # ax3 = ax[1]
    # ax3.set_title("Entering, Exiting and Active Firms")
    # # ax3.plot(firms_entered)
    # ax3.plot(entering_firms_count, color='red')
    # ax3.plot(exiting_firms_count, color='blue')
    # ax3.plot(active_firms, color='black')
    # ax2.plot(total_projects, color='green')

    # plt.xlabel("Date")
    # plt.ylabel("Average Queue")
    # plt.title("Average queue length for all firms taking on new clients")
    # plt.xticks(rotation=45)
    plt.show()

def firm_entry():

    apps = pd.read_csv('./data/applications_cleaned.csv')
    # apps = apps[apps['app_received'] > 0]
    apps['firm_enter_date'] =apps['firm_enter_date'].astype('datetime64[ns]')
    apps['firm_exit_date'] =apps['firm_exit_date'].astype('datetime64[ns]')
    apps['entrant_week'] = apps['firm_enter_date'] - pd.to_timedelta(apps['firm_enter_date'].dt.day_of_week , unit='d')
    apps['exit_week'] = apps['firm_exit_date'] - pd.to_timedelta(apps['firm_exit_date'].dt.day_of_week , unit='d')
    # apps['entrant_week'] = apps['firm_enter_date'].dt.strftime("%Y-%W")

    apps['entrant_week'] = pd.to_datetime(apps['entrant_week'], format='%Y-%m-%d')
    apps['exit_week'] = pd.to_datetime(apps['exit_week'], format="%Y-%m-%d")

    # Entrances by state
    apps_enter = apps.groupby('firm_identifier')['entrant_week'].min().reset_index()
    apps_exit = apps.groupby('firm_identifier')['exit_week'].max().reset_index()

    apps_enter = apps_enter[apps_enter['entrant_week'] >= '2021-01']
    apps_enter = apps_enter[apps_enter['entrant_week'] <= '2024-06']
    apps_exit = apps_exit[apps_exit['exit_week'] >= '2021-01']
    apps_exit = apps_exit[apps_exit['exit_week'] <= '2024-06']

    entrants_by_week = apps_enter.groupby('entrant_week')['firm_identifier'].nunique()
    exits_by_week = apps_exit.groupby('exit_week')['firm_identifier'].nunique()


    fig, ax = plt.subplots(2)
    ax[0].plot(entrants_by_week, 'r', label="Entrances")
    ax[0].plot(exits_by_week, 'b', label="Exits")
    ax[0].legend()

    ax[0].set_title("State Level", fontsize=20)
    plt.suptitle("Entrants and exits by week", fontsize=24)
    ax[0].set_xlabel("Date", fontsize=16)
    ax[0].set_ylabel("Count", fontsize=16)

    apps_enter = apps.groupby(['firm_identifier', 'service_county', 'pop'])['entrant_week'].min().reset_index()
    apps_exit = apps.groupby(['firm_identifier', 'service_county', 'pop'])['exit_week'].max().reset_index()

    entrants_by_week_county = apps_enter.groupby(['entrant_week', 'service_county', 'pop'])['firm_identifier'].nunique().reset_index()
    entrants_by_week_county['count_mils'] = entrants_by_week_county['firm_identifier'] # / entrants_by_week_county['pop'] * 1000000
    exits_by_week_county = apps_exit.groupby(['exit_week', 'service_county', 'pop'])['firm_identifier'].nunique().reset_index()
    exits_by_week_county['count_mils'] =  exits_by_week_county['firm_identifier'] #/ exits_by_week_county['pop'] * 1000000

    # add zeros
    counties = apps_enter['service_county'].unique()

    rows_enter = []
    rows_exit = []
    for week in range(52):
        for year in [2020, 2021, 2022, 2023, 2024]:
            if year == 2024 and week >=26:
                continue
            d = f"{year}-{week}"
            r = dt.datetime.strptime(d + '-1', "%Y-%W-%w").strftime("%Y-%m-%d")
            for county in counties:
                week_entrants = entrants_by_week_county[entrants_by_week_county['entrant_week'] == r]
                if len(week_entrants[week_entrants['service_county'] == county]) == 0:
                    rows_enter.append({'entrant_week': r, 'service_county': county, 'count_mils': 0})

                week_exits = exits_by_week_county[exits_by_week_county['exit_week'] == r]
                if len(week_exits[week_exits['service_county'] == county]) == 0:
                    rows_exit.append({'exit_week': r, 'service_county': county, 'count_mils': 0})

    new_df_enter = pd.DataFrame(rows_enter)
    new_df_exit = pd.DataFrame(rows_exit)
    new_df_enter['entrant_week'] = pd.to_datetime(new_df_enter['entrant_week'])
    new_df_exit['exit_week'] = pd.to_datetime(new_df_exit['exit_week'])



    entrants_by_week_county = pd.concat([entrants_by_week_county, new_df_enter])
    exits_by_week_county = pd.concat([exits_by_week_county, new_df_exit])
    entrants_by_week_county = entrants_by_week_county.sort_values('entrant_week')
    exits_by_week_county = exits_by_week_county.sort_values('exit_week')

    entrants_by_week_county = entrants_by_week_county[entrants_by_week_county['entrant_week'] >= '2021-01']
    entrants_by_week_county = entrants_by_week_county[entrants_by_week_county['entrant_week'] <= '2024-06']
    exits_by_week_county = exits_by_week_county[exits_by_week_county['exit_week'] >= '2021-01']
    exits_by_week_county = exits_by_week_county[exits_by_week_county['exit_week'] <= '2024-06']

    avg_entrants = entrants_by_week_county.groupby(['entrant_week'])['count_mils'].mean()
    avg_exits = exits_by_week_county.groupby(['exit_week'])['count_mils'].mean()

    # fig, ax = plt.subplots()
    ax[1].plot(avg_entrants, 'r', label="Entrances")
    ax[1].plot(avg_exits, 'b', label="Exits")
    ax[1].legend()

    ax[1].set_title("County Level", fontsize=20)
    plt.xlabel("Date", fontsize=16)
    plt.ylabel("Count", fontsize=16)

    plt.savefig(f'./firm_entry_exit.png')
    plt.show()

    # df = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')



    # installers_by_price = df.groupby(['installer_name'])['total_cost'].aggregate('mean')
    # most_expensive_installers = installers_by_price[installers_by_price > 6*installers_by_price.std()]
    # most_expensive_installers = most_expensive_installers.reset_index()
    # df_installers_county = df.groupby(['year_month', 'installer_name', 'service_county'])[['app_received', 'app_approved']].aggregate('sum')
    # df_installers_county = df_installers_county.reset_index()
    # df = df[~df['installer_name'].isin(most_expensive_installers['installer_name'])]
    # # # df = df[df['total_cost'] < 100000]

    # costs = df.groupby('installer_name')['total_cost'].aggregate('mean')

    # counts = df.groupby('installer_name')['app_received'].aggregate('count')

    # plt.scatter(counts, costs)
    # b, a = np.polyfit(counts, costs, deg=1)
    # xseq = np.linspace(0, 8000, num=200)
    # plt.plot(xseq, a + b * xseq, color="k", lw=2.5)
    # plt.suptitle("Avg price of installed job by number of installations")
    # plt.show()




    # df_installers = df.groupby()
    # df = apps

    # num_installers = df_installers_county.groupby(['year_month', 'service_county'])['installer_name'].aggregate('count')
    # num_installers = num_installers.reset_index()
    # num_installers = num_installers.groupby(['year_month'])['installer_name'].aggregate('mean')
    # avg_projects = df[df['app_approved'] >0].groupby(['year_month'])['app_approved'].aggregate('mean')


    # # print(df[df['app_received'] > 0])
    # firms_entered = df[df['app_received'] > 0].groupby(['year_month', 'service_county'])['installer_name'].nunique()
    # firms_entered = firms_entered.reset_index().groupby('year_month')['installer_name'].aggregate('mean')
    # # firms_entered_2 = firms_entered.reset_index().groupby('year_month')['installer_name'].aggregate('mean')

    # entering_firms = df[df.loc[:, 'entrant_month'] == df.loc[:, 'year_month']]
    # entering_firms_county_count = entering_firms.groupby(['year_month', 'service_county'])['installer_name'].nunique().reset_index()
    # entering_firms_county_count = entering_firms_county_count.groupby(['year_month'])['installer_name'].aggregate('mean')
    # entering_firms_all_count = entering_firms.groupby(['year_month'])['installer_name'].nunique().reset_index()
    # entering_firms_all_count = entering_firms_all_count.groupby(['year_month'])['installer_name'].aggregate('mean')

    # def std(data):
    #     return np.std(data)

    # exiting_firms = df[df.loc[:, 'exit_date'] == df.loc[:, 'year_month']]
    # exiting_firms_county_count = exiting_firms.groupby(['year_month', 'service_county'])['installer_name'].nunique().reset_index()
    # exiting_firms_county_count = exiting_firms_county_count.groupby(['year_month'])['installer_name'].aggregate(['mean', std])
    # print(exiting_firms_county_count)
    # exiting_firms_all_count = exiting_firms.groupby(['year_month'])['installer_name'].nunique().reset_index()
    # exiting_firms_all_count = exiting_firms_all_count.groupby(['year_month'])['installer_name'].aggregate(['mean'])

    # active_firms = df[df['app_received'] > 0]
    # active_firms_county = active_firms.groupby(['year_month', 'service_county'])['installer_name'].nunique().reset_index()
    # active_firms_county = active_firms_county.groupby(['year_month'])['installer_name'].aggregate(['mean', std])
    # print(active_firms_county)
    # active_firms_all = active_firms.groupby(['year_month'])['installer_name'].nunique().reset_index()
    # active_firms_all = active_firms_all.groupby(['year_month'])['installer_name'].aggregate('mean')

    # fig, ax = plt.subplots(2, figsize=(10, 6))
    # ax1 = ax[0]
    # ax1.set_title("Entering, Exiting and Active Firms State")
    # # ax1.plot(firms_entered)
    # ax1.plot(entering_firms_all_count, color='red', label="Entering")
    # ax1.plot(exiting_firms_all_count, color='blue', label="Exiting")
    # # ax1.plot(active_firms_all, color='black', label="Active")
    # ax1.legend()
    # ax1.axvline(x=pd.to_datetime('2022-12-15'))
    # ax1.axvline(x=pd.to_datetime('2023-04-13'))

    # ax3 = ax[1]
    # ax3.set_title("Entering, Exiting and Active Firms by county")
    # # ax3.plot(firms_entered)
    # ax3.plot(entering_firms_county_count, color='red', label="Entering")
    # ax3.plot(exiting_firms_county_count, color='blue', label="Exiting")
    # # ax3.plot(active_firms_county, color='black', label="Active")
    # ax3.legend()
    # ax3.axvline(x=pd.to_datetime('2022-12-15'))
    # ax3.axvline(x=pd.to_datetime('2023-04-13'))
    # # ax2.plot(total_projects, color='green')

    # plt.xlabel("Date")
    # # plt.ylabel("Average Queue")
    # # plt.title("Average queue length for all firms taking on new clients")
    # # plt.xticks(rotation=45)
    # plt.show()


def largest_vs_avg():
    df = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
    # df = df[df['app_received'] > 0]
    # print(df['service_county'].unique())
    df = df[df['service_county'] == 'riverside']
    # df = df.astype({'year_month': 'datetime64[ns]', 'is_largest_firm': 'bool'})
    df = df[df['year_month'] > '2021-12']



    num_apps = df.groupby(['year_month', 'installer_name'])['app_received'].aggregate('sum').reset_index()
    num_apps_comp = df.groupby(['year_month', 'installer_name'])['app_approved'].aggregate('sum').reset_index()

    N = 5
    temp_df = num_apps.groupby('year_month')['app_received'].nlargest(N).reset_index()
    top_N = temp_df.groupby('year_month')['app_received'].aggregate('sum')

    temp_df = num_apps_comp.groupby('year_month')['app_approved'].nlargest(N).reset_index()
    top_N_comp = temp_df.groupby('year_month')['app_approved'].aggregate('sum')


    # df['largest_firm'] = df.groupby(['year_month'])[['app_received']].transform(lambda x: x==x.max())
    # print(df['largest_firm', 'installer_name'])
    # return


    # qdf = pd.read_csv('./data/queue.csv')
    # qdf = qdf.astype({'year_month': 'datetime64[ns]'})
    # qdf.set_index(['year_month', 'queue', 'service_city', 'installer_name'], inplace=True)

    # df = df.join(qdf, on=['year_month', 'queue', 'service_city', 'installer_name'], how='left', rsuffix='_right')

    aggregate = df.groupby(['year_month'])['app_received'].aggregate('sum')
    # aggregate = aggregate[aggregate['app_received'] >0].groupby(['year_month'])['app_received']#.aggregate('mean')
    aggregate_comp = df.groupby(['year_month'])['app_complete'].aggregate('sum')
    # aggregate_comp = aggregate_comp[aggregate_comp['app_complete'] >0].groupby(['year_month'])['app_complete']#.aggregate('mean')

    largest_apps = num_apps.groupby('year_month')['app_received'].aggregate('max')
    largest_comps = num_apps.groupby('year_month')['app_received'].aggregate('max')
    # largest_proj = df[df['is_largest_firm'] == True].groupby(['service_county', 'year_month'])['app_received'].aggregate('sum').reset_index()
    # largest_proj = largest_proj.groupby('year_month')['app_received'].aggregate('mean')

    not_largest_proj = aggregate - top_N
    not_largest_comp = aggregate_comp - top_N_comp

    # largest_proj_comp = df[df['is_largest_firm'] == True].groupby(['service_county', 'year_month'])['app_complete'].aggregate('sum').reset_index()
    # largest_proj_comp = largest_proj_comp.groupby('year_month')['app_complete'].aggregate('mean')

    # not_largest_proj_comp = df[df['is_largest_firm'] == False].groupby(['service_county', 'year_month', 'installer_name'])['app_complete'].aggregate('sum').reset_index()
    # not_largest_proj_comp = not_largest_proj_comp.groupby('year_month')['app_complete'].aggregate('mean')



    fig, ax = plt.subplots(3, figsize=(10, 9))

    fig.suptitle("Market Structure -- Riverside County")

    ax0 = ax[0]
    ax0.set_title("Aggregate Avg Projects")

    ax0.plot(aggregate, label="Received")
    ax0.set_ylabel("Number of Projects")
    ax0.plot(aggregate_comp, color='red', label="Completed")
    ax0.legend()



    ax1 = ax[1]
    ax1.set_title('Total Number of Projects Received')
    ax1.plot(top_N, label=f'Largest {N}')
    # ax2 = ax1.twinx()
    ax1.plot(not_largest_proj, color='red', label="All but")
    ax1.legend()
    # ax1.set_ylabel("Largest Firm")
    # ax2.set_ylabel("All But Largest Firm")

    ax3 = ax[2]
    ax3.plot(top_N_comp, label=f"Largest {N}")
    ax3.set_title('Total Number of Projects Completed')
    # ax4 = ax3.twinx()
    ax3.plot(not_largest_comp, color='red', label="All but")
    ax3.legend()
    # ax3.set_ylabel("Largest Firm")
    # ax4.set_ylabel("All But Largest Firm")
    plt.show()

def four_firm_concentration():
    df = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
    df['queue'] = df['queue'].fillna(0)
    df = df.astype(const.TYPE_DICT_AGG)
    df = df[df['service_city'] == "san diego"]
    df = df[df['year_month'] <= '2023-05']
    df = df[df['year_month'] > '2022-05']
    # df = df[df['NEM_tariff'] == '2.0']

    df_total_rev = df.groupby('installer_name')['total_cost'].aggregate("sum").reset_index()

    print(df_total_rev.nlargest(10, 'total_cost'))

    df_total_rev = df_total_rev.sort_values('total_cost')

    top_four = df_total_rev['total_cost'].nlargest(4)

    top_4_total = sum(top_four)
    total = sum(df_total_rev['total_cost'])
    print(top_4_total)
    print(total)

    print(top_4_total/total)


def queue_heat_map():

    df = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')
    # df = df[df['app_received'] > 0]

    df = df.astype({'year_month': 'datetime64[ns]'})
    df = df[df['year_month'] > '2021-12']

    qdf = pd.read_csv('./data/queue.csv')
    qdf = qdf.astype({'year_month': 'datetime64[ns]'})
    qdf = qdf[qdf['year_month'] > '2021-12']
    qdf = qdf[qdf['year_month'] >= qdf['entered_date']]
    qdf = qdf[qdf['year_month'] <= qdf['exit_date']]

    qdf['count'] = qdf['queue']
    qdf_grouped = qdf.groupby(['year_month', 'queue'])['count'].aggregate('count').reset_index()
    qdf_grouped['log_count'] = np.log(qdf_grouped['count'])
    print(qdf_grouped)
    # qdf.set_index(['year_month', 'queue', 'service_city', 'installer_name'], inplace=True)

    # df = df.join(qdf, on=['year_month', 'queue', 'service_city', 'installer_name'], how='left', rsuffix='_right')
    plt.axvline(x=pd.to_datetime('2022-12-15'))
    plt.axvline(x=pd.to_datetime('2023-04-13'))


    plt.scatter(qdf_grouped['year_month'], qdf_grouped['queue'],alpha=0.5)
    plt.title('Distribution of Queues though time')
    plt.xlabel('Date')
    plt.ylabel('Queue Length')
    plt.show()

def ccci():
    df = pd.read_csv('./data/CCCI_08_24.csv')
    df['date'] = df[['year', 'month']].apply(lambda row: '-'.join(row.values.astype(str)), axis=1)
    df = df.astype({'date': 'datetime64[ns]'})

    plt.plot(df.date, df.ccci)
    plt.axvline(x=pd.to_datetime('2022-12-15'))
    plt.axvline(x=pd.to_datetime('2023-04-13'))
    plt.show()


def hhi():
    df = pd.read_csv('./data/aggregate_by_city_installer_ts.csv')


    def get_hhi(df, deliminator="service_county"):

        count_sales_installer = df.groupby([deliminator, 'installer_name'])['app_received'].aggregate('sum').reset_index()

        count_sales_all = count_sales_installer.groupby([deliminator])['app_received'].aggregate('sum').to_dict()
        counties = count_sales_installer[deliminator].unique()

        # print(count_sales_installer)
        # print(count_sales_all)
        hhis_dict = {}

        for county in counties:
            if count_sales_all[county] > 0:
                hhis_dict[county] = sum(
                    count_sales_installer[count_sales_installer[deliminator] == county]['app_received']**2/count_sales_all[county]**2
                )
        # print(hhis_dict)

        hhis = hhis_dict.values()

        average = sum(hhis)/len(hhis)

        stdev = sum([(h - average)**2 for h in hhis]) / len(hhis)
        print(f"Average HHI at {deliminator} level: ")
        print(average)

        print(f"Std Dev: {stdev}")
        print(f"Max HHI: {max(hhis)}")

    df1 = df[(df['year_month'] > "2021-05") & (df['year_month'] <= "2022-05")]
    df2 = df[(df['year_month'] > "2022-05") & (df['year_month'] <= "2023-05")]
    df3 = df[(df['year_month'] > "2022-12") & (df['year_month'] <= "2023-12")]
    df4 = df[(df['year_month'] > "2023-05") & (df['year_month'] <= "2024-05")]
    get_hhi(df1)
    get_hhi(df2)
    get_hhi(df3)
    get_hhi(df4)
    get_hhi(df1, 'service_city')
    get_hhi(df2, 'service_city')
    get_hhi(df3, 'service_city')
    get_hhi(df4, 'service_city')
    # get_hhi(df1, 'service_zip')
    # get_hhi(df2, 'service_zip')
    # get_hhi(df3, 'service_zip')


def iou_chart():
    apps = pd.read_csv('./data/applications_cleaned.csv')
    ious = pd.read_csv('./data/monthly_iou_interconnection_time.csv')
    ious = ious.astype({'year_month': 'datetime64[ns]'})
    ious['year_month'] = ious['year_month'].dt.strftime('%Y-%m')
    ious['iou'] = ious['iou'].str.lower()

    apps_grouped = apps.groupby(['iou', 'year_month_approved'])['days_to_completion'].mean().reset_index()
    apps_count = apps.groupby(['iou', 'year_month_approved'])['app_id'].count().reset_index()
    apps_grouped = pd.merge(apps_grouped, apps_count, how='left', on=['iou', 'year_month_approved'])
    apps_grouped = apps_grouped.rename(columns={'year_month_approved':'year_month'})
    apps_grouped = pd.merge(apps_grouped, ious, how='left', on=['iou', 'year_month'])
    apps_grouped = apps_grouped.astype({'year_month': 'datetime64[ns]'})


    sdge = apps_grouped[apps_grouped['iou'] == 'sdge']
    pge = apps_grouped[apps_grouped['iou'] == 'pge']
    sce = apps_grouped[apps_grouped['iou'] == 'sce']
    print(sdge['year_month'].min())
    print(pge['year_month'].min())
    print(sce['year_month'].min())

    fig, ax = plt.subplots(3,2, figsize=(15,8))
    ax[1][0].set_title('SDG&E - Days to Completion')
    # plt.xticks(rotation=45)
    ax[1][0].plot(sdge['year_month'], sdge['days_to_completion'], label="Days to Completion")
    # plt.xticks(rotation=45)
    ax[1][0].plot(sdge['year_month'], sdge['days'], label="IOU time")

    ax[2][0].set_title('PG&E - Days to Completion')
    ax[2][0].plot(pge['year_month'], pge['days_to_completion'], label="Days to Completion")
    # plt.xticks(rotation=45)
    ax[2][0].plot(pge['year_month'], pge['days'], label="IOU time")
    # plt.xticks(rotation=45)
    ax[0][0].set_title('SCE - Days to Completion')
    ax[0][0].plot(sce['year_month'], sce['days_to_completion'], label="Days to Completion")
    # plt.xticks(rotation=45)
    ax[0][0].plot(sce['year_month'], sce['days'], label="IOU time")
    ax[0][0].legend()

    ax[0][0].axvline(x=pd.to_datetime('2023-04', format='%Y-%m'))
    ax[1][0].axvline(x=pd.to_datetime('2023-04', format='%Y-%m'))
    ax[2][0].axvline(x=pd.to_datetime('2023-04', format='%Y-%m'))

    # plt.xticks(rotation=45)
    ax[1][1].set_title('SDG&E - Count Approved')
    ax[1][1].plot(sdge['year_month'], sdge['app_id'])

    ax[2][1].set_title('PG&E - Count Approved')
    ax[2][1].plot(pge['year_month'], pge['app_id'])

    ax[0][1].set_title('SCE - Count Approved')
    ax[0][1].plot(sce['year_month'], sce['app_id'])

    ax[0][1].axvline(x=pd.to_datetime('2023-04', format='%Y-%m'))
    ax[1][1].axvline(x=pd.to_datetime('2023-04', format='%Y-%m'))
    ax[2][1].axvline(x=pd.to_datetime('2023-04', format='%Y-%m'))
    ax[0][0].tick_params(labelrotation=45)
    ax[1][0].tick_params(labelrotation=45)
    ax[2][0].tick_params(labelrotation=45)
    ax[0][1].tick_params(labelrotation=45)
    ax[1][1].tick_params(labelrotation=45)
    ax[2][1].tick_params(labelrotation=45)
    plt.show()


def largest_x(x):
    apps = pd.read_csv('./data/applications_cleaned.csv')

    grouped = apps.groupby(x)['app_id'].count()
    print(grouped.nlargest(10))
    count = apps['app_id'].count()

    print(grouped.nlargest(10)/count)


def fifo_score(fixed_effect, forward=True):
    apps = pd.read_csv(f'./data/applications_cleaned.csv')

    apps = apps[apps['self_install'] == False]
    apps = apps[apps['size_dc'] >= 1]
    apps = apps[apps['size_dc'] <= 12]
    apps = apps[apps['total_cost'] <= 500000]
    apps = apps[apps['total_cost'] >= 1000]

    apps = apps[apps['is_NEM2'] == True]
    apps_after = apps[apps['app_received'] > '2022-12-15']
    apps_before = apps[apps['app_received'] <= '2022-12-15']
    apps_pre = apps_before[apps_before['app_received'] <= '2022-05-15']
    apps_anticipation = apps_before[apps_before['app_received'] > '2022-05-15']

    def print_stats(apps):
        print(f"FIFO_{fixed_effect} mean, std and % > .95")
        print(apps[f'fifo_score_{fixed_effect}{"" if forward else "_backwards"}'].mean())
        print(apps[f'fifo_score_{fixed_effect}{"" if forward else "_backwards"}'].std())
        print(apps[f'fifo_score_{fixed_effect}{"" if forward else "_backwards"}'].kurtosis())
        print(apps[f'fifo_score_{fixed_effect}{"" if forward else "_backwards"}'].skew())

        print(apps[apps[f'fifo_score_{fixed_effect}{"" if forward else "_backwards"}'] >= .95]['app_id'].count()/apps['app_id'].count())

        print(apps['app_id'].count())

    print("whole sample")
    print_stats(apps)
    print("apps pre-trend")
    print_stats(apps_pre)
    print("apps anticipation")
    print_stats(apps_anticipation)
    print("apps after")
    print_stats(apps_after)
    # print(apps[apps['fifo_score_c'] >= .95]['app_id'].count()/apps['app_id'].count())
    # plt.hist(apps[f'fifo_score_{fixed_effect}'], bins=50)
    # plt.show()

def date_entry():
    apps = pd.read_csv(f'./data/applications_cleaned.csv')



def dist_prices():
    apps = pd.read_csv(f'./data/applications_cleaned.csv')
    apps = apps.astype(
        {
            'app_approved': 'datetime64[ns]',
            'app_complete': 'datetime64[ns]',
            'app_received': 'datetime64[ns]',
            'firm_enter_date': 'datetime64[ns]'})
    # apps['installer_months_age__county'] = ((apps['app_received']-apps['firm_enter_date']).dt.days +1)/30
    # apps = apps[apps['year_month'] == '2024-04']
    # apps = pd.read_csv(f'./data/self_installed_cleaned.csv')
    apps = apps[apps['size_dc'] >= 1]
    apps = apps[apps['size_dc'] <= 12]
    apps = apps[apps['total_cost'] <= 300000]
    apps = apps[apps['total_cost'] >= 2000]

    # apps = apps[apps['cost_per_watt'] <= 30]
    apps['log_cpw'] = np.log(apps['cost_per_watt'])
    apps = apps.groupby('county_lic')[['cost_per_watt', 'log_cpw']].max()

    fig, ax = plt.subplots(2)
    ax[0].hist(apps['cost_per_watt'], bins=30)
    ax[1].hist(apps['log_cpw'], bins=30)
    ax[0].axvline(apps['cost_per_watt'].median(), color='black')
    ax[1].axvline(apps['log_cpw'].median(), color='black')
    plt.show()


def firm_age_sum():
    apps = pd.read_csv(f'./data/applications_cleaned.csv')

    apps = apps[apps['is_NEM2'] == True]
    apps = apps[apps['app_received'] <= '2023-04-15']
    apps = apps[apps['app_received'] >= '2021-01-01']
    apps = apps[apps['size_dc'] >= 1]
    apps = apps[apps['size_dc'] <= 12]


    bins = [1, 3, 6, 12, 24]

    bins_strs = [f'bin_{b}' for b in bins]
    old_bin = 0
    for b in bins:
        apps[f'bin_{b}'] = (apps['installer_months_age__county'].between(old_bin, b, inclusive='left'))
        old_bin = b


    grouped_full = apps.groupby(bins_strs)['app_id'].count()
    print(grouped_full)
    grouped_full = apps.groupby(bins_strs)['cslb_num'].nunique()
    print(grouped_full)

    grouped_period = apps.groupby(bins_strs + ['pio_TF', 'anticipation_period'])['app_id'].nunique()
    print(grouped_period)

    grouped_period = apps.groupby(bins_strs + ['pio_TF', 'anticipation_period'])['cslb_num'].nunique()
    print(grouped_period)


def snapshot_active_participants():

    apps = pd.read_csv(f'./data/applications_cleaned.csv')
    apps = apps[apps['size_dc'] >= 1]
    apps = apps[apps['size_dc'] <= 12]

    apps_pre = apps[apps['app_received'].between('2022-01-01', '2022-04-01')]
    apps_treat = apps[apps['year_month'].between('2023-01-01', '2023-04-01')]
    apps_post = apps[apps['year_month'].between('2024-01-01', '2024-04-01')]

    groups = [apps_pre, apps_treat, apps_post]
    chart_titles = ["Q1 2022", "Q1 2023", "Q1 2024"]
    counts_by_group = []
    sorter = ['0-3 mo.', '3-6 mo.', '6-9 mo.','9-12 mo.', '12-15 mo.',  '15-36 mo.', '> 36 mo.']
    sorter2 = ['0-3', '3-6', '6-9','9-12', '12-15',  '15-18', '18-24', '24-36',  '> 36']
    labels = {1: '0-1 mo.', 3:'0-3 mo.', 6:'3-6 mo.', 9:'6-9 mo.',12:'9-12 mo.', 15:'12-15 mo.', 36:'15-36 mo.', 100000:'> 36 mo.'}
    labels2 = {1: '0-1.', 3:'0-3.', 6:'3-6.', 9:'6-9.',12:'9-12.', 15:'12-15.', 18: '15-18', 24: '18-24', 36:'24-36', 48: '36-48', 60:'48-60', 100000:'> 60'}
    bins = [3, 6, 9, 12, 15, 36, 100000]
    explode = [0.1 for _ in bins]

    explode[4] = 0.3


    CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                      '#f781bf', '#a65628', '#984ea3',
                      '#999999', '#e41a1c', '#dede00']

    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return '{v:d}'.format(pct, v=val)
            # return '{:.1f}%\n({v:d})'.format(pct, v=val)
        return my_format

    fig, ax = plt.subplots(nrows=1, ncols=3)
    for i, group in enumerate(groups):
        end_age = group.groupby('cslb_num')['installer_months_age__state'].max().reset_index()

        bins.reverse()
        end_age["bin"] = "> 48 mo."

        def get_bin(x):
            # if x < 1:
            #     return labels[1]
            if x < 3:
                return labels[3]
            elif x < 6:
                return labels[6]
            elif x < 9:
                return labels[9]
            elif x < 12:
                return labels[12]
            elif x < 15:
                return labels[15]
            # elif x < 18:
            #     return labels[18]
            # elif x < 24:
            #     return labels[24]
            elif x < 36:
                return labels[36]
            # elif x < 48:
            #     return labels[48]
            # elif x < 60:
            #     return labels[60]

            return labels[100000]
        end_age['bin'] = end_age['installer_months_age__state'].apply(get_bin)
        print(end_age)
        counts = end_age.groupby('bin')['cslb_num'].count()
        # counts = counts.sort_values('bin')
        counts = counts.reindex(sorter).reset_index()

        patches, texts, autotexts = ax[i].pie(
            counts['cslb_num'], explode=explode, labels=counts['bin'], autopct=autopct_format(counts['cslb_num']),
            colors=CB_color_cycle[:len(bins)],
            # shadow=True,
            startangle=135,
            pctdistance=0.8)
        # [ _.set_fontsize(7) for _ in autotexts ]
        ax[i].set_title(chart_titles[i])

        # print(counts)
        # ax[i].bar(counts['bin'], counts['cslb_num'])
        # ax[i].hist(end_age['installer_months_age__state'], bins=[0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 60])

    # ax[0] = ax[1].twiny()
    # ax[2] = ax[1].twiny()

    # fig.suptitle('Distribution of Active Firm Ages')
    # # Data for the pie chart
    # sizes = [15, 30, 45, 10, 3, 4]
    # # colors = ['red', 'green', 'blue', 'yellow', '']

    # # Create the pie chart
    # plt.pie(
    #     sizes,
    #     explode=explode,
    #     labels=labels,
    #     # colors=colors,
    #     autopct='%1.1f%%',
    #     shadow=True,
    #     startangle=90)

    # Equal aspect ratio ensures that pie is drawn as a circle.
    # plt.axis('equal')

    # Add a title

    # Display the chart
    plt.show()

# ccci()
# clean_tts()
# handle_grouped_installer()
# ca_projects(True)
# ca_projects(False, True)
# prices() # broken
# prices_trunc()
# prices_completed()
# prices_trunc_dtc() # Not useful
# iou_chart()
# avg_queue()
# largest_x('manufacturer')

# largest_x('installer_name')
# four_firm_concentration()
# largest_vs_avg()
# hhi()
# queue_heat_map()
# fifo_score('c')
# fifo_score('fc')
# fifo_score('c', False)
# fifo_score('fc', False)
# dist_prices()
# firm_age_sum()

# ca_projects()
# firm_entry()
snapshot_active_participants()
