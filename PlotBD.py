import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import time
from mpl_toolkits.mplot3d import Axes3D

start_time = time.time()

# Ruta de la base de datos
ruta_bd = "/home/ninetydrake313/Documentos/Tesis/SM/simulacion_particulas.db"

# Conectar a la base de datos SQLite
conn = sqlite3.connect(ruta_bd)

# Crear una figura para el gráfico 3D con tamaño específico (ancho, alto en pulgadas)
fig = plt.figure(figsize=(20, 20))  # Ajusta las dimensiones según necesites
ax = fig.add_subplot(111, projection='3d')

# Obtener los IDs de las partículas únicas
particle_ids = pd.read_sql_query("SELECT DISTINCT particle_id FROM particulas", conn)

# Iterar sobre cada ID de partícula y graficar su trayectoria
for particle_id in particle_ids['particle_id']:
    # Leer los datos de la base de datos para la partícula actual
    query = f"SELECT x, y, z FROM particulas WHERE particle_id = {particle_id} ORDER BY N_iteracion"
    data = pd.read_sql_query(query, conn)

    # Graficar las líneas que conectan cada punto con un grosor específico
    ax.plot(data['x'], data['y'], data['z'], marker='', linewidth=2)  # Ajusta el grosor con linewidth

    # Agregar un marcador en el último punto de la trayectoria
    ax.scatter(data['x'].iloc[-1], data['y'].iloc[-1], data['z'].iloc[-1], color='red', s=0.3)  # s es el tamaño del marcador

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

end_time = time.time() - start_time
print(f"\nTiempo de Ploteo: {end_time} segundos")

# Cerrar la conexión a la base de datos
conn.close()
