import glob
import os
import pandas as pd

# ==== Configuración ====
# Ajusta fácilmente estos valores:
FOLDER_PATH = 'csv/A_Val/a10/RAD/'        # Carpeta que contiene los CSV a procesar
PATTERN = 'i_*.csv'                      # Patrón de archivos (ej. 'a_*.csv')
OUTPUT_CSV = 'csv/A_Val/a10/RAD/averages.csv'              # Nombre del CSV de salida con los promedios


def aggregate_csv_averages(folder_path: str, pattern: str, output_csv: str) -> None:
    """
    Lee todos los CSVs en `folder_path` que coincidan con `pattern`,
    concatena los resultados y calcula el promedio de las columnas
    'radius' y 'energy_avg' por cada 'in_bin', guardando el resultado en `output_csv`.
    """
    # Construir lista de archivos
    search_pattern = os.path.join(folder_path, pattern)
    csv_files = glob.glob(search_pattern)
    if not csv_files:
        print(f"No se encontraron archivos con el patrón '{pattern}' en '{folder_path}'")
        return

    # Leer y concatenar
    df_list = []
    for file in csv_files:
        df = pd.read_csv(file)
        # Mantener solo columnas relevantes si existen
        cols = ['in_bin']
        if 'radius' in df.columns:
            cols.append('radius')
        if 'energy_avg' in df.columns:
            cols.append('energy_avg')
        df_list.append(df[cols])

    combined = pd.concat(df_list, ignore_index=True)

    # Agrupar por in_bin calculando media
    df_mean = combined.groupby('in_bin', as_index=False).mean()

    # Guardar resultado
    df_mean.to_csv(output_csv, index=False)
    print(f"[OK] Resultados promedio guardados en '{output_csv}'")


if __name__ == '__main__':
    # Ejecutar agregación usando la configuración
    aggregate_csv_averages(
        folder_path=FOLDER_PATH,
        pattern=PATTERN,
        output_csv=OUTPUT_CSV
    )
