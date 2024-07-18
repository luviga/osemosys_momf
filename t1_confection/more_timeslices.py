# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 12:13:00 2024

@author: Andrey Salazar
"""

import pandas as pd

# Cargar los datos

# Duplicar cada fila
data = pd.read_csv('C:\\Users\\ClimateLeadGroup\\Desktop\\CLG_repositories\\osemosys_momf\\t1_confection\\A2_Output_Params\\BAU\\SpecifiedDemandProfile.csv')
data_duplicated = data.loc[data.index.repeat(2)].reset_index(drop=True)

# Asignar nuevos valores a la columna TIMESLICE
timeslices = ['DRY', 'RAIN'] * (len(data_duplicated) // 2)
data_duplicated['TIMESLICE'] = timeslices

# Guardar el nuevo DataFrame
data_duplicated.to_csv('C:\\Users\\ClimateLeadGroup\\Desktop\\CLG_repositories\\osemosys_momf\\t1_confection\\A2_Output_Params\\BAU\\SpecifiedDemandProfile.csv', index=False)
