import numpy as np
import math
import time
import sqlite3
import os
import argparse

# ==== Parser de argumentos ====
parser = argparse.ArgumentParser(
    description="Simulación Monte Carlo de iones de carbono con salida parametrizada"
)
parser.add_argument(
    '--output-db', '-o',
    required=True,
    help="Ruta de la base de datos SQLite de salida (p.ej. BUENA_DATA/PRUEBA_1.db)"
)
parser.add_argument(
    '--n', type=int, default=10,
    help="Número total de partículas (default: 10000)"
)
parser.add_argument(
    '--nc', type=int, default=600000,
    help="Máximo de colisiones por partícula (default: 100000)"
)
parser.add_argument(
    '--block', type=int, default=5,
    help="Tamaño de bloque para commits en la BD (default: 1000)"
)
args = parser.parse_args()



# =============================================================
# -----------------Actualización de posiciones-----------------
# =============================================================

def update_position(x, y, z, l, theta, phi, scale = 1):
    """
    Actualiza la posición de la partícula en coordenadas cartesianas (en cm).
    Se asume que l ya está en cm.
    """
    x_new = x + l * math.sin(theta) * math.cos(phi) * scale * 1e23
    y_new = y + l * math.sin(theta) * math.sin(phi) * scale * 1e23
    z_new = z + l * math.cos(theta) * scale * 1e23
    return x_new, y_new, z_new


# Constantes
qelectron = 1.602176634e-19  # Carga elemental (C)
melectron = 0.511  # Masa del electrón (MeV/c²)
epsilon0 = 8.8541878128e-12  # Permisividad del vacío (F/m)
k = 1 / (4 * math.pi * epsilon0)  # Constante de Coulomb (N·m²/C²)
na = 6.02214076e23  # Número de Avogadro (1/mol)

re = 2.8179403227e-13          # Classical electron radius (cm)
K = 4 * np.pi * na * re**2 * melectron
z_ion = 6

a0_cm = 0.529e-8  # cm
e_2 = 1.44e-13  # MeV * cm  unidad de carga elemental para altas energias
hbar_c = 197.3269804e-13  # MeV·cm
hbar   = 6.582119569e-22  # MeV·s

# =======================================================
# -----------------Parametros elementales----------------
# =======================================================
#densidad en g/cm^3
density = {
    'H2O'   : 1.00  ,
    'Ag'    : 10.49 ,
    'Fe3O4' :  5.17 ,
    'SiO2'  : 2.65  ,
    'TiO2'  : 4.23  ,
    'ZnO'   : 5.61  ,
    'Au'    : 19.32 ,
    'Bi'    : 9.78  ,
    'Pb'    : 11.34 ,
    'Pt'    : 21.45 ,
    'Ta'    : 16.65 ,
    'W'     : 19.25
}

# se calcula Z para los compuestos de esta forma dado que son moleculas en un medio separadas
Z = {
    'H2O'   :  (2 * 1 + 8),
    'Ag'    :  47,
    'Fe3O4' :  (3 * 26 + 4 * 8) ,
    'SiO2'  :  (14 + 2 * 8) ,
    'TiO2'  :  (22 + 2 * 8) ,
    'ZnO'   :  (30 + 8) / 2,
    'Au'    :  79,
    'Bi'    :  83,
    'Pb'    :  82,
    'Pt'    :  78,
    'Ta'    :  73,
    'W'     :  74
}

#peso atomico por molecula ,de igual forma se ven las moleculas individuales y no un solido
A = {
    'H2O'   : (2 * 1.0079 + 15.999),                  # ≈ 18.015
    'Ag'    : 107.8682,
    'Fe3O4' : (3 * 55.845 + 4 * 15.999) ,          # ≈ 39.73
    'SiO2'  : (28.085 + 2 * 15.999) ,              # ≈ 20.03
    'TiO2'  : (47.867 + 2 * 15.999) ,              # ≈ 26.62
    'ZnO'   : (65.38 + 15.999) ,                   # ≈ 40.69
    'Au'    : 196.9665,
    'Bi'    : 208.9804,
    'Pb'    : 207.2,
    'Pt'    : 195.084,
    'Ta'    : 180.94788,
    'W'     : 183.84
}
#En eV ,valores tabulados para los elementos y los compuestos con diferentes metodos
I = {
    'H2O'   : 75.0,
    'Ag'    : 470.0,
    'Fe3O4' : 286.0,    # Aproximado (mezcla Fe y O, valor usado en literatura)
    'SiO2'  : 139.2,    # Usado en Geant4, simulaciones de radiación
    'TiO2'  : 233.0,    # Aproximado por mezcla ponderada
    'ZnO'   : 284.0,    # Usado en nanodosimetría
    'Au'    : 790.0,
    'Bi'    : 823.0,
    'Pb'    : 823.0,
    'Pt'    : 780.0,
    'Ta'    : 727.0,
    'W'     : 727.0
}

