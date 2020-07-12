import numpy as np
import helpers as hp

def get_return_data(price_data):
    """ Esta funcion regresa 'return data' (referencia en paper) en forma de un arreglo de numpy. El numero de 
        elementos de este arreglo es uno menos que price_data y su primero elementos corresponde al tiempo (indice)
        t=1 (suponiendo que el primer elemento de price_data corresponde a t=0).
        
        La funcion asume lo siguiente: 
            - price_data es un arreglo de numpy
            - price_data tiene al menos 2 elementos"""
    
    past_price_data = price_data[:-1]
    present_price_data = price_data[1:]
    return_data = (present_price_data/past_price_data) - 1
    
    return return_data


def get_formal_EMA_EMSD_data(x, M):
    """ La funcion regresa dos arreglos de numpy con los valores de EMA y EMSD de periodo-M a
        partir de x. Hay que tomar en cuenta que el primer elemento de cada uno de estos arreglos
        corresponde al tiempo (indice) t=M (suponiendo que el primer elemento de x corresponde a t=0)
        con respecto a x. El valor para t=M-1 corresponde al promedio de los primeros M elementos pero
        no se incluye y para tiempos anteriores el valor no esta definido.
        
        La funcion asume lo siguiente:
            - x es un arreglo de numpy
            - x tiene al menos M+1 elementos"""
    
    alpha         = 2/(1+M)
    past_EMA      = x[:M].mean()
    past_EMSD_sqr = 0
    n_elements    = x.shape[0]-M
    EMA_data      = np.zeros(n_elements)
    EMSD_data     = np.zeros(n_elements)
    
    for i in range(n_elements):
        EMA_data[i]   = alpha*x[i+M] + (1-alpha)*past_EMA
        EMSD_sqr      = (1-alpha)*(past_EMSD_sqr + alpha*((x[i+M]-past_EMA)**2))
        EMSD_data[i]  = EMSD_sqr**0.5
        past_EMA      = EMA_data[i]
        past_EMSD_sqr = EMSD_sqr
        
    return EMA_data, EMSD_data


def get_formal_SMMA(x, N):
    """ La funcion regresa un arreglo de numpy con el valor de SMMA de periodo-N de x. 
        Hay que tomar en cuenta que el primer elemento de este arreglo corresponde al tiempo 
        (indice) t=N (suponiendo que el primer elemento de x corresponde a t=0) con respecto 
        a x. El valor para t=N-1 corresponde al promedio de los primeros N elementos pero no se
        incluye y para tiempos anteriores el valor no esta definido.
        
        La funcion asume lo siguiente: 
            - x es un arreglo de numpy
            - x tiene al menos N+1 elementos"""
    
    alpha       = 1/N
    past_SMMA    = x[:N].mean()
    n_elements  = x.shape[0]-N
    SMMA_data   = np.zeros(n_elements)
    
    for i in range(n_elements):
        SMMA_data[i+N] = (x[i] + (N-1)*past_SMMA)/N
        past_SMMA    = SMMA_data[i]
        
    return SMMA_data
    

def get_formal_RSI(x, K):
    
    """ La funcion regresa un arreglo de numpy con los valores de RSI de N-periodo a partir de x. 
        Hay que tomar en cuenta que el primer elemento de este arreglo corresponde al tiempo 
        (indice) t=K+1 (suponiendo que el primer elemento de x corresponde a t=0) con respecto 
        a x. Los valores para t<K+1 estan indefinidos.
        
        La funcion asume que lo siguiente:
            - x es un arreglo de numpy
            - x tiene al menos K+2 elementos"""
    
    n_elements = x.shape[0]
    
    #Tomar en cuenta que aunque el primer elemento de U_data y D_data tiene el valor de 0
    #en realidad esta indefinido
    U_data     = np.zeros(n_elements)
    D_data     = np.zeros(n_elements)
    
    for i in range(1,n_elements):
        U_data[i] = max(x[i] - x[i-1], 0)
        D_data[i] = max(-(x[i] - x[i-1]), 0)
        
    SMMA_U = get_formal_SMMA(U_data[1:],K)
    SMMA_D = get_formal_SMMA(D_data[1:],K)
        
    RS_data = SMMA_U/SMMA_D
    RSI_data = 1/(1+RS_data)
    
    return RSI_data
    
    
def get_paper_EMA_EMSD_data(x, M):
    """ La funcion regresa dos arreglos de numpy con los valores de EMA y EMSD de periodo-M a
        partir de x. Hay que tomar en cuenta que el primer elemento de cada uno de estos arreglos
        corresponde al tiempo (indice) t=M (suponiendo que el primer elemento de x corresponde a t=0) 
        con respecto a x. El valor para t=M-1 corresponde al promedio de los primeros M elementos pero
        no se incluye y para tiempos anteriores el valor no esta definido.
        
        La funcion asume lo siguiente:
            - x es un arreglo de numpy
            - x tiene al menos M+1 elementos"""
    
    alpha         = 2/(1+M)
    past_EMA      = x[:M].mean()
    past_EMSD_sqr = 0
    n_elements    = x.shape[0]-M
    EMA_data      = np.zeros(n_elements)
    EMSD_data     = np.zeros(n_elements)
    
    for i in range(n_elements):
        EMA_data[i]   = alpha*x[i+M] + (1-alpha)*past_EMA
        EMSD_sqr      = (1-alpha)*past_EMSD_sqr + alpha*((x[i+M]-past_EMA)**2)
        EMSD_data[i]  = EMSD_sqr**0.5
        past_EMA      = EMA_data[i]
        past_EMSD_sqr = EMSD_sqr
        
    return EMA_data, EMSD_data


