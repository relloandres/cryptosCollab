from datetime import datetime
import json
import numpy as np
import os

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


def save_empty_periods_info(file_path, period_length, dest_file_path):
    
    """ Lo que esta funcion hace es escribir la informacion de periodos vacios del archivo 
        file_path al archivo dest_file_path (el cual puede o no existir). Si 
        hay alguna inconsistencia entre el numero de periodos en los datos y las fechas de inicio y 
        final no se escribira nada al archivo final y se obtendra un mensaje de error para que se revisen
        los datos con más detalle."""

    # Verificar si dest_file_path existe
    dest_file_exists = os.path.exists(dest_file_path)
    
    # Correspondencia de periodos en segundos
    periods_in_secs = {"1MIN":60, "5MIN":300}
    
    # Cargar información
    with open(file_path) as csv_file:
        data = json.load(csv_file)
    
    # Obtener fecha de inicio y fin
    data_start_date = data[0]['time_period_start']
    data_end_date   = data[-1]['time_period_end']
    
    # Obtener numero de periodos sin información
    number_empty_periods = num_periods(period_length, data_start_date, data_end_date) - len(data)

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
    consistent_data = num_periods('5MIN', data_start_date, data_end_date) - (len(data)+diff.sum()-diff.shape[0])

    if consistent_data == 0:
        
        file_name = file_path.split("/")[-1].split(".")[0]
        file_info = {
                    "start_date":data_start_date,
                    "end_date":data_end_date,
                    "period_length":period_length,
                    "total_empty_periods":number_empty_periods,
                    "start_idx_empty_periods":diff_index.tolist(),
                    "length_empty_periods":diff[diff_index].tolist()
                    }
        
        if dest_file_exists:
            
            with open(dest_file_path) as f:
                dest_file = json.load(f)
            
            dest_file[file_name] = file_info
            
        else:
            dest_file = {file_name:file_info}
        
        with open(dest_file_path, 'w') as f:
            json.dump(dest_file,f)
            
        print('Empty periods info saved')   
        return True
    
    else:
        
        print('Inconsistent data, empty periods info not saved')
        return False


def update_data_info(data_info, exchange_name, symbol_name, new_date, new_exchange=False, new_symbol=False):

    
    """This function updates info in file coinapypy\Data\info_data.txt. It has 6 arguments:
            - data_info: old version of info_data.txt in dict form (must be open first)
            - exchange_name: name of the exchange the info will be updated of
            - symbol_name: symbol the info will be updated of
            - new_date: new date to update. If it is a new end date new_date="dd-mm-yyy". If a new symbol is to be registered
              then new_date=("dd-mm-yyy","dd-mm-yyyy")
            - new_exchange: True if new exchange is to be registered
            - new_symbol: True if new symbol is to be registered"""

    updated_data_info = data_info.copy()
    
    if new_exchange:
        if len(new_date)==2:
            updated_data_info[exchange_name]={symbol_name:[new_date[0],new_date[1]]}
        else:
            print("No update made: new_date variabel must be a tuple of two elements (StartDate,EndDate)")
            return None
    else:
        if new_symbol:
            if len(new_date)==2:
                updated_data_info[exchange_name][symbol_name]=[new_date[0],new_date[1]]  
            else:
                print("No update made: new_date variabel must be a tuple of two elements (StartDate,EndDate)")
                return None
        else:
            updated_data_info[exchange_name][symbol_name][1]=new_date
    
    return updated_data_info

