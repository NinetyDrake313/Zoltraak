import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import multiprocessing
import time

start_time = time.time()

# Definir el número de núcleos que deseas usar
num_cores = 20
print(f"Usando {num_cores} núcleos para el procesamiento paralelo.")

# Ruta de la base de datos
ruta_bd = "/home/ninetydrake313/Documentos/Tesis/SM/simulacion_particulas.db"

# Conectar a la base de datos SQLite
conn = sqlite3.connect(ruta_bd)

# Obtener los IDs de las partículas únicas
particle_ids = pd.read_sql_query("SELECT DISTINCT particle_id FROM particulas", conn)

# Función que grafica la trayectoria de una partícula específica y devuelve los datos
def plot_trajectory(particle_id):
    query = f"SELECT x, y, z FROM particulas WHERE particle_id = {particle_id} ORDER BY N_iteracion"
    data = pd.read_sql_query(query, conn)
    return data['x'].values, data['y'].values, data['z'].values

# Usar multiprocessing.Pool para paralelizar el trabajo usando 4 núcleos
with multiprocessing.Pool(processes=num_cores) as pool:
    results = pool.map(plot_trajectory, particle_ids['particle_id'].values)

# Crear una figura para el gráfico 3D
fig = plt.figure(figsize=(20, 20))  # Ajusta las dimensiones según necesites
ax = fig.add_subplot(111, projection='3d')

# Agregar todas las trayectorias al gráfico
for x, y, z in results:
    ax.plot(x, y, z, marker='', linewidth=2)  # Ajusta el grosor con linewidth
    ax.scatter(x[-1], y[-1], z[-1], color='red', s=0.3)  # s es el tamaño del marcador

# Configurar los ángulos de visualización
ax.view_init(elev=10, azim=50)  # Ajusta estos valores según necesites
# Etiquetas de los ejes con tamaño de fuente específico
ax.set_xlabel('X', fontsize=25)  # Ajusta el tamaño de la fuente
ax.set_ylabel('Y', fontsize=25)
ax.set_zlabel('Z', fontsize=25)

# Cambiar el tamaño de las marcas de los ejes
ax.tick_params(axis='both', which='major', labelsize=20)  # Ajusta el tamaño de las marcas

# Título del gráfico
ax.set_title('Trayectorias de Todas las Partículas', fontsize=50)

# Guardar el gráfico
plt.savefig('/home/ninetydrake313/Documentos/Tesis/trayectorias_particulas.png')

# Mostrar el gráfico
plt.show()

# Cerrar la conexión a la base de datos
conn.close()

end_time = time.time() - start_time
print(f"\nTiempo de Ploteo: {end_time} segundos")
