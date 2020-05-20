import urllib.request
import urllib.parse
import gzip
import json

PRODUCTION_URL = 'https://rest.coinapi.io/v1%s'

class HTTPClient:

    def __init__(self, endpoint, headers = dict(), params = dict()):
        self.url = PRODUCTION_URL % endpoint
        self.params = params
        self.headers = headers

    def perform(self):
        resource = self.url

        if self.params:
            query_string = urllib.parse.urlencode(self.params)
            resource = '%s?%s' % (self.url, query_string)

        request = urllib.request.Request(resource, headers=self.headers)
        handler = urllib.request.urlopen(request)
        response_headers = handler.getheaders()
        raw_response = handler.read()

        if 'Accept-Encoding' in self.headers:
            if self.headers['Accept-Encoding'] == 'deflat, gzip':
                raw_response = gzip.decompress(raw_response)

        encoding = handler.info().get_content_charset('utf-8')
        response = json.loads(raw_response.decode(encoding))
        return response, response_headers


class OHLCVHistoricalDataRequest:
    def __init__(self, symbol_id, query_parameters = dict()):
        self.symbol_id = symbol_id
        self.query_parameters = query_parameters

    def endpoint(self):
        return '/ohlcv/%s/history' % self.symbol_id


class CoinAPIv1:
    DEFAULT_HEADERS = {
        'Accept': 'application/json'
    }
    def __init__(self, api_key, headers = dict(), client_class=HTTPClient):
        self.api_key = api_key
        header_apikey = {'X-CoinAPI-Key': self.api_key}
        self.headers = {**self.DEFAULT_HEADERS, **headers, **header_apikey}
        self.client_class = client_class

    def ohlcv_historical_data(self,
                              symbol_id,
                              query_parameters):
        request = OHLCVHistoricalDataRequest(symbol_id, query_parameters)
        client = self.client_class(request.endpoint(),
                                   self.headers,
                                   request.query_parameters)
        return client.perform()