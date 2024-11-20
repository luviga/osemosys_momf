# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 09:02:14 2024

@author: ClimateLeadGroup
"""

# Abrir el archivo de entrada y leer todas las líneas
with open('archivo_entrada.txt', 'r') as file:
    lines = file.readlines()

# Crear un archivo de salida con los valores modificados
with open('archivo_salida.txt', 'w') as file:
    for line in lines:
        # Dividir la línea por comas y reemplazar el último valor numérico por 999
        parts = line.strip().split(',')
        if parts[-1].replace('.', '', 1).isdigit():  # Verificar si el último elemento es numérico
            parts[-1] = '999'
        # Escribir la línea modificada al archivo de salida
        file.write(','.join(parts) + '\n')

print("El archivo de salida se ha creado con los valores modificados.")
