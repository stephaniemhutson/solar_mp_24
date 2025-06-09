import pandas as pd

cities = pd.read_csv('./data/us-cities-table.csv')

cities['county'] = cities['county'].str.lower()
cities['city'] = cities['city'].str.lower()

cities = cities[[
    'pop2024',
    'pop2023',
    'pop2022',
    'pop2020',
    'growth',
    'city',
    'county',
    'densityMi',
]]

cities.to_csv('./data/cities_popultion.csv')


license = pd.read_csv('./data/CSLB_license_numbers.csv')


license['LicenseNumber'] = license['LicenseNumber'].astype(int)

apps = pd.read_csv('./data/applications_cleaned.csv')

apps[]
