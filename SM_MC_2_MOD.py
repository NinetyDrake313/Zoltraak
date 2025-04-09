import numpy as np
import math
import time
import sqlite3
import os

# Constantes
qelectron = 1.602176634e-19  # Carga elemental (C)
melectron = 0.511  # Masa del electrón (MeV/c²)
epsilon0 = 8.8541878128e-12  # Permisividad del vacío (F/m)
k = 1 / (4 * math.pi * epsilon0)  # Constante de Coulomb (N·m²/C²)
na = 6.02214076e23  # Número de Avogadro (1/mol)
conv = 1.602176634e-13  # Factor de conversión: 1 MeV = 1.602176634e-13 J

# =============================================================
# -----------------Actualización de posiciones-----------------
# =============================================================

def update_position(x, y, z, l, theta, phi, scale=1):
    """
    Actualiza la posición de la partícula en coordenadas cartesianas (en cm).
    Se asume que l ya está en cm.
    """
    x_new = x + l * math.sin(theta) * math.cos(phi) * scale * 1e-10
    y_new = y + l * math.sin(theta) * math.sin(phi) * scale * 1e-10
    z_new = z + l * math.cos(theta) * scale * 1e-10
    return x_new, y_new, z_new

# =======================================================
# -----------------Funciones de energía -----------------
# =======================================================

def calc_beta_gamma(E, E_rest):
    """
    Calcula β (v/c) y γ para una partícula.
    E y E_rest deben estar en MeV.
    """
    gamma = E / E_rest
    beta = math.sqrt(1 - 1 / (gamma ** 2))
    return beta, gamma

def bethe_energy_loss(l, beta, gamma, params):
    """
    Calcula la pérdida de energía en un paso de longitud l (en cm)
    usando la fórmula de Bethe–Bloch. Se fuerza que los argumentos de los
    logaritmos sean mayores a un umbral (1.1) para evitar valores negativos.
    """
    rho_g_cm3 = params['r'] / 1000.0  # conversión: 1000 kg/m³ → 1 g/cm³
    K = 0.307075  # MeV·cm²/g
    f_H = 2 / 18.0
    f_O = 16 / 18.0
    m_e = params['melectron']  # 0.511 MeV
    I1 = params['I1']
    I2 = params['I2']
    z1 = params['z1']

    # Calcular los argumentos de los logaritmos y forzarlos a un mínimo de 1.1
    arg_H = (2 * m_e * beta**2 * gamma**2) / I1
    arg_O = (2 * m_e * beta**2 * gamma**2) / I2
    if arg_H < 1.1:
        arg_H = 1.1
    if arg_O < 1.1:
        arg_O = 1.1

    term_H = f_H * (math.log(arg_H) - beta ** 2)
    term_O = f_O * (math.log(arg_O) - beta ** 2)
    dEdx = K * (z1 ** 2) / (beta ** 2) * rho_g_cm3 * (term_H + term_O)  # MeV/cm

    # dE en MeV; se elimina el factor de conversión ya que dEdx*l está en MeV.
    dE = - dEdx * l * 1e-9

    # Forzar a que la pérdida sea negativa si se llega a obtener un valor positivo.
    if dE > 0:
        dE = -abs(dE)
    return dE

def energy_loss1(l, beta, gamma, params):
    """
    Variante de la pérdida de energía. La implementación es idéntica a la de bethe_energy_loss,
    lo que permite cambios futuros sin afectar la otra función.
    """
    rho_g_cm3 = params['r'] / 1000.0
    K = 0.307075
    f_H = 2 / 18.0
    f_O = 16 / 18.0
    m_e = params['melectron']
    I1 = params['I1']
    I2 = params['I2']
    z1 = params['z1']

    arg_H = (2 * m_e * beta**2 * gamma**2) / I1
    arg_O = (2 * m_e * beta**2 * gamma**2) / I2
    if arg_H < 1.1:
        arg_H = 1.1
    if arg_O < 1.1:
        arg_O = 1.1

    term_H = f_H * (math.log(arg_H) - beta ** 2)
    term_O = f_O * (math.log(arg_O) - beta ** 2)
    dEdx = K * (z1 ** 2) / (beta ** 2) * rho_g_cm3 * (term_H + term_O)
    dE = - dEdx * l * 1e-9
    if dE > 0:
        dE = -abs(dE)
    return dE