concentracion = {
    'medio' : 0.90,
    'nano'  : 0.10
}

# =======================================================
# -----------Parametros del modelos de Yukawa------------
# =======================================================

#masa reducida de ion de carbon con compuesto de dispersion (MeV/c²)
m_reducida = {
    'H2O'   : 6708.99,
    'Ag'    : 10058.91,
    'Fe3O4' : 10627.14,
    'SiO2'  : 9317.14,
    'TiO2'  : 9717.83,
    'ZnO'   : 9822.44,
    'Au'    : 11002.13,
    'Bi'    : 11056.09,
    'Pb'    : 11049.14,
    'Pt'    : 11000.63,
    'Ta'    : 10938.53,
    'W'     : 10957.72
}

#parametro de apantallamiento mu thomas-fermi
mu = {
    'H2O'   :  ((10)**(1/3)) / (0.8853 * a0_cm),
    'Ag'    :  ((47)**(1/3)) / (0.8853 * a0_cm),
    'Fe3O4' :  ((110)**(1/3)) / (0.8853 * a0_cm),
    'SiO2'  :  ((30)**(1/3)) / (0.8853 * a0_cm),
    'TiO2'  :  ((38)**(1/3)) / (0.8853 * a0_cm),
    'ZnO'   :  ((38)**(1/3)) / (0.8853 * a0_cm),
    'Au'    :  ((79)**(1/3)) / (0.8853 * a0_cm),
    'Bi'    :  ((83)**(1/3)) / (0.8853 * a0_cm),
    'Pb'    :  ((82)**(1/3)) / (0.8853 * a0_cm),
    'Pt'    :  ((78)**(1/3)) / (0.8853 * a0_cm),
    'Ta'    :  ((73)**(1/3)) / (0.8853 * a0_cm),
    'W'     :  ((74)**(1/3)) / (0.8853 * a0_cm)
}

#constante de acoplo de yukawa g^2 en MeV * cm
g2 = {
    'H2O'   : z_ion * e_2 * (2 * 1 + 8) ,
    'Ag'    : z_ion * e_2 * 47,
    'Fe3O4' : z_ion * e_2 * (3 * 26 + 4 * 8),
    'SiO2'  : z_ion * e_2 * (14 + 2 * 8),
    'TiO2'  : z_ion * e_2 * (22 + 2 * 8),
    'ZnO'   : z_ion * e_2 * (30 + 8) / 2,
    'Au'    : z_ion * e_2 * 79,
    'Bi'    : z_ion * e_2 * 83,
    'Pb'    : z_ion * e_2 * 82,
    'Pt'    : z_ion * e_2 * 78,
    'Ta'    : z_ion * e_2 * 73,
    'W'     : z_ion * e_2 * 74
}

# =======================================================
# -----------------Funciones de energía -----------------
#-----------------------Modificadas----------------------
# =======================================================
def gamma(E_total,E_reposo):
    gamma = E_total /E_reposo
    return gamma

def beta(gamma):
    beta = math.sqrt(1 - 1 / (gamma ** 2))
    return beta

def ZA_mezcla(medio,nano):
    ZA_mix = concentracion['medio'] * (Z[medio]/A[medio]) + concentracion['nano'] * (Z[nano]/A[nano])
    return ZA_mix

def rho_mezcla(medio,nano):
    rho_mix = concentracion['medio'] * density[medio] + concentracion['nano'] * density[nano]
    return rho_mix

def I_mezcla(medio,nano):
    I_mix = np.exp( (concentracion['medio'] * (Z[medio]/A[medio]) * np.log(I[medio]) + concentracion['nano'] * (Z[nano]/A[nano]) * np.log(I[nano])) / (concentracion['medio'] * (Z[medio]/A[medio]) + concentracion['nano'] * (Z[nano]/A[nano])) )
    return I_mix

