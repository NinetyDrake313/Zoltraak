import os
import numpy as np
import pandas as pd
from vispy import scene
from vispy.scene import visuals
from vispy.color import get_colormap

# Ruta de la carpeta que contiene los archivos CSV
folder_path = "/home/ninetydrake313/Documentos/Tesis/SM/"

# Listar todos los archivos CSV en la carpeta
files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

# Configurar la visualización
canvas = scene.SceneCanvas(keys='interactive', bgcolor='white', size=(800, 600), show=True)
view = canvas.central_widget.add_view()

# Crear un mapa de colores
cmap = get_colormap('viridis')
colors = cmap.map(np.linspace(0, 1, len(files)))

# Variables para calcular los límites
min_coords = np.array([np.inf, np.inf, np.inf])
max_coords = np.array([-np.inf, -np.inf, -np.inf])

# Leer y visualizar cada archivo CSV por separado
for file, color in zip(files, colors):
    data = pd.read_csv(file)
    coords = data[['x', 'y', 'z']].values
    coords = np.nan_to_num(coords)  # Asegurarse de que no hay valores NaN

    # Actualizar los límites
    min_coords = np.minimum(min_coords, coords.min(axis=0))
    max_coords = np.maximum(max_coords, coords.max(axis=0))

    # Agregar las trayectorias como líneas con un color único
    line = visuals.Line(pos=coords, color=color, method='gl', parent=view.scene)

# Agregar ejes para indicar dimensiones
axis = visuals.XYZAxis(parent=view.scene)

# Agregar etiquetas a los ejes
x_label = visuals.Text("X-axis", pos=[max_coords[0], 0, 0], color='red', bold=True, font_size=14, parent=view.scene)
y_label = visuals.Text("Y-axis", pos=[0, max_coords[1], 0], color='green', bold=True, font_size=14, parent=view.scene)
z_label = visuals.Text("Z-axis", pos=[0, 0, max_coords[2]], color='blue', bold=True, font_size=14, parent=view.scene)

# Configurar la cámara para mostrar todos los datos
view.camera = 'turntable'
view.camera.set_range()

if __name__ == '__main__':
    canvas.app.run()
