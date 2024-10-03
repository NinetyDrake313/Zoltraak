import numpy as np
import math
from math import pi, sqrt, log, acos, sin, cos
import time
import sqlite3
import os

start_time = time.time()
# Constantes físicas
qelectron = 1.602176634e-19  # Carga del electrón en Coulombs
melectron = 0.511  # Masa del electrón en MeV/c^2
c = 299792458  # Velocidad de la luz en m/s
a0 = 5.29177210903e-11  # Radio de Bohr en metros
epsilon_0 = 8.854187817e-12  # Permisividad del vacío en C^2/(N·m^2)
na = 6.02214076e23  # Número de Avogadro en mol^-1
K = 0.307075  # MeV·cm²/mol (Constante en la fórmula de Bethe)

# Propiedades del material (agua)
rho = 1.0  # Densidad del agua en g/cm^3
M_agua = 18.01528  # Masa molar del agua en g/mol
Z_agua = 7.42  # Número atómico efectivo del agua
A_agua = 18.01528  # Peso atómico del agua en g/mol
I = 75e-6  # Potencial de ionización promedio del agua en MeV

# Partícula incidente (ion de carbono)
z1 = 6  # Número atómico del carbono
A_carbono = 12  # Número másico del carbono
E_reposo = A_carbono * 931.5  # Energía de masa en reposo en MeV
E_i = 400 * A_carbono  # Energía cinética inicial en MeV (400 MeV/u * 12 u)
E_total = E_i + E_reposo  # Energía total inicial en MeV

# Configuración de la base de datos
ruta_carpeta = "/home/ninetydrake313/Documentos/Tesis/SM/"
os.makedirs(ruta_carpeta, exist_ok=True)
ruta_bd = os.path.join(ruta_carpeta, 'simulacion_particulasCARBON.db')

conn = sqlite3.connect(ruta_bd)
cursor = conn.cursor()
# Limpiar la tabla 'particulas' antes de insertar nuevos datos
#cursor.execute('DELETE FROM particulas')

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

# Limpiar la tabla 'particulas' antes de insertar nuevos datos
cursor.execute('DELETE FROM particulas')

# Parámetros de la simulación
N = 100 # Número total de partículas a simular

# Bucle de simulación
for i in range(1, N + 1):
    Ef = E_total  # Energía total inicial de la partícula
    contador = 0
    x, y, z = 0.0, 0.0, 0.0  # Posiciones iniciales
    print(i)
    while Ef > E_reposo:
        contador += 1
                # Energía cinética actual
        Ek = Ef - E_reposo  # Energía cinética en MeV
        if Ek <= 0:
            break  # La partícula se ha detenido

        # Calcular beta y gamma
        gamma = Ef / E_reposo
        beta = math.sqrt(1 - (1 / gamma ** 2))
        v = beta * c  # Velocidad de la partícula en m/s

        # Calcular Tmax
        me_c2 = melectron  # MeV
        Tmax = (2 * me_c2 * beta ** 2 * gamma ** 2) / (1 + 2 * gamma * (me_c2 / (A_carbono * 931.5)) + (me_c2 / (A_carbono * 931.5)) ** 2)  # MeV

        # Calcular el término logarítmico en la fórmula de Bethe
        term1 = 2 * me_c2 * beta ** 2 * gamma ** 2 * Tmax
        term2 = I ** 2
        if term1 > 0 and term2 > 0:
            L = math.log(term1 / term2) - 2 * beta ** 2
        else:
            L = 0  # Evitar logaritmo de número negativo o cero

        # Calcular dE/dx en MeV·cm²/g
        dEdx = K * (Z_agua / A_agua) * (z1 ** 2 / beta ** 2) * L  # MeV·cm²/g

        # Convertir dE/dx a MeV/cm
        dEdx = dEdx * rho  # MeV/cm

        # Convertir dE/dx a MeV/m
        dEdx = dEdx * 100  # MeV/m

        # Calcular theta_min basado en el apantallamiento electrónico
        Z1 = z1
        Z2 = 1  # Para electrones
        a = 0.8853 * a0 / (Z1 ** (1 / 3))  # Longitud de apantallamiento en metros

        # Convertir Ek a Joules
        Ek_J = Ek * 1.602176634e-13  # 1 MeV = 1.602e-13 J

        # Calcular theta_min
        numerador = Z1 * Z2 * qelectron ** 2
        denominador = 2 * pi * epsilon_0 * Ek_J * a
        theta_min = numerador / denominador  # En radianes

        # Asegurar que theta_min no sea mayor que pi
        if theta_min > pi:
            theta_min = pi

        # Cálculo de sigma usando la sección eficaz de Rutherford con theta_min
        ke = 8.987551787e9  # Constante de Coulomb en N·m²/C²
        sigma = ((Z1 * Z2 * qelectron ** 2 * ke) / Ek_J) ** 2 * (1 / theta_min ** 2)  # m²

        # Números aleatorios para la longitud de camino y ángulos
        gamma_rand = np.random.rand()
        theta_rand = np.random.rand()
        phi_rand = np.random.rand()

        # Longitud de camino
        # ne: número de electrones por unidad de volumen en el agua
        ne = (rho * na / M_agua) * Z_agua  # Número de electrones por cm³
        ne = ne * 1e6  # Convertir a m⁻³
        l = - (1. / (ne * sigma)) * np.log(gamma_rand) * 10000  # m

        # Pérdida de energía en la longitud l
        Ec = dEdx * l # Energía perdida en MeV

        # Asegurarse de que Ec no sea negativa
        if Ec < 0:
            Ec = 0

        Ef -= Ec  # Actualiza la energía total de la partícula

        if Ef < E_reposo:
            break  # La partícula se ha detenido

        # Ángulos de dispersión
        # Ahora theta varía entre theta_min y pi
        theta = theta_min + (pi - theta_min) * theta_rand  # radianes
        phi = 2 * pi * phi_rand  # radianes

        # Actualiza las posiciones
        x += l * sin(theta) * cos(phi) * 1000
        y += l * sin(theta) * sin(phi) * 1000
        z += l * cos(theta) * 1000

        # Guarda los datos en la base de datos
        cursor.execute('''
            INSERT INTO particulas (particle_id, N_iteracion, x, y, z, Ef, Ec)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (i, contador, x, y, z, Ef, Ec))

        # Opcional: imprimir l y Ec para verificar

        print(f"{i} Iteración {contador}: l = {l:.4e} m, Ec = {Ec:.4e} MeV")

    # Commit después de cada partícula


# Cerrar la conexión a la base de datos
conn.commit()
conn.close()

end_time = time.time() - start_time
print(f"\nTiempo de simulación: {end_time} segundos")
print("Simulación completada.")
