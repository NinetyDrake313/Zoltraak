import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

NA = 'SN'

# ==== Configuración ====
# Ajusta estas rutas según tu entorno:
RADIUS_CSV = f'csv/A_Val/{NA}/RAD/averages.csv'                 # CSV con columnas: in_bin, radius
ENERGY_CSV = f'csv/A_Val/{NA}/Ec/averages.csv'                 # CSV con columnas: in_bin, energy_avg
OUTPUT_CSV = f'csv/A_Val/{NA}/normalized_by_area.csv'    # CSV de salida con energía normalizada por área


def normalize_from_two_csv(radius_csv: str, energy_csv: str, output_csv: str) -> pd.DataFrame:
    """
    Lee dos CSVs separados:
      - radius_csv con columnas ['in_bin', 'radius']
      - energy_csv con columnas ['in_bin', 'energy_avg']
    Combina por 'in_bin', calcula área de cada bin, energía por unidad de área,
    guarda el resultado en output_csv y devuelve el DataFrame normalizado.
    """
    # Leer CSVs
    df_radius = pd.read_csv(radius_csv)
    df_energy = pd.read_csv(energy_csv)

    # Combinar en un solo DataFrame por 'in_bin'
    df = pd.merge(
        df_radius[['in_bin', 'radius']],
        df_energy[['in_bin', 'energy_avg']],
        on='in_bin',
        how='inner'
    )

    # Calcular área de círculo para cada bin
    df['area'] = np.pi * df['radius']**2
    # Calcular energía por unidad de área, evitando división por cero
    df['energy_per_area'] = df.apply(
        lambda row: row['energy_avg'] / row['area'] if row['area'] > 0 else 0.0,
        axis=1
    )

    # Guardar CSV
    out_cols = ['in_bin', 'radius', 'energy_avg', 'area', 'energy_per_area']
    df[out_cols].to_csv(output_csv, index=False)
    print(f"[OK] CSV normalizado guardado en '{output_csv}'")

    return df[out_cols]


if __name__ == '__main__':
    # Normalizar y obtener DataFrame
    df_norm = normalize_from_two_csv(RADIUS_CSV, ENERGY_CSV, OUTPUT_CSV)

    # Graficar in_bin vs energy_per_area
    plt.figure(figsize=(8, 6))
    plt.plot(
        df_norm['in_bin'],
        df_norm['energy_per_area'],
        marker='o', linestyle='-'
    )
    plt.xlabel('Profundidad z (cm)')
    plt.ylabel('Energy per area')
    plt.title('Energía por unidad de área ')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