def energy_loss2(l, beta, gamma, params):
    """
    Otra variante de la pérdida de energía. Actualmente idéntica a las demás,
    pero se puede modificar de forma independiente en el futuro.
    """
    rho_g_cm3 = params['r'] / 1000.0
    K = 0.307075
    f_H = 2 / 18.0
    f_O = 16 / 18.0
    m_e = params['melectron']
    I1 = params['I1']
    I2 = params['I2']
    z1 = params['z1']

    arg_H = (2 * m_e * beta**2 * gamma**2) / I1
    arg_O = (2 * m_e * beta**2 * gamma**2) / I2
    if arg_H < 1.1:
        arg_H = 1.1
    if arg_O < 1.1:
        arg_O = 1.1

    term_H = f_H * (math.log(arg_H) - beta ** 2)
    term_O = f_O * (math.log(arg_O) - beta ** 2)
    dEdx = K * (z1 ** 2) / (beta ** 2) * rho_g_cm3 * (term_H + term_O)
    dE = - dEdx * l * 1e-9
    if dE > 0:
        dE = -abs(dE)
    return dE

# =====================================================
# -----------------Secciones eficaces-----------------
# =====================================================

def calc_sigma1(E, beta, params):
    """
    Calcula la sección macroscópica Σ (en 1/m) para obtener el camino libre medio.
    """
    zo = params['zo']
    w2 = params['w2']
    zh = params['zh']
    w1 = params['w1']
    n_med = params['nagua']  # en 1/m³
    qelectron = params['qelectron']
    k = params['k']
    z1 = params['z1']

    factor = (z1 * qelectron ** 2 * k / (E * conv)) ** 2  # unidades: (m)²
    dim_factor = (zo ** 2 * w2 + zh ** 2 * w1) / (w2 + w1)
    sigma = dim_factor * n_med * 4 * math.pi * factor / (3 * beta ** 2 + 1)
    return sigma

def calc_sigma2(E, beta, params):
    """
    Variante de la sección eficaz.
    """
    zo = params['zo']
    w2 = params['w2']
    zh = params['zh']
    w1 = params['w1']
    n_med = params['nagua']
    qelectron = params['qelectron']
    k = params['k']
    z1 = params['z1']

    factor = (z1 * qelectron ** 2 * k / (E * conv)) ** 2
    dim_factor = (zo ** 2 * w2 + zh ** 2 * w1) / (w2 + w1)
    sigma = dim_factor * n_med * 4 * math.pi * factor / (3 * beta ** 2 + 1)
    return sigma

def calc_sigma3(E, beta, params):
    """
    Otra variante de la sección eficaz.
    """
    zo = params['zo']
    w2 = params['w2']
    zh = params['zh']
    w1 = params['w1']
    n_med = params['nagua']
    qelectron = params['qelectron']
    k = params['k']
    z1 = params['z1']

    factor = (z1 * qelectron ** 2 * k / (E * conv)) ** 2
    dim_factor = (zo ** 2 * w2 + zh ** 2 * w1) / (w2 + w1)
    sigma = dim_factor * n_med * 4 * math.pi * factor / (3 * beta ** 2 + 1)
    return sigma

# =====================================================
# -----------------Camino libre medio-----------------
# =====================================================

def calc_collision_length(sigma, n_med, rand_val):
    """
    Calcula la longitud de colisión l en cm.
    """
    lambda_m = 1 / sigma  # en metros
    lambda_cm = lambda_m * 100  # conversión a cm
    l = - lambda_cm * math.log(rand_val)
    return l  # l en cm

# ========================================================
# -----------------Distribución de medio-----------------
# ========================================================

