import numpy as np
from math import pi, sqrt, log, acos, sin, cos
import secrets
import scipy.constants
import time
import sqlite3
from multiprocessing import Pool

from particle import Particle
from scipy.constants import physical_constants

def simulate_particle(i):
    # Constantes físicas
    electron = Particle.from_pdgid(11)
    qelectron = physical_constants['elementary charge']  # Carga del electrón (Coulombs)
    melectron = physical_constants['electron mass']  # Masa del electrón (kg)
    mpelectron = electron.mass  # Masa del electrón (MeV/c^2)

    k = 1 / (4 * np.pi * scipy.constants.epsilon_0)  # Constante de Coulomb (N*m^2/C^2)

    k = 1 / (4 * np.pi * scipy.constants.epsilon_0)  # Constante de Coulomb (N*m^2/C^2)
    electron = Particle.from_pdgid(11)
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

    Ef = E
    gam = Ef / Ereposo
    beta = sqrt(1 - (1. / pow(gam, 2)))
    sigma = ((zo ** 2 * w2 + zh ** 2 * w1) / (w2 + w1)) * nagua * 4 * pi * (
                z1 * qelectron[0] ** 2 * k / Ef) ** 2 / (3 * beta ** 2 + 1)

    [x, y, z] = [0, 0, 0]
    contador = 0
    results = []

    while Ef > 0:
        contador += 1
        gamma = secrets.randbelow((2 ** 53) - 1) / (2 ** 53)
        theta_rand = secrets.randbelow(2 ** 53) / (2 ** 53)
        phi_rand = secrets.randbelow(2 ** 53) / (2 ** 53)

        l = -(1. / (3 * nagua * sigma * 1E6)) * log(gamma)
        theta = acos(1 - (2 * theta_rand * (1 - beta ** 2)) / (3 * beta ** 2 - 4 * theta_rand * beta ** 2 + 1))
        phi = 2 * pi * phi_rand
        Ec = (1E-6 * r * 4 * pi / melectron[0]) * (z1 * qelectron[0] ** 2 * k / beta) ** 2 * (
                (w1 * zh * na1 * (log(2 * melectron[0] * (beta * gam) ** 2 / I1) - beta ** 2) / r1) +
                (w2 * zo * na2 * (log(2 * melectron[0] * (beta * gam) ** 2 / I2) - beta ** 2) / r2)) * l
        Ef += Ec

        if Ef > Ereposo:
            x = x + l * sin(theta) * cos(phi) * 10
            y = y + l * sin(theta) * sin(phi) * 10
            z = z + l * cos(theta) * 10
            Ec = -Ec
            results.append((i, contador, x, y, z, Ef, Ec))
        else:
            break

    return results

def main():
    N = 1000000  # Total de simulaciones
    num_processes = 20  # Número de procesos a utilizar

    start_time = time.time()

    # Configurar la base de datos
    ruta_bd = '/home/ninetydrake313/Documentos/Tesis/SM/simulacion_particulas.db'
    conn = sqlite3.connect(ruta_bd)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM particulas')
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
    conn.commit()

    # Procesamiento en paralelo
    with Pool(num_processes) as pool:
        results = pool.map(simulate_particle, range(1, N + 1))

    # Insertar resultados en la base de datos
    for result in results:
        for data in result:
            cursor.execute('''
                INSERT INTO particulas (particle_id, N_iteracion, x, y, z, Ef, Ec)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', data)

    conn.commit()
    conn.close()

    end_time = time.time() - start_time
    print(f"Tiempo de simulación: {end_time} segundos")

if __name__ == '__main__':
    main()