def Tmax(beta,gamma,E_reposo):
     T_max = (2 * melectron * beta ** 2 * gamma ** 2) / (1 + 2 * gamma * (melectron / E_reposo) + (melectron / E_reposo) ** 2)
     return T_max

def Energyloss_bethebloch(beta,gamma,Z,A,Tmax,I):
    c1 = K * z_ion**2 * (Z/A) * (1 / beta**2)
    c2 = 1/2 * np.log((2 * melectron * beta**2 * gamma**2 * Tmax)/ (I * 1e-6)**2 )
    delta = 0
    dEdx = c1 * (c2 - beta**2 - 0.5 * delta)
    return dEdx

def Energyloss_bethebloch_mix(beta,gamma,ZA,rho,Tmax,I):
    c1 = K * z_ion**2 * ZA * (1 / beta**2) * rho
    c2 = 1/2 * np.log((2 * melectron * beta**2 * gamma**2 * Tmax)/ (I * 1e-6)**2 )
    delta = 0
    dEdx = c1 * (c2 - beta**2 - 0.5 * delta)
    return dEdx

def Energyloss_percm(dEdx,l):
    dE = - dEdx * np.abs(l) * 1e24
    return dE

# =====================================================
# -----------------Secciones eficaces------------------
#-----------------------Modificadas--------------------
# =====================================================
def wave_vector(beta,gamma):
    k = (beta * gamma * Ereposo) / hbar_c
    return k

def sigma(compuesto,k): #cm^2
    c1 = (4*math.pi * (m_reducida[compuesto])**2 * g2[compuesto]**2 ) / (hbar_c**4 * k**2 * mu[compuesto]**2 )
    c2 = (k**2) / (4*k**2 + mu[compuesto]**2)
    sigma = c1 * c2
    return sigma

def sigma_mix(sigma1,sigma2,medio,nano): #cm^2
    s1 = sigma1 * concentracion['medio'] * na * (density[medio]/A[medio])
    s2 = sigma2 * concentracion['nano']* na * (density[nano]/A[nano])
    sigma_mix = s1 + s2
    return sigma_mix

# =====================================================
# -----------------Camino libre medio------------------
#-----------------------Modificadas--------------------
# =====================================================
def average_free_path(sigma):
    n_molecules = na * (density['H2O']/A['H2O'])
    lamb = 1 / (sigma * n_molecules )
    l = - lamb * np.log(np.random.rand())
    return l

def average_free_path_mix(sigma,medio,nano):
    n_molecules = concentracion['medio'] * na * (density[medio]/A[medio]) + concentracion['nano']* na * (density[nano]/A[nano])
    lamb = 1 / (sigma * n_molecules )
    l = - lamb * np.log(np.random.rand())
    return l


# ========================================================
# -----------------Distribución de medio-----------------
# ========================================================

def distribucion_valor(x, y, z):
    """
    Devuelve el valor absoluto del producto de las funciones usadas para determinar la región.
    """
    a = 630
    rangox = - math.cos(a * x)
    rangoy = - math.cos(a * y)
    rangoz = - math.cos(a * z)
    region = rangox * rangoy * rangoz
    return abs(region)

# ==============================
# Configuración e Inicialización para iones de carbono
# ==============================

start_time = time.time()

# Parámetros de la simulación
N = args.n
Nc = args.nc
bloque = args.block

# Parámetros del medio (agua)
r = 1000.0        # Densidad del agua en kg/m³ (→ 1 g/cm³)
nagua = 3.37e28   # Número de moléculas de agua por m³


# Características del ion de carbono (¹²C)
z1 = 6            # Carga: 6+
Ereposo = 12 * 931.5  # Energía de reposo ~ 11178 MeV
E_nucleon = 225 * 6   # Rango tipico 120 -430 ,un valor medio 225 MeV/u
Ei = E_nucleon * 12
E = Ei + Ereposo       # Energía total inicial (MeV)


#Region de la muestra
muestra_x, muestra_y, muestra_z = 4, 4, 2.5
inicio_x, inicio_y, inicio_z = -2, -2, 20

gen_xlim = (inicio_x, inicio_x + muestra_x)
gen_ylim = (inicio_y, inicio_y + muestra_y)
gen_zlim = (inicio_z, inicio_z + muestra_z)


# =======================
# Parametos de Mezcla
# =======================
medio = 'H2O'
nano = 'Au'