def get_paper_sumR(x, N):
    """ La funcion regresa un arreglo de numpy donde cada elemento representa la suma de N 
        elementos consecutivos de x. Hay que tomar en cuenta que el primer elemento de este 
        arreglo corresponde al tiempo (indice) t=N-1 (suponiendo que el primer elemento de x 
        corresponde a t=0) con respecto a x. Los valores para t<N-1 estan indefinidos.
        
        La funcion asume lo siguiente:
            - x es un arreglo de numpy
            - x tiene al menos N elementos"""
    
    n_elements = x.shape[0]-N+1
    sumR_data  = np.zeros(n_elements)
    
    for i in range(n_elements):
        sumR_data[i] = x[n_elements:n_elements+N].sum()

    return sumR_data


def get_paper_RSI(x, K):
    """ La funcion regresa un arreglo de numpy con los valores de RSI de N-periodo a partir de x. 
        Hay que tomar en cuenta que el primer elemento de este arreglo corresponde al tiempo 
        (indice) t=K-1 (suponiendo que el primer elemento de x corresponde a t=0) con respecto a
        x. Los valores para t<K-1 estan indefinidos.
        
        La funcion asume lo siguiente:
            - x es un arreglo de numpy
            - x tiene al menos K elementos"""
    
    n_elements = x.shape[0]
    
    posR_data  = np.zeros(n_elements)
    negR_data  = np.zeros(n_elements)
    
    for i in range(n_elements):
        posR_data[i] = max(x[i], 0)
        negR_data[i] = max(-x[i], 0)

    PR_data = get_paper_sumR(posR_data,K)
    NR_data = get_paper_sumR(negR_data,K)

    RSI_data = PR_data/(PR_data+NR_data)
    
    return RSI_data


def build_paper_data(historical_data, delta, EMA_periods, RSI_periods):
    
    # Inicializamos todas las variables donde se guardaran los datos de los indicadores
    r_data = []
    EMA_data  = {}
    EMSD_data = {}
    RSI_data  = {}
    
    for M in EMA_periods:
        M_period_key = f"M{M}"
        EMA_data[M_period_key] = []
        EMSD_data[M_period_key] = []

    for K in RSI_periods:
        K_period_key = f"K{K}"
        RSI_data[K_period_key] = []
    
    #Escogemos el numero minimo de periodos consecutivos anteriores que tiene que tener cada periodo valido que se usara
    EMA_required_past_periods = max(EMA_periods) + 1
    RSI_required_past_periods = max(RSI_periods)
    required_past_periods     = max(EMA_required_past_periods,RSI_required_past_periods)
    
    #Definimos el numero minimo de elementos que debe de tener un intervalo de price data para que se puedan obtener
    #datos de entrenamiento de el
    t_start = required_past_periods + delta
    
    # Obtenemos los indices de periodos validos tomando en cuenta lagunas en los datos
    data_valid_idx = hp.get_valid_data_idx(historical_data,"5MIN",required_past_periods)
    
    # Obtenemos los datos de precios validos 
    for valid_interval in data_valid_idx:
        valid_interval_len = len(valid_interval)
        n_useful_periods   = valid_interval_len + required_past_periods
        
        if n_useful_periods >= t_start:
            
            first_useful_idx   = valid_interval[0] - required_past_periods
            current_price_data = np.zeros(n_useful_periods)

            for i in range(n_useful_periods):
                current_price_data[i] = historical_data[first_useful_idx+i]["price_close"]

            # Obtenemos los datos utiles de 'return data'
            current_r_data = get_return_data(current_price_data) 
            r_data += current_r_data[t_start-1:].tolist()
            
            # Obtenemos los datos utiles de EMA y EMSD
            for M in EMA_periods:
                current_EMA_data, current_EMSD_data = get_paper_EMA_EMSD_data(current_r_data, M)
                current_EMA_key = f"M{M}"
                EMA_data[current_EMA_key] += current_EMA_data[t_start-(M+1):].tolist()
                EMSD_data[current_EMA_key] += current_EMSD_data[t_start-(M+1):].tolist()

            # Obtenemos los datos utiles de RSI
            for K in RSI_periods:
                current_RSI = get_paper_RSI(current_r_data, K)
                current_RSI_key = f"K{K}"
                RSI_data[current_RSI_key] += current_RSI[t_start-K:].tolist()

    return r_data, EMA_data, EMSD_data, RSI_data