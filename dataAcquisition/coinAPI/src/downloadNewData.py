import sys
import coinapi_v2 as cAPI
import helpers as hp
import json


def main(config_file_path):

    # Cargar archivo JSON con configuraciones de datos a descargar
    with open(config_file_path) as f:
        configs = json.load(f)

    # Construimos variables correspondientes a fechas
    start_date_str  = f'{configs["start_date"][0]}-{configs["start_date"][1]}-{configs["start_date"][2]}'
    end_date_str    = f'{configs["end_date"][0]}-{configs["end_date"][1]}-{configs["end_date"][2]}'
    start_date_dict = {'year':configs["start_date"][2], 'month':configs["start_date"][1], 'day':configs["start_date"][0]}
    end_date_dict   = {'year':configs["end_date"][2], 'month':configs["end_date"][1], 'day':configs["end_date"][0]}

    # Generamos usuario para descargar datos
    headers     = {'Accept-Encoding':'deflat, gzip'}
    cAPI_user   = cAPI.CoinAPIv2(configs["api_key"], headers=headers)

    # Descargamos los datos
    try:
        res, res_headers = cAPI_user.ohlcv_historical_data(configs["symbol_id"],configs["period_length"],start_date_dict,end_date_dict)
    except Exception as e:
        print('Error ocurred: ', e)
        sys.exit(1)

    # Nombre y dreccion donde se guardaran los datos
    data_file_name = f'{configs["symbol_id"]}_{start_date_str}_{end_date_str}'
    data_file_path = f'{configs["dest_dir_path"]}/{data_file_name}.json'

    # Guardar los datos
    with open(data_file_path, 'w') as f:
        json.dump(res, f)

    # Guardar Headers si asi se especifica
    if configs["save_headers"]:

        headers_file_path = f'{configs["dest_dir_path"]}/{data_file_name}_headers.json'
        
        with open(headers_file_path, 'w') as f:
            json.dump(res_headers, f)

    # Guardar información de periodos vacios presentes en los datos
    hp.save_empty_periods_info(data_file_path, configs["period_length"], configs["empty_periods_file_path"])

    return "success"



if __name__ == "__main__":
    main(sys.argv[1])