ZA_mix = ZA_mezcla(medio,nano)
rho_mix = rho_mezcla(medio,nano)
I_mix = I_mezcla(medio,nano)

# =======================
# Configurar la base de datos
# =======================

# usamos directamente la ruta que vino por argumentos
ruta_bd = args.output_db
os.makedirs(os.path.dirname(ruta_bd), exist_ok=True)

conn = sqlite3.connect(ruta_bd)
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS particulas')
cursor.execute('''
CREATE TABLE particulas (
    particle_id INTEGER,
    N_iteracion INTEGER,
    x REAL,
    y REAL,
    z REAL,
    Ef REAL,
    Ec REAL
)
''')

# =======================
# Simulación Monte Carlo para iones de carbono
# =======================
results = []

for i in range(1, N + 1):
    Ef = E  # Energía total actual (MeV)
    x, y, z = 0.0, 0.0, 0.0  # Posición inicial en cm
    collision_count = 0

    while Ef >= Ereposo and collision_count < Nc:
        collision_count += 1
        gamma_val = gamma(Ef, Ereposo)
        beta_val = beta(gamma_val)
        T_max = Tmax(beta_val,gamma_val,Ereposo)
        k = wave_vector(beta_val,gamma_val)
        valor_region = distribucion_valor(x, y, z)

        if (gen_xlim[0] <= x <= gen_xlim[1] and
                gen_ylim[0] <= y <= gen_ylim[1] and
                gen_zlim[0] <= z <= gen_zlim[1]):
            if valor_region < 0.4:
                s1 = sigma(medio,k)
                s1_medio = sigma_mix(s1, s1, medio, medio)
                l = average_free_path(s1_medio)
                dEdx = Energyloss_bethebloch(beta_val, gamma_val, Z[medio], A[medio], T_max, I[medio])
                dE = Energyloss_percm(dEdx, l)
            elif 0.4 <= valor_region <= 0.5:
                s1 = sigma(medio,k)
                s2 = sigma(nano,k)
                s_mix = sigma_mix(s1, s1, medio, nano)
                l = average_free_path_mix(s_mix,medio, nano)
                dEdx = Energyloss_bethebloch_mix(beta_val, gamma_val, ZA_mix, rho_mix, T_max, I_mix)
                dE = Energyloss_percm(dEdx, l)
            else:
                s1 = sigma(medio, k)
                s1_medio = sigma_mix(s1, s1, medio, medio)
                l = average_free_path(s1_medio)
                dEdx = Energyloss_bethebloch(beta_val, gamma_val, Z[medio], A[medio], T_max, I[medio])
                dE = Energyloss_percm(dEdx, l)
        else:
            s1 = sigma(medio, k)
            s1_medio = sigma_mix(s1, s1, medio, medio)
            l = average_free_path(s1_medio)
            #sigma = calc_sigma1(Ef, beta_val, params)
            dEdx = Energyloss_bethebloch(beta_val, gamma_val, Z[medio], A[medio], T_max, I[medio])
            dE = Energyloss_percm(dEdx, l)

        rand_l = np.random.rand()
        rand_theta = np.random.rand()
        rand_phi = np.random.rand()

        theta = math.acos(1 - (2 * rand_theta * (1 - beta_val ** 2)) / (3 * beta_val ** 2 - 4 * rand_theta * beta_val ** 2 + 1))
        phi = 2 * math.pi * rand_phi

        Ef_new = Ef + dE  # dE es negativo
        #print(Ef_new)
        if Ef_new >= Ereposo:
            x, y, z = update_position(x, y, z, l, theta, phi, scale=1)
            results.append((i, collision_count, x, y, z, Ef_new, dEdx))
            Ef = Ef_new
        else:
            break

    # Cada 'bloque' de partículas se escribe en la base de datos
    if i % bloque == 0:
        cursor.executemany('''
            INSERT INTO particulas (particle_id, N_iteracion, x, y, z, Ef, Ec)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', results)
        conn.commit()
        results = []  # Limpiar la lista para liberar memoria
        print(f"Partículas simuladas: {i}")

# Inserción de cualquier resultado pendiente
if results:
    cursor.executemany('''
        INSERT INTO particulas (particle_id, N_iteracion, x, y, z, Ef, Ec)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', results)
    conn.commit()

conn.close()

end_time = time.time() - start_time
print(f"\nTiempo de simulación: {end_time} segundos")
