import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Conectar a la base de datos y cargar los datos
ruta_bd = "/home/ninetydrake313/Documentos/Tesis/SM/simulacion_particulasCARBON.db"
conn = sqlite3.connect(ruta_bd)
query = "SELECT * FROM particulas"
df = pd.read_sql_query(query, conn)
conn.close()

# 2. Calcular las diferencias en posiciones y la distancia recorrida
df[['dx', 'dy', 'dz']] = df[['x', 'y', 'z']].diff().fillna(0)
df['dl'] = np.sqrt(df['dx']**2 + df['dy']**2 + df['dz']**2)

# 3. Calcular la profundidad acumulada y la energía acumulada
df['depth'] = df.groupby('particle_id')['dl'].cumsum()
df['Ec_cumulative'] = df.groupby('particle_id')['Ec'].cumsum()

# 4. Definir los bins de profundidad
num_bins = 100
max_depth = df['depth'].max()
bins = np.linspace(0, max_depth, num_bins + 1)
df['depth_bin'] = pd.cut(df['depth'], bins=bins, labels=False, include_lowest=True)

# 5. Calcular la pérdida de energía media por bin
bragg_data = df.groupby('depth_bin')['Ec'].mean()

# 6. Reindexar para asegurar que todos los bins estén presentes
bragg_data = bragg_data.reindex(range(num_bins), fill_value=0).reset_index()

# 7. Calcular el centro de los bins
bragg_data['depth_center'] = bins[:-1] + (bins[1] - bins[0])/2

# 8. Opcional: Convertir la profundidad a centímetros
bragg_data['depth_center_cm'] = bragg_data['depth_center'] * 0.1  # metros a centímetros

# 9. Plotear la curva de Bragg
plt.figure(figsize=(10, 6))
plt.plot(bragg_data['depth_center_cm'], bragg_data['Ec'], label='400 MeV/u')
plt.xlabel('Profundidad (cm)')
plt.ylabel('Pérdida de Energía (MeV)')
plt.title('Curva de Bragg simulacion de iones de carbono en Agua')
plt.legend()
plt.grid(True)
# Guardar el gráfico
plt.savefig('/home/ninetydrake313/Documentos/Tesis/Curva de braggCARBON.png')
plt.show()


