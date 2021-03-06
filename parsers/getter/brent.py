"""Download Brent FOB price time series from EIA API.

The data is sevral days behind (Oct 5, 2017):

{'date': '2017-10-02', 'freq': 'd', 'name': 'BRENT', 'value': Decimal('55.67')}
{'date': '2017-09-29', 'freq': 'd', 'name': 'BRENT', 'value': Decimal('57.02')}
{'date': '2017-09-28', 'freq': 'd', 'name': 'BRENT', 'value': Decimal('58.80')}
{'date': '2017-09-27', 'freq': 'd', 'name': 'BRENT', 'value': Decimal('58.74')}
{'date': '2017-09-26', 'freq': 'd', 'name': 'BRENT', 'value': Decimal('59.77')}

"""

import json
import parsers.getter.util as util
from parsers.config import EIA_ACCESS_KEY


def make_url(access_key=EIA_ACCESS_KEY):
    series_id = 'PET.RBRTE.D'
    return ("http://api.eia.gov/series/"
            f"?api_key={access_key}"
            f"&series_id={series_id}")


def parse_response(text):
    """Returns list of rows based on response *text*."""
    json_data = json.loads(text)
    return json_data["series"][0]["data"]


def yield_brent_dicts(downloader=util.fetch):
    """Yeilds datapoints as dicts.

    Args:
        downloader(function) - function used to retrieve URL
    """
    url = make_url()
    text = downloader(url)
    for row in parse_response(text):
        yield {"date": util.format_date(row[0], fmt="%Y%m%d"),
               "freq": "d",
               "name": "BRENT",
               "value": util.format_value(row[1])}


if __name__ == "__main__":
    gen = yield_brent_dicts()
    for i in range(14):
        print(next(gen))