def distribucion_valor(x, y, z):
    """
    Devuelve el valor absoluto del producto de las funciones usadas para determinar la región.
    """
    rangox = (1 / math.sqrt(2)) * (math.sin(x - 0.25 * 3 * math.pi) + math.cos(x - 0.25 * 3 * math.pi))
    rangoy = (1 / math.sqrt(2)) * (math.sin(y - 0.25 * 3 * math.pi) + math.cos(y - 0.25 * 3 * math.pi))
    rangoz = (1 / math.sqrt(2)) * (math.sin(z - 0.25 * 3 * math.pi) + math.cos(z - 0.25 * 3 * math.pi))
    region = rangox * rangoy * rangoz
    return abs(region)

# ==============================
# Configuración e Inicialización para iones de carbono
# ==============================

start_time = time.time()

# Parámetros de la simulación
N = 10000         # Número total de partículas (simulaciones)
Nc = 100000       # Número máximo de colisiones por partícula
bloque = 1000     # Tamaño del bloque para escritura en la BD

# Parámetros del medio (agua)
r = 1000.0        # Densidad del agua en kg/m³ (→ 1 g/cm³)
nagua = 3.37e28   # Número de moléculas de agua por m³

# Propiedades del agua (para la contribución en la fórmula de Bethe)
w1 = 2.0
w2 = 1.0
zh = 1.0
zo = 8.0

# Características del ion de carbono (¹²C)
z1 = 6            # Carga: 6+
Ereposo = 12 * 931.5  # Energía de reposo ~ 11178 MeV
Ei = 1350 * 12        # Energía cinética (1350 MeV/nucleón → 16200 MeV total)
E = Ei + Ereposo       # Energía total inicial (MeV)

# Potenciales de ionización (valores aproximados en MeV)
I1 = (12 * zh + 7) * 1e-6  # ~19e-6 MeV
I2 = (12 * zo + 7) * 1e-6  # ~103e-6 MeV

params = {
    'zo': zo,
    'w2': w2,
    'zh': zh,
    'w1': w1,
    'nagua': nagua,
    'qelectron': qelectron,
    'k': k,
    'z1': z1,
    'r': r,
    'melectron': melectron,
    'I1': I1,
    'I2': I2
}

# =======================
# Configurar la base de datos
# =======================
ruta_carpeta = "/home/ninetydrake313/Documentos/Tesis/La vie est drôle/BUENA_DATA/"
os.makedirs(ruta_carpeta, exist_ok=True)
ruta_bd = os.path.join(ruta_carpeta, 'PRUEBA.db')

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
        beta, gamma_val = calc_beta_gamma(Ef, Ereposo)
        valor_region = distribucion_valor(x, y, z)

        if valor_region < 0.4:
            sigma = calc_sigma1(Ef, beta, params)
            print(sigma)
        elif 0.4 <= valor_region <= 0.6:
            sigma = calc_sigma2(Ef, beta, params)
        else:
            sigma = calc_sigma3(Ef, beta, params)

        rand_l = np.random.rand()
        rand_theta = np.random.rand()
        rand_phi = np.random.rand()

        l = calc_collision_length(sigma, params['nagua'], rand_l)
        theta = math.acos(1 - (2 * rand_theta * (1 - beta ** 2)) / (3 * beta ** 2 - 4 * rand_theta * beta ** 2 + 1))
        phi = 2 * math.pi * rand_phi

        if valor_region < 0.4:
            dE = bethe_energy_loss(l, beta, gamma_val, params)
        elif 0.4 <= valor_region <= 0.6:
            dE = energy_loss1(l, beta, gamma_val, params)
        else:
            dE = energy_loss2(l, beta, gamma_val, params)

        Ef_new = Ef + dE  # dE es negativo
        print(Ef_new)
        if Ef_new >= Ereposo:
            x, y, z = update_position(x, y, z, l, theta, phi, scale=1)
            results.append((i, collision_count, x, y, z, Ef_new, dE))
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
