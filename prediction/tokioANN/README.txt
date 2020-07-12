Aquí se intentan reproducir los resultados que reportan en el paper tokioANN. A continuación se hace una pequena 
descripción de los archivos del proyecto:


checkValidDataIdx.ipynb
Este archivo creo que lo use para ver como podía seleccionar datos válidos de los obtenidos de coinAPI. Y por validos
me refiero a detectar lagunas y seleccionar solo datos continuos. Este archivo no es nada relevante y eventualmente se
va a eliminar. Solo tengo que revisar que no tenga nada importante.


helpers.py
En este archivo es donde segun yo esta la parte importante de checkValidDataIdx.ipynb. Básciamente aquí se encuentran
la función que sirve para detectar lagunas y seleccionar únicamente datos continuo. Hay que mencionar que además se 
implementaron función para calcular fechas en segundos, esto se hizo debido a que usando la de python había algunas
inconsistencias (o eso recuerdo al menos jajaja).


tokioFunctions.py
En este archivo se encuentran todas las funciones necesarias para construir los indicadores que se usan como datos 
de entrenamiento. Hay que mencionar que en el paper las definiciones de estos indicadores difieren de las definiciones
formales. Por esta razón se pueden encontrar dos funciones diferentes que sirven para construir el mismo indicador, estas
se pueden diferenciar por el nombre. De forma automatica hasta ahora únicamente se tiene implementada la generación 
de los indicadores como (casi) los definen en el paper. 


createTrainingData.ipynb
En este archivo se describe un poco más a detalle como se construyen los datos de entrenamiento y al final se explica
como se hace esto con una sola función.