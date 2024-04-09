# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 11:56:55 2024

@author: andreysava19
"""

import os

def compare_files_in_directory(directory_path):
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

    # Comparación de archivos, similar a lo anterior
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()
        
        if file1_lines == file2_lines:
            print(f"Los archivos del escenario {directory_path} son iguales.")
        else:
            print(f"Los archivos del escenario {directory_path} son diferentes.")
            # Opcional: mostrar las diferencias
            for i, (line1, line2) in enumerate(zip(file1_lines, file2_lines)):
                if line1 != line2:
                    print(f"Diferencia en la línea {i+1}:")
                    print(f"Archivo 1: {line1.strip()}")
                    print(f"Archivo 2: {line2.strip()}")

compare_files_in_directory('NDP/5')

