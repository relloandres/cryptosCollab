En este documento se explica cual es la estructura de los directorios y archivos que sirven para obtener y limpiar datos obtenidos de https://www.coinapi.io/. A partir de ahora el directorio root se supondr� como: /coinAPI







DIRECTORIO /data

Este directorio no se sincroniza con github ya que contiene los datos historicos de diferentes cryptomoneda y diferentes exchanges, lo cual eventualmente puede ser muy pesado. Lo �nico que se comenta aqu� es la estructura recomendad que deber�a tener este directorio. Dentro de el debe haber un directorio por cada exchange y dentro de estos otro directorio con pares de monedas. Un ejemplo para el par BTC-USDT en Binance es el siguiente:

	data/binance/BTC-USDT

Dentro del directorio /BTC-USDT se guardan los archivos JSON obtenidos de coinAPI que tienen los historiales historicos. Estos archivos se guardan con la siguiente convenci�n en el nombre:

[exchange]_[order_type]_[base_currency]_[quoted_currency]_[start_date]_[end_date].json

	- Base currency hace referencia a la moneda a la cual se define el precio en funci�n de quoted currency. Dicho en otras palabras cuanto en quoted currency se 		necesita para comprar base_currency.
	- Order type generalmente ser� SPOT (compra venta com�n).
	- El formato de las fechas es el siguiente: dd-mm-aa y estas indican las fechas de inicio y fin para las que fueron solicitados datos a coinAPI (La hora de 		ambas fechas es 00:00:00 i.e. inicio del d�a)

Un ejmplo de el nombre de un archivo es el siguiente: 

	BINANCE_SPOT_BTC_USDT_01-01-18_04-02-18.json

Adem�s de estos archivos tambi�n se puede guardar uno con el siguiente nombre: 

	[exchange]_[order_type]_[base_currency]_[quoted_currency]_[start_date]_[end_date]_headers.json

el cual tiene la respuesta al request HTTP que se hizo para obtener cada uno de los archivos con datos. La mayor utilidad que tienen estos archivos es monitorear el l�mite de requests y la fecha de renovaci�n de estas. 


Dentro de cada directorio de par de monedas se guarda un archivo llamado emptyPeriodsInfo.txt (nombre sugerido) que guarda la informaci�n general de los datos que se han obtenido hasta ahora. Esta informaci�n esta estructurada en formato JSON de la siguiente manera:

{
"file_name":{
	"start_date":str,
	"end_date":str,
    	"period_length":str,
    	"total_empty_periods":int,
    	"start_idx_empty_periods":array,
    	"length_empty_periods":array,
    	}
}

	- Las fechas de inicio y fin ("start_date" y "end_date") ahora no son las que se pidieron a coinAPI sino las que entrego. Idealmente estas deber�a coincidir 		pero no siempre pasa. 
	- "Period_length" indica cuanto dura el periodo de los datos ("1MIN", "5MIN", etc.)
	- "total_empty_periods" indoca el n�mero total de periodos sin informaci�n
	- "start_idx_empty_periods" es un arreglo que tiene los indices de los periodos donde comienzan periodos sin informaci�n
	- "length_empty_periods" es un arreglo que indica cuantos periodos vacios hay despu�s de los periodos guardados en start_idx_empty_periods 







DIRECTORIO \symbols

Dentro de este directorio hay un archivo llamado symbols_list.json. Este archivo guarda todos los pares de cryptomonedas para los que se pueden pedir datos en coinAPI. Aqu� se encuentran otros tipos de transacciones como futures. Este archivo es una lista cuyos elementos son diccionarios, se puede abrir como un JSON. 







DIRECTORIO /keys

En este directorio hay un archivo: API_keys.json
Este archivo tiene las diferentes llaves que tengo para pedir datos a coinAPI. Cada llave tiene capacidad de pedir 100 requests







DIRECTORIO /src:

En este directorio se encuentran los archivos fuente que eprmiten comunicarse con coinAPI y guardar la informaci�n obtenida de forma consistente. A continuaci�n se hace una descripci�n general de estos y se ahonda un poco m�s en los m�s �tiles. 

-> coinapi_v2.py
Este archivo sirve para comunicarse con la API de coinAPI y su estructura se obtuvo de https://github.com/coinapi/coinapi-sdk (python-rest). Se obtuvierons solo las funciones y clases que se consideran �tiles por ahora. 

-> helpers.py
Este archivo tiene funciones que ayudan al tratamiento consistente de los datos, sobre todo a poder extraer periodos sin informaci�n dentro de estos.
La �nica funci�n que vale la pena mencionar de este archivo es: 

	save_empty_periods_info(file_path, period_length, dest_file_path)

Esta se encarga de guardar la informaci�n de periodos vac�os de un archivo descargado de coinAPI. La �nica raz�n por la que esta funci�n se tendr�a que usar de forma manual es porque se perdi� o sobreescribi� alg�n archivo que conten�a la informaci�n de periodos vac�os para algun symbol y se tiene que volver a generar. Los argumentos de esta funci�n son los siguientes:

	- file_path: Direcci�n (con nombre) del archivo JSON descargado de coinAPI del cual se quiere guardar la informaci�n de periodos vac�os
	- period_length: Duraci�n del periodo de la informacion en el archivo file_path
	- dest_file_path: Direcci�n (con nombre) del archivo donde se va a guardar la informaci�n de periodos vac�os. Si este archivo no existe ser� creado, de otra forma el existente se actualizar�. Este archivo es un diccionario y cada que se corre esta funci�n se agrega una nueva llave a �l. Esta llave corresponde al nombre de file_paht sin la extenci�n y guarda la siguiente estructura de datos: 

{
"COINBASE_SPOT_BTC_USD_1-1-2018_2-1-2018": {
	"start_date": "2018-01-01T00:00:00.0000000Z", 
	"end_date": "2018-01-02T00:00:00.0000000Z", 
	"period_length": "5MIN", 
	"total_empty_periods": 0.0, 
	"start_idx_empty_periods": [], 
	"length_empty_periods": []
	}
}

A continuaci�n se describe la informaci�n de estos datos:
	- "start_date": Es la fecha de inicio del primero periodo en los datos
	- "end_date": Es la fecha de fin del �ltimo periodo en los datos
	- "period_length": Duraci�n del periodo de los datos
	- "total_empty_periods": El total de periodos sin informaci�n en los datos
	- "start_idx_empty_periods": Arreglo con los �ndices de los datos donde empiezan las lagunas (periodos vacios)
	- "length_empty_periods": Arreglo con el n�mero de periodos de cada laguna en "start_idx_empty_periods"

-> downloadNewData.py
Este archivo es el que se usar� m�s seguido y sirve para descargar datos espec�ficos de coinAPI. A continuaci�n se explica como se tiene que invocar:
	- El primer paso es escoger el par de monedas del cual se quiere informaci�n y de que exchange. Esto se resume en obtener un elemento del archivo "\symbols\symbols_list.json". Un ejemplo es: BINANCE_SPOT_BTC_USDT
	- El siguiente paso es decidir donde se van a guardar los datos y crear directorios para esto si es necesario, se recomienda seguir la estructura descrita para el directorio \data.
	- Posteriormente se tiene que crear un archivo de configuraciones que va a indicar exactamente que datos se van a obtener y donde se va a guardar toda la informaci�n de estos. Este archivo tiene la siguiente estructura: 

		{
    			"api_key":"key",
    			"symbol_id":"BINANCE_SPOT_BTC_USDT", 
    			"period_length":"5MIN", 
   			"start_date":[2,1,2018], 
    			"end_date":[2,1,2018], 
    			"dest_dir_path":"C:/Users/malala/Desktop/Andres/Blockain/Trading/cryptosCollab/dataAcquisition/coinAPI", 
    			"save_headers":false,
			"empty_periods_file_path":"C:/Users/malala/Desktop/Andres/Blockain/Trading/cryptosCollab/dataAcquisition/coinAPI/emptyPeriodsInfo.json"

		}

		A continuaci�n se describen los diferentes elementos de este archivo JSON:
			- api_key: Es la llave que se obtiene de coinAPI
			- symbol_id: Es el symbol que especifica el par de cryptomonedas del cual se desea obtener la informaci�n
			- period_length: Indica la duraci�n del periodo para el cual se desea obtener la informaci�n
			- start_date: Fecha de inicio para obtener los datos [dia,mes,a�o] (La hora es siempre 00:00:00 i.e. el inicio del d�a)
			- end_date: Fecha de fin para obtener los datos [dia,mes,a�o] (La hora es siempre 00:00:00 i.e. el inicio del d�a)
			- dest_dir_path: Directorio donde se guardar� el archivo JSON con los datos (Esta direcci�n debe acabar con el nombre del directorio sin "/" al final)
			- save_headers: true si se quieren guardar los headers del request, de otra forma false
			- empty_periods_file_path: direcci�n (con nombre) del archivo donde se guardar� la informaci�n de los periodos vac�os existenetes en la informaci�n.

	- El �ltimo paso es llamar desde la terminal a este archivo con un �nico argumento el cual corresponde a la direcci�n del archivo de configuraciones. SI este �ltimo se guardo en \temp\configsFile.json por ejemplo entonces para descargar los datos la invocaci�n es la siguiente (suponiendo que nos encontramos en el directorio donde vive downloadNewData.py):

	python downloadNewData.py \temp\configsFile.json

Hay que mencionar que como tenemos llaves gratuitas nuestro tenemos un limite de requests. Este l�mite para el caso de datos historicos es de 10 000 periodos. Sin importar la longitud temporal de estos. De esta forma si estamos trabajando con periodos de 5MIN por ejemplo en total podemos jalar la informaci�n correspondiente a un poco m�s de 34 d�as, pero como la funci�n sirve para d�as completos el m�ximo se considera como 34. 






