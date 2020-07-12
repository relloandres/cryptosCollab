
import numpy as np

def days_till_month(month, leap_year):
    """Returns the number of days from the start of the year to month"""

    days_per_month = {'01':31,'02':28,'03':31,'04':30,'05':31,'06':30,'07':31,'08':31,'09':30,'10':31,'11':30,'12':31}
    
    if leap_year:
        days_per_month['02'] = 29
    
    days = 0
    for i in range(1,month):
        days += days_per_month['%02i' %i]

    return days

def date_to_sec(date):
    """"    
        Returns the total number of seconds from the firs second of 2017 (year zero) to date. 
        date must be in the format: 2018-10-19T06:00:00.0000000Z
    """
    sec_in_one_year         = 31536000
    sec_in_one_day          = 86400
    sec_in_one_hr           = 3600
    sec_in_one_min          = 60
    year_zero               = 2017
    sec_in_one_leap_year    = sec_in_one_year + sec_in_one_day


    total_secs              = 0
    
    d = date.split('T')
    d1 = d[0].split('-')                # d1 = [year, month, day]
    d2 = d[1].split('.')[0].split(':')  # d2 = [hour, min, sec]

    year_count = int(d1[0])-year_zero

    for i in range(1, year_count+1):
        if (i+1)%4==0:
            total_secs += sec_in_one_leap_year
        else:
            total_secs += sec_in_one_year
    
    if (year_count+1)%4==0:
        leap_year = True
    else:
        leap_year = False

    total_secs += days_till_month(int(d1[1]), leap_year)*sec_in_one_day
    total_secs += (int(d1[2])-1)*sec_in_one_day
    total_secs += int(d2[0])*sec_in_one_hr
    total_secs += int(d2[1])*sec_in_one_min
    total_secs += int(d2[2])
        
    return total_secs

def num_periods(time_lapse,start,end):
    """time_laps can be:
        - 5MIN
        - 15MIN
        - 30MIN
        - 1H"""
    lapses = {"5MIN":300, "15MIN":900, "30MIN":1800, "1H":3600}
    start_m = date_to_sec(start)
    end_m = date_to_sec(end)
    periods = (end_m - start_m)/lapses[time_lapse]
    return periods

def get_empty_periods(data, period_length):
    
    """ Esta función se encarga de recibir una lista con diccionarios dentro (data), donde cada diccionario tiene
        la información de mercado para un periodo de longitud period_length. Las propiedades de estos diccionarios 
        que nos son relevantes ahora son: time_period_start y time_period_end. Idealmente el elemento i e i+1 de 
        data deberían estar separados por un solo periodo, sin emabrgo a veces existen periodos sin información 
        y se forman lagunas. El problema es que para muchos algoritmos estas lagunas pueden llevar a mal interpretaciones
        de los datos por lo que se tienen que detectar. Esta función regresa dos listas. La primera tiene los indices 
        donde comeinza una laguna. Por ejemplo si el indice k se encuentra en esta lista esto quiere decir que entre el 
        elemento k y k+1 hay una laguna. La segunda lista tiene la misma longitud que la primera lista y tiene la longitud
        en numero de periodos de cada laguna.
        
        period_length = str (ejemplo: 5MIN)
    """

    

    # Correspondencia de periodos en segundos
    periods_in_secs = {"1MIN":60, "5MIN":300}

    # Obtener fecha de inicio y fin
    data_start_date = data[0]['time_period_start']
    data_end_date   = data[-1]['time_period_end']

    # Obtener indices de inicio de periodos vacios y numero de periodos vacios correspondientes
    # Obtenemos todas las fechas de inicio de period (en segundos)
    o_dates = []
    for i,date in enumerate(data):
        o_dates.append(date_to_sec(date['time_period_start']))

    #Obtenemos las diferencias entre las fechas entre elementos consecutivos
    diff = []
    for i in range(len(o_dates)-1):
        diff.append((o_dates[i+1]-o_dates[i])/periods_in_secs[period_length])
    diff = np.array(diff)

    #Escogemos los indices cuya diferencia sea mayor a la del periodo temporal que se este utilizando
    o_dates_diff = np.array(diff)
    o_dates_diff = (o_dates_diff != 1)
    diff_index = np.where(o_dates_diff == True)[0]
    
    # El numero de periodos entre fecha de inicio y fecha de fin debe ser igual al del total de datos más los correpondientes a lagunas
    consistent_data = num_periods(period_length, data_start_date, data_end_date) - (len(data)+diff.sum()-diff.shape[0])

    if consistent_data == 0:

        start_idx_empty_periods = diff_index.tolist()
        length_empty_periods    = (diff[diff_index]-1).tolist()

    else:

        start_idx_empty_periods = []
        length_empty_periods    = []
        
        
    return start_idx_empty_periods, length_empty_periods

def get_valid_data_idx(data, period_length, N):

    """ Esta función se encarga de recibir una lista con diccionarios dentro (data), donde cada diccionario tiene
        la información de mercado para un periodo de longitud period_length. Las propiedades de estos diccionarios 
        que nos son relevantes ahora son: time_period_start y time_period_end. Idealmente el elemento i e i+1 de 
        data deberían estar separados por un solo periodo, sin emabrgo a veces existen periodos sin información 
        y se forman lagunas. 
        Esta función regresa un arreglo con subarreglos. Los subarreglos contienen los indices de los elementos de 
        data que tienen N elementos consecutivos antes de ellos y cada subarreglo contiene esta información en un 
        intervalo definido por dos lagunas consecutivas. De esta forma si el indice i se encuentra en un sub arreglo 
        esto implica que los elementos i-N,i-N+1,...,i estan separados por un solo periodo cada uno o dicho de otra 
        forma son datos consecutivos.  
    """

    valid_data_idx = []

    # Numero total de elementos en data
    data_lenght = len(data)

    # Informacion de lagunas de data
    data_empty_periods_idx, data_empty_periods_len  = get_empty_periods(data, period_length)
    number_of_empty_periods                         = len(data_empty_periods_idx)

    if number_of_empty_periods==0:
        valid_data_idx.append(np.arange(N,data_lenght).tolist())

    else:
        # Agregamos 2 indices para tomar en cuenta periodos ante de la primera laguna y despues de la ultima
        data_empty_periods_idx.insert(0,-1)
        data_empty_periods_idx.append(data_lenght-1)
        number_of_empty_periods += 2

        for i in range(number_of_empty_periods-1):

            current_period_start_idx    = data_empty_periods_idx[i]
            current_period_end_idx      = data_empty_periods_idx[i+1]
            current_period_len          = current_period_end_idx - current_period_start_idx

            if current_period_len>N:
                start_valid_idx = current_period_start_idx + 1 + N
                end_valid_idx   = current_period_end_idx + 1
                valid_data_idx.append(np.arange(start_valid_idx, end_valid_idx).tolist())

    return valid_data_idx


            

    


    
        
        




