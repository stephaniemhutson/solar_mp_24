TYPE_DICT = {
    'app_approved': 'datetime64[ns]',
    'app_complete': 'datetime64[ns]',
    'app_received': 'datetime64[ns]',
    'year_month': 'datetime64[ns]',
    'year_month_comp': 'datetime64[ns]',
    'size_dc': 'float64',
    'size_ac': 'float64',
    'cost_per_watt': 'float64',
    'battery_storage': 'float64',
    'self_install': 'bool',
    'NEM_tariff': 'str',
    'electric_vehicle': 'bool',
    'output_monitoring': 'bool',
    'service_zip': 'category',
    'service_county': 'category',
    'app_id': 'str',
    'pre_id': 'str',
    'mounting_method': 'category',
    'days_to_completion': 'int64',
    'is_largest_firm': 'bool',
    'is_NEM2': 'bool',
    'has_battery': 'bool',
    'service_city': 'str',
    'service_county': 'str',
    'installer_name': 'str',
    'total_cost': 'float64',
    # 'year': 'category'
}

TYPE_DICT_AGG = {
    "service_city": 'str',
    "installer_name": 'str',
    "year_month": 'datetime64[ns]',
    "size_dc": 'float64',
    "battery_storage": 'float64',
    "total_cost": 'float64',
    "is_largest_firm": 'bool',
    "days_to_completion": 'int64',
    "adjusted_price": 'float64',
    "app_received": 'int64',
    "app_complete": 'int64',
    "queue": 'int64',
}
TYPE_DICT_QUEUE = {
    "service_city": 'str',
    "installer_name": 'str',
    "year_month": 'datetime64[ns]',
    "app_received": 'int64',
    "app_complete": 'int64',
    "queue": 'int64',
    "entered_date": 'datetime64[ns]',
    "exit_date": 'datetime64[ns]',
    'active_sales_months': 'int',
    'count_sales': 'int',
}
