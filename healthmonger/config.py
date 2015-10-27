"""Configuration for healthmonger. It contains app configuration for running
the API service. It also contains data source and schema information.
"""
import os
from whoosh import fields

# Configuration for healthmonger's API service and data fetching tool
debug = True

APP_PATH = os.path.dirname(os.path.realpath(__file__))+"/../"

DOWNLOAD_PATH = APP_PATH + "data/"

INDEX_PATH = APP_PATH + "index/"


DEFAULT_QUERY_LIMIT = 10

API_VERSION = 1

DATA_SOURCES = {
    # 'historical': ('xls', 'https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/NationalHealthExpendData/Downloads/Tables.zip'), # noqa
    'age_and_gender': ('csv', 'https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/NationalHealthExpendData/Downloads/2010AgeandGenderCSVfiles.zip')  # noqa
}

TABLE_SCHEMA = {
    'age_and_gender': fields.Schema(
        id=fields.ID(stored=True),
        age_group=fields.KEYWORD,
        service=fields.KEYWORD,
        gender=fields.KEYWORD,
        category=fields.KEYWORD,
        payer=fields.KEYWORD,
        timestamp=fields.ID)
}
