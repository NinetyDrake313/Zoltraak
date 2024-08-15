import numpy as np
import math
from math import pi, sqrt, log, acos, sin, cos
import secrets
import scipy.constants
import csv
import os
import time

from particle import Particle
from scipy.constants import physical_constants

start_time = time.time()

electron = Particle.from_pdgid(11)
# Definición de parámetros

N = 100000 #000                                                  # Número total de simulaciones(Particulas)
Nc = 100000                                            # Número máximo de colisiones por simulación

qelectron   = physical_constants['elementary charge']       # Carga del electrón (Coulombs)
melectron   = physical_constants['electron mass']           # Masa del electrón (kg)
mpelectron  = electron.mass                                 # Masa del electrón (MeV/c^2)
k           = 1 / (4 * np.pi * scipy.constants.epsilon_0)   # Constante de Coulomb (N*m^2/C^2)

# Variables adicionales
h           = 30.0                                           # Ancho de la placa (cm)
r           = 1000.0                                         # Densidad del agua (kg/m^3)
r1          = 0.0899                                         # Densidad del hidrógeno (kg/m^3)
r2          = 1.429                                          # Densidad del oxígeno (kg/m^3)
na          = scipy.constants.Avogadro                       # Número de Avogadro
A1          = 1.0                                            # Peso atómico del hidrógeno
A2          = 16.0                                           # Peso atómico del oxígeno
w1          = 2.0                                            # Número de elementos de hidrógeno
w2          = 1.0                                            # Número de elementos de oxígeno
zh          = 1.0                                            # Número de electrones del hidrógeno
zo          = 8.0                                            # Número de electrones del oxígeno
nagua       = 3.37e28                                        # Número de moles de agua por unidad de volumen (1/m^3)

# Características de la partícula incidente
z1          = 1                                            # Número de electrones del elemento incidente
Ereposo     = 938.972                                      # Masa de la partícula incidente (Mev/c^2)
Ei          = 1350                                         # Energía inicial de la partícula (Mev)
E           = Ei + Ereposo                                 # Energía Total de la partícula incidente

Nat = Nref = Nab = 0
h = 30.0  # Altura o profundidad de la simulación

# Matriz para almacenar los resultados de la energía
En = np.zeros((300, 2))

I1 = (12 * zh + 7) * 1e-6                                  # Potencial de ionización del hidrógeno (MeV)
I2 = (12 * zo + 7) * 1e-6                                  # Potencial de ionización del oxígeno (MeV)
na1 = w1*nagua
na2 = w2*nagua

# Impresión de las constantes físicas y variables adicionales
print(f"Constantes Físicas:\n")
print(f"Nombre de la partícula:   {electron.name}")
print(f"Masa del electrón:        {melectron[0]} kg")
print(f"Carga del electrón:       {qelectron[0]} C")
print(f"Masa del electrón:        {mpelectron} MeV/c²")
print(f"Permeabilidad del vacio:  {scipy.constants.epsilon_0} F⋅m−1")
print(f"Constante de Coulumb:     {k} N*m^2/C^2")

print(f"\nPropiedades de los materiales y constantes químicas:\n")
print(f"Densidad del agua:          {r} kg/m^3")
print(f"Densidad del hidrógeno:     {r1} kg/m^3")
print(f"Densidad del oxígeno:       {r2} kg/m^3")
print(f"Número de Avogadro:         {na} mol⁻¹")
print(f"Peso atómico del hidrógeno: {A1}")
print(f"Peso atómico del oxígeno:   {A2}")
print(f"Número de elementos H:      {w1}")
print(f"Número de elementos O:      {w2}")
print(f"Número de electrones H:     {zh}")
print(f"Número de electrones O:     {zo}")
print(f"Moles de agua por volumen:  {nagua} mol/m^3")

print(f"\nCaracterísticas de la partícula incidente:\n")
print(f"Número de electrones del elemento incidente:  {z1}")
print(f"Masa de la partícula incidente (reposo):      {Ereposo} MeV/c²")
print(f"Energía inicial de la partícula:              {Ei} MeV")
print(f"Energía total de la partícula incidente:      {E} MeV")

#Ciclo para N cantidad de particulas
for i in range(1, N + 1):
    Ef    = E                                                   #Solo carga el valor inicial de la energia
    gam   = Ef /Ereposo                                         #Renombra la relacion entre la energia total y la energia en reposo
    beta  = math.sqrt(1 - (1. / pow(gam, 2)))                   #beta relativista
    sigma = ((zo**2 * w2 + zh**2 * w1) / (w2 + w1)) * nagua * 4 * pi * (z1 * qelectron[0]**2 * k * 1.602e13 / Ef)**2 / (3 * beta**2 + 1)  #Sección eficaz

    [x,y,z] = [0,0,0]          #Valores iniciales en marco de referencia
    [l,phi,theta] = [0,0,0]    #valores inciales de calculo
    ruta_carpeta = "/home/ninetydrake313/Documentos/Tesis/SM/"  # Nota las barras invertidas dobles
    os.makedirs(ruta_carpeta, exist_ok=True)
    nombre_archivo = f"{ruta_carpeta}{i} Particula.csv"
    with open(nombre_archivo, 'w', newline='') as file:
      writer = csv.DictWriter(file, fieldnames=['N_iteracion', 'x', 'y', 'z', 'Ef','Ec'])
      writer.writeheader()
      contador = 0

      while Ef > 0:
        contador += 1
        gamma = (secrets.randbelow((2**53) - 1) + 1) / (2**53)    # Genera un número flotante aleatorio en el rango [casi 0, 1)
        theta_rand = secrets.randbelow(2**53) / (2**53)           # Genera un número flotante aleatorio en el rango (0, 1)
        phi_rand = secrets.randbelow(2**53) / (2**53)             # Genera un número flotante aleatorio en el rango (0, 1)

        l = -(1. / (3 * nagua * sigma * 1E6)) * math.log(gamma)                                                #Calculo de recorrido medio
        theta = math.acos(1 - (2 * theta_rand * (1 - beta**2)) / (3 * beta**2 - 4 * theta_rand * beta**2 + 1)) #Generacion del angulo theta aleatorio
        phi = 2*pi*phi_rand                                                                                    #Generacion del angulo phi aleatorio
        Ec = (1E-6 * r * 4 * math.pi / melectron[0]) * (z1 * qelectron[0]**2 * k * 1.602E13 / beta)**2 * ((w1 * zh * na1 * (math.log(2 * melectron[0] * (beta * gam)**2 / I1) - beta**2) / r1) + (w2 * zo * na2 * (math.log(2 * melectron[0] * (beta * gam)**2 / I2) - beta**2) / r2)) * l
        Ef += Ec
        if Ef > Ereposo:
          #Posiciones en cartesianas
          x = x + l*sin(theta)*cos(phi) * 1e31
          y = y + l*sin(theta)*sin(phi) * 1e31
          z = z + l*cos(theta) * 1e31
          # Escribir directamente en el archivo CSV
          writer.writerow({'N_iteracion': contador, 'x': x, 'y': y, 'z': z, 'Ef': Ef, 'Ec': Ec})
        else:
          #print(f"{i} La energía de la partícula ha caído a cero o es negativa, terminando el ciclo.")
          break  # Salir del bucle si la energía es cero o negativa
          # Imprimir todos los resultados guardados

end_time = time.time() - start_time
print(f"\nTiempo de simulacio: {end_time} segundos")
