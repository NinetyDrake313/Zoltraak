#!/usr/bin/env python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

# =====================================================
# Funciones de cálculo
# =====================================================

def compute_enclosing_radius(db_path: str, bin_size: float) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT x, y, z FROM particulas", conn)
    conn.close()

    z_min, z_max = df['z'].min(), df['z'].max()
    bins = np.arange(z_min, z_max + bin_size, bin_size)

    results = []
    for i in range(len(bins) - 1):
        z0, z1 = bins[i], bins[i + 1]
        df_bin = df[(df['z'] >= z0) & (df['z'] < z1)]
        radius = df_bin.empty and 0.0 or np.sqrt((df_bin['x']**2 + df_bin['y']**2)).max()
        results.append({
            'in_bin': round(i * bin_size, 2),
            'radius': radius
        })

    return pd.DataFrame(results)


def compute_bragg_curve(db_path: str, bin_size: float) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT z, Ec FROM particulas", conn)
    conn.close()

    z_min, z_max = df['z'].min(), df['z'].max()
    bins = np.arange(z_min, z_max + bin_size, bin_size)

    results = []
    for i in range(len(bins) - 1):
        z0, z1 = bins[i], bins[i + 1]
        df_bin = df[(df['z'] >= z0) & (df['z'] < z1)]
        energy_avg = df_bin.empty and 0.0 or df_bin['Ec'].abs().mean()
        results.append({
            'in_bin': round(i * bin_size, 2),
            'energy_avg': energy_avg
        })

    return pd.DataFrame(results)

# =====================================================
# Función principal con argparse
# =====================================================

def main():
    parser = argparse.ArgumentParser(
        description="Genera CSV de radios y curva de Bragg dinámicos"
    )
    parser.add_argument(
        '--input-db', '-i', required=True,
        help="Ruta a la base de datos SQLite (por ejemplo 'BUENA_DATA/PRUEBA.db')"
    )
    parser.add_argument(
        '--radius-csv', '--radius-output', '-r', required=True,
        help="Ruta de salida para CSV de radios (in_bin,radius)"
    )
    parser.add_argument(
        '--bragg-csv', '--bragg-output', '-b', required=True,
        help="Ruta de salida para CSV de curva de Bragg (in_bin,energy_avg)"
    )
    parser.add_argument(
        '--bin-radius', type=float, default=0.05,
        help="Tamaño del bin para cálculo de radios"
    )
    parser.add_argument(
        '--bin-bragg', type=float, default=0.05,
        help="Tamaño del bin para curva de Bragg"
    )
    args = parser.parse_args()

    # Asegurar que existan directorios de salida
    os.makedirs(os.path.dirname(args.radius_csv), exist_ok=True)
    os.makedirs(os.path.dirname(args.bragg_csv),  exist_ok=True)

    # Calcular y guardar radios
    df_r = compute_enclosing_radius(args.input_db, args.bin_radius)
    df_r[['in_bin', 'radius']].to_csv(args.radius_csv, index=False)
    print(f"[OK] Radios guardados en '{args.radius_csv}'")

    # Calcular y guardar curva de Bragg
    df_b = compute_bragg_curve(args.input_db, args.bin_bragg)
    df_b[['in_bin', 'energy_avg']].to_csv(args.bragg_csv, index=False)
    print(f"[OK] Curva de Bragg guardada en '{args.bragg_csv}'")

    # (Opcional) Graficar curva de Bragg
    try:
        plt.figure(figsize=(8, 6))
        plt.plot(df_b['in_bin'], df_b['energy_avg'], marker='o', linestyle='-')
        plt.xlabel('Profundidad z (bin start)')
        plt.ylabel('Promedio de energía perdida |Ec|')
        plt.title('Curva de Bragg - Promedio de Ec positivo')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception:
        pass

if __name__ == '__main__':
    main()
