import urllib.request
import urllib.parse
import gzip
import json
from datetime import datetime

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


class MetadataListExchangesRequest:
    def endpoint(self):
        return '/exchanges'


class MetadataListSymbolsRequest:
    def endpoint(self):
        return '/symbols'


class MetadataListAssetsRequest:
    def endpoint(self):
        return '/assets'


class CoinAPIv2:

    DEFAULT_HEADERS = {
        'Accept': 'application/json'
    }

    def __init__(self, api_key, headers = dict(), client_class=HTTPClient):
        self.api_key        = api_key
        header_apikey       = {'X-CoinAPI-Key': self.api_key}
        self.headers        = {**self.DEFAULT_HEADERS, **headers, **header_apikey}
        self.client_class   = client_class

    def ohlcv_historical_data(self, symbol_id, period_id, start, end, limit=10000):

        """ Esta funcion regresa los datos historicos (candlesticks) de symbol_id entre las fechas start y end.
            Hay que mencionar que esta función  en especifico no permite especifiar horas, minutos y segundos en 
            las fechas, por lo que toma como valor predeterminado 00:00:00 (inicio del día)
            Args:
                - symbol_id: coinAPI pair ID
                - period_id: tiempo del periodo (Ej. 5MIN)
                - start: fecha de inicio
                - end: fecha de fin
                - limit: limite de datos que se puede pedir
                
            El formato de las fechas es el siguiente: {"year":int(aaaa), "month":int(mm), "day":int(dd)}
        """

        start_iso           = datetime.date(datetime(start['year'], start['month'], start['day'])).isoformat()
        end_iso             = datetime.date(datetime(end['year'], end['month'], end['day'])).isoformat()
        query_parameters    = {'period_id': period_id, 'time_start': start_iso, 'time_end':end_iso, 'limit':limit}
        request             = OHLCVHistoricalDataRequest(symbol_id, query_parameters)
        client              = self.client_class(request.endpoint(), self.headers, request.query_parameters)

        return client.perform()

    def metadata_list_exchanges(self):
        request = MetadataListExchangesRequest()
        client = self.client_class(request.endpoint(), self.headers)
        return client.perform()

    def metadata_list_symbols(self):
        request = MetadataListSymbolsRequest()
        client = self.client_class(request.endpoint(), self.headers)
        return client.perform()

    def metadata_list_assets(self):
        request = MetadataListAssetsRequest()
        client = self.client_class(request.endpoint(), self.headers)
        return client.perform()

