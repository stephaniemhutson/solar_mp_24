import pandas as pd

apps = pd.read_csv('./data/self_installed_cleaned.csv')
apps_agg = apps.groupby([ 'service_county', 'service_city', 'year_month', 'has_battery'])[['cost_per_watt']].aggregate('mean')
apps_count = apps.groupby([ 'service_county', 'service_city', 'year_month', 'has_battery'])[['app_id']].aggregate('count')
apps_agg = apps_agg.join(apps_count)

apps_agg = apps_agg.rename(columns={'app_id': 'count'})

apps_agg.to_csv('./data/self_installed_zip_ym.csv')
