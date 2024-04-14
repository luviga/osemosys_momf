# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 11:56:55 2024

@author: andreysava19
"""

import os

import os
import pandas as pd

def compare_files_in_directory(directory_path, output_type='df'):
    # Lista todos los archivos en el directorio especificado
    all_files = os.listdir(directory_path)
    # Filtra los archivos para obtener solo aquellos con extensión .txt
    txt_files = [file for file in all_files if file.endswith('.txt')]
    
    if len(txt_files) != 2:
        print("El directorio debe contener exactamente dos archivos .txt para comparar.")
        return

    # Construye las rutas completas a los archivos
    file1_path = os.path.join(directory_path, txt_files[0])
    file2_path = os.path.join(directory_path, txt_files[1])

    # Comparación de archivos
    differences = []
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()
        
        if file1_lines == file2_lines:
            print(f"Los archivos del escenario {directory_path} son iguales.")
        else:
            print(f"Los archivos del escenario {directory_path} son diferentes.")
            # Guarda las diferencias según el tipo de salida elegido
            for i, (line1, line2) in enumerate(zip(file1_lines, file2_lines)):
                if line1 != line2:
                    diff = {"line_number": i+1, "file1": line1.strip(), "file2": line2.strip()}
                    differences.append(diff)

    # Retornar las diferencias en el formato deseado
    if output_type == 'list':
        return differences
    elif output_type == 'dict':
        return {i: diff for i, diff in enumerate(differences)}
    elif output_type == 'df':
        return pd.DataFrame(differences)
    else:
        raise ValueError("output_type debe ser 'list', 'dict' o 'df'")


differences = compare_files_in_directory('PIUP/BAU/1', 'df')