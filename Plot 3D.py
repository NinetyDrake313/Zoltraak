import os
import pandas as pd
import matplotlib.pyplot as plt
import time

from mpl_toolkits.mplot3d import Axes3D
start_time = time.time()
# Ruta de la carpeta donde están los archivos
folder_path = "/home/ninetydrake313/Documentos/Tesis/SM/"

# Listar todos los archivos CSV en la carpeta
files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Crear una figura para el gráfico 3D con tamaño específico (ancho, alto en pulgadas)
fig = plt.figure(figsize=(20, 20))  # Ajusta las dimensiones según necesites
ax = fig.add_subplot(111, projection='3d')

for file in files:
    # Cargar los datos desde cada archivo
    data = pd.read_csv(os.path.join(folder_path, file))

    # Graficar las líneas que conectan cada punto con un grosor específico
    ax.plot(data['x'], data['y'], data['z'], marker='', linewidth=0.5)  # Ajusta el grosor con linewidth

    # Agregar un marcador en el último punto de la trayectoria
    ax.scatter(data['x'].iloc[-1], data['y'].iloc[-1], data['z'].iloc[-1], color='red',s=0.3)  # s es el tamaño del marcador


# Configurar los ángulos de visualización
ax.view_init(elev=10, azim=50)  # Ajusta estos valores según necesites
# Etiquetas de los ejes con tamaño de fuente específico
ax.set_xlabel('X', fontsize=25)  # Ajusta el tamaño de la fuente
ax.set_ylabel('Y', fontsize=25)
ax.set_zlabel('Z', fontsize=25)

# Cambiar el tamaño de las marcas de los ejes
ax.tick_params(axis='both', which='major', labelsize=20)  # Ajusta el tamaño de las marcas

# Título del gráfico
ax.set_title('Trayectorias de Todas las Partículas',fontsize=50)

plt.savefig('/home/ninetydrake313/Documentos/Tesis/trayectorias.png')

# Mostrar el gráfico
plt.show()

end_time = time.time() - start_time
print(f"\nTiempo de Ploteo: {end_time} segundos")
