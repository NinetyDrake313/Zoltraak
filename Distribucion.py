import numpy as np
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D

# ----------------------------
# Función principal
# ----------------------------
def f(x):
    return (1 / math.sqrt(2)) * (np.sin(x - 0.75 * np.pi) + np.cos(x - 0.75 * np.pi))

def f_total(x, y, z):
    return f(x) * f(y) * f(z)

# ----------------------------
# Parámetros configurables
# ----------------------------
target_value = 0.9          # Valor objetivo para |f(x, y, z)|
tolerance = 0.01            # Tolerancia para considerar un punto como válido
resolution = 150            # Número de puntos por eje

# Límites personalizados para cada eje
xlim = (-3, 3)
ylim = (-3, 3)
zlim = (-3, 3)

# ----------------------------
# Generar malla 3D
# ----------------------------
x_vals = np.linspace(*xlim, resolution)
y_vals = np.linspace(*ylim, resolution)
z_vals = np.linspace(*zlim, resolution)

X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals, indexing='ij')
F_vals = f_total(X, Y, Z)

# ----------------------------
# Filtrar puntos con |f(x, y, z)| ≈ target_value
# ----------------------------
mask = np.abs(np.abs(F_vals) - target_value) < tolerance
x_sol = X[mask]
y_sol = Y[mask]
z_sol = Z[mask]

# ----------------------------
# Graficar puntos en 3D
# ----------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x_sol, y_sol, z_sol, s=1, color='teal')

ax.set_title(f'Puntos donde |f(x, y, z)| ≈ {target_value}')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# Aplicar los márgenes configurados
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_zlim(zlim)
ax.view_init(elev=30, azim=30)


plt.show()
