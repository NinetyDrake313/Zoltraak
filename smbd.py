import numpy as np
import math
from math import pi, sqrt, log, acos, sin, cos
import secrets
import scipy.constants
import time
import sqlite3
import os

from particle import Particle
from scipy.constants import physical_constants

start_time = time.time()

electron = Particle.from_pdgid(11)

# Definición de parámetros
N = 10000  # Número total de simulaciones(Particulas)
Nc = 100000  # Número máximo de colisiones por simulación

qelectron = physical_constants['elementary charge']  # Carga del electrón (Coulombs)
melectron = physical_constants['electron mass']  # Masa del electrón (kg)
mpelectron = electron.mass  # Masa del electrón (MeV/c^2)
k = 1 / (4 * np.pi * scipy.constants.epsilon_0)  # Constante de Coulomb (N*m^2/C^2)

# Variables adicionales
h = 30.0  # Ancho de la placa (cm)
r = 1000.0  # Densidad del agua (kg/m^3)
r1 = 0.0899  # Densidad del hidrógeno (kg/m^3)
r2 = 1.429  # Densidad del oxígeno (kg/m^3)
na = scipy.constants.Avogadro  # Número de Avogadro
A1 = 1.0  # Peso atómico del hidrógeno
A2 = 16.0  # Peso atómico del oxígeno
w1 = 2.0  # Número de elementos de hidrógeno
w2 = 1.0  # Número de elementos de oxígeno
zh = 1.0  # Número de electrones del hidrógeno
zo = 8.0  # Número de electrones del oxígeno
nagua = 3.37e28  # Número de moles de agua por unidad de volumen (1/m^3)

# Características de la partícula incidente
z1 = 1  # Número de electrones del elemento incidente
Ereposo = 938.972  # Masa de la partícula incidente (Mev/c^2)
Ei = 1350  # Energía inicial de la partícula (Mev)
E = Ei + Ereposo  # Energía Total de la partícula incidente

I1 = (12 * zh + 7) * 1e-6  # Potencial de ionización del hidrógeno (MeV)
I2 = (12 * zo + 7) * 1e-6  # Potencial de ionización del oxígeno (MeV)
na1 = w1 * nagua
na2 = w2 * nagua

# Configurar la base de datos
ruta_carpeta = "/home/ninetydrake313/Documentos/Tesis/SM/"
os.makedirs(ruta_carpeta, exist_ok=True)
ruta_bd = os.path.join(ruta_carpeta, 'simulacion_particulas.db')

conn = sqlite3.connect(ruta_bd)
cursor = conn.cursor()

# Limpiar la tabla 'particulas' antes de insertar nuevos datos
cursor.execute('DELETE FROM particulas')

# Crear la tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS particulas (
    particle_id INTEGER,
    N_iteracion INTEGER,
    x REAL,
    y REAL,
    z REAL,
    Ef REAL,
    Ec REAL
)
''')

# Ciclo para N cantidad de partículas
for i in range(1, N + 1):
    Ef = E
    gam = Ef / Ereposo
    beta = math.sqrt(1 - (1. / pow(gam, 2)))
    sigma = ((zo ** 2 * w2 + zh ** 2 * w1) / (w2 + w1)) * nagua * 4 * pi * (
                z1 * qelectron[0] ** 2 * k * 1.602e13 / Ef) ** 2 / (3 * beta ** 2 + 1)

    [x, y, z] = [0, 0, 0]
    [l, phi, theta] = [0, 0, 0]
    contador = 0

    while Ef > 0:
        contador += 1
        gamma = (secrets.randbelow((2 ** 53) - 1) + 1) / (2 ** 53)
        theta_rand = secrets.randbelow(2 ** 53) / (2 ** 53)
        phi_rand = secrets.randbelow(2 ** 53) / (2 ** 53)

        l = -(1. / (3 * nagua * sigma * 1E6)) * math.log(gamma)
        theta = math.acos(1 - (2 * theta_rand * (1 - beta ** 2)) / (3 * beta ** 2 - 4 * theta_rand * beta ** 2 + 1))
        phi = 2 * pi * phi_rand
        Ec = (1E-6 * r * 4 * math.pi / melectron[0]) * (z1 * qelectron[0] ** 2 * k * 1.602E13 / beta) ** 2 * (
                (w1 * zh * na1 * (math.log(2 * melectron[0] * (beta * gam) ** 2 / I1) - beta ** 2) / r1) +
                (w2 * zo * na2 * (math.log(2 * melectron[0] * (beta * gam) ** 2 / I2) - beta ** 2) / r2)) * l
        Ef += Ec

        if Ef > Ereposo:
            # Posiciones en cartesianas
            x = x + l * sin(theta) * cos(phi) * 1e31
            y = y + l * sin(theta) * sin(phi) * 1e31
            z = z + l * cos(theta) * 1e31

            # Insertar los datos en la base de datos
            cursor.execute('''
                INSERT INTO particulas (particle_id, N_iteracion, x, y, z, Ef, Ec)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (i, contador, x, y, z, Ef, Ec))
        else:
            break

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

end_time = time.time() - start_time
print(f"\nTiempo de simulación: {end_time} segundos")
