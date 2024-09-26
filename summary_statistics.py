import pandas as pd
import collections
import pprint
import datetime as dt
import matplotlib.pyplot as plt

def clean_tts():
    tts_df = pd.read_csv("./data/TTS_10_2023.csv")

    tts_df = tts_df[tts_df.total_installed_price > 5]
    tts_df = tts_df[tts_df.city != -1]
    tts_df = tts_df[tts_df.city != "-1"]

    print("Summary Statistics of the Tracking the Sun")



    pprint.pp(tts_df.columns)
    # module_manufacturer_1 = collections.Counter(tts_df['module_manufacturer_1'])

    # pprint.pp(module_manufacturer_1)
    # module_manufacturer_2 = collections.Counter(tts_df['module_manufacturer_2'])

    # pprint.pp(module_manufacturer_2)
    # module_manufacturer_3 = collections.Counter(tts_df['module_manufacturer_3'])

    # pprint.pp(module_manufacturer_3)
    print("Total installed price by City, State where count > 4")
    # state_city_tts = tts_df.groupby(['state', 'city'])

    # print(state_city_tts.groupby(['state', 'city'])['total_installed_price'].describe())

    installer_tts = tts_df[tts_df['installer_name'] != -1]
    installer_tts = installer_tts[installer_tts['installer_name'] != '-1']
    installer_tts['installer_name'] = installer_tts['installer_name'].str.upper()
    installer_tts['city'] = installer_tts['city'].str.upper()
    installer_tts['state'] = installer_tts['state'].str.upper()

    # print(installer_tts.groupby(['state', 'city', 'installer_name'])['total_installed_price'].describe())

    grouped_installer = pd.DataFrame(installer_tts.groupby(['state', 'city', 'installer_name', ])['total_installed_price'].describe())

    grouped_installer.to_csv("./data/grouped_installer.csv")

def handle_grouped_installer():
    grouped_installer = pd.read_csv("./data/grouped_installer.csv")
    grouped_installer = grouped_installer[grouped_installer['installer_name'] != "UNKNOWN"]


    # print(collections.Counter(list(grouped_installer["state"])))
    grouped_installer = grouped_installer.groupby(['state', 'city']).filter(lambda x: x['city'].count() > 50)

    # state_cities =
    print(grouped_installer.sort_values("count"))

    print(grouped_installer[grouped_installer['city'] == "SAN FRANCISCO"].sort_values("count")[350:])

    # for state, city in state_cities:
    #     market = grouped_installer[grouped_installer["state"] == state and grouped_installer["city"] == city]
    #     print(f"{state}, {city}")
    print(collections.Counter(list(grouped_installer["state"])))

    print(collections.Counter(list(grouped_installer[grouped_installer['city'] == "SAN DIEGO"][grouped_installer['count'] > 3]["city"])))
    print(grouped_installer[grouped_installer['city'] == "SAN DIEGO"][grouped_installer['count'] > 3].sort_values("count"))
    print(collections.Counter(list(grouped_installer[grouped_installer['city'] == "BAKERSFIELD"][grouped_installer['count'] > 3]["city"])))
    print(grouped_installer[grouped_installer['city'] == "YOLO"][grouped_installer['count'] > 3].sort_values("count"))


    san_diego = grouped_installer[grouped_installer['city'] == "SAN DIEGO"].to_dict()
    bakersfield = grouped_installer[grouped_installer['city'] == "BAKERSFIELD"].to_dict()
    sacramento = grouped_installer[grouped_installer['city'] == "SACRAMENTO"].to_dict()
    yolo = grouped_installer[grouped_installer['city'] == "YOLO"].to_dict()
    san_francisco = grouped_installer[grouped_installer['city'] == "SAN FRANCISCO"].to_dict()

    # print(hhi(san_diego))
    # print(hhi(bakersfield))
    # print(hhi(sacramento))
    # print(hhi(san_francisco))
    # print(hhi(yolo))
    hhis = []
    for city in set(grouped_installer['city']):

        hhis.append(hhi(grouped_installer[grouped_installer['city'] == city].to_dict()))

    # print(hhis)
    # print(len([h for h in hhis if h > 1000])/len(hhis))
    plt.hist(hhis)
    plt.suptitle("HHI Index, California cities with more than 50 projects")

    plt.show()


def hhi(market_data):
    income = {}

    # for key, value in market_data.items()
    count = len(market_data['state'])

    for index in market_data['installer_name'].keys():
        # print(market_data['installer_name'])
        installer = market_data['installer_name'][index]
        mean_cost = market_data['mean'][index]
        num_proj = market_data['count'][index]

        income[installer] = mean_cost * num_proj


        # print(installer)
        # data = market_data[market_data['installer_name'] == installer]
        # income.push(data['count'] * data['mean'])
    # print(income)
    total_income = sum(income.values())
    return sum([(i*100/total_income)**2 for i in income.values()])

def ca_projects():
    projects = pd.read_csv('./data/truncated_concated_applications.csv')


    # print(list(projects.columns))
    # # return
    projects_app = projects[projects['App Received Date'].notnull()]
    # projects = projects[projects['Cancelled Date'].isna()]

    print(projects_app['App Received Date'][2])
    # projects = projects[projects['Program Year'].isin([2021, 2022, 2023])]
    # df['year'] = pd.DatetimeIndex(df['ArrivalDate']).year

    # df['month'] = pd.DatetimeIndex(df['ArrivalDate']).month
    # projects['iso_date'] = projects['Date Received'].isoformat()
    # 01/31/23 16:05:46.159983
    projects_app['year_month'] = pd.to_datetime(projects_app['App Received Date'], format='%Y-%m-%d').dt.strftime('%Y-%m')
    # project_months = projects.groupby(projects[''])
    projects_app = projects_app[projects_app['year_month'] >= '2019-01']
    # print(projects)
    count_df = pd.DataFrame(projects_app.groupby('year_month')['year_month'].describe()).reset_index()
    # print(count_df.columns)

    fig, ax = plt.subplots(nrows=1, ncols=2)

    ax[0].tick_params(labelrotation=90)
    ax[1].tick_params(labelrotation=90)

    ax[0].bar(count_df['year_month'], count_df['count'])
    ax[0].title.set_text("Applications Received for new solar in California")

    # ax[0].xticks(rotation = 90)
    # ax[0].suptitle("Applications Received for new solar in California")
    # plt.show()


    projects_inter = projects[projects['App Complete Date'].notnull()]

    # 01/31/23 16:05:46.159983
    projects_inter['year_month'] = pd.to_datetime(projects_inter['App Complete Date'], format='%Y-%m-%d').dt.strftime('%Y-%m')
    # project_months = projects.groupby(projects[''])
    projects_inter = projects_inter[projects_inter['year_month'] >= '2019-01']
    # projects_inter = projects_inter[projects_inter['NEM Tariff'] == 2]
    # print(projects)
    count_df = pd.DataFrame(projects_inter.groupby('year_month')['year_month'].describe()).reset_index()
    # print(count_df.columns)



    ax[1].bar(count_df['year_month'], count_df['count'])
    ax[1].title.set_text("Applications Completed for new solar in California")
    # ax[1].xticks(rotation = 90)
    # ax[1].suptitle(
    # plt.xticks(rotation=90)
    plt.show()

# clean_tts()
# handle_grouped_installer()
ca_projects()

