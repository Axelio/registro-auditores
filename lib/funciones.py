# -*- coding: utf-8 -*-
import datetime


def fecha_futura(fecha):
    '''
    Funcion para determinar si la fecha es o no futura.
    La función debe retornar True si la fecha es futura.
    '''
    # Fecha actual
    fecha_actual = datetime.date.today()
    # Se revisa si la fecha del formulario es futura
    # (fecha de formulario mayor a la actual)
    if fecha >= fecha_actual:
        # Se retorna True dado que la fecha facilitada es futura
        return True
    else:
        return False


def fecha_pasada(fecha):
    '''
    Funcion para determinar si la fecha es o no pasada.
    La función debe retornar True si la fecha es pasada.
    '''
    # Fecha actual
    fecha_actual = datetime.date.today()
    # Se revisa si la fecha del formulario es pasada
    # (fecha de formulario menor a la actual)
    if fecha <= fecha_actual:
        # Se retorna True dado que la fecha facilitada es pasada
        return True
    else:
        return False
