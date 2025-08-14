import numpy as np
import math
import matplotlib.pyplot as plt


qelectron = 1.602176634e-19  # Carga elemental (C)
melectron =  0.5109989461 # Masa del electrón (MeV)
epsilon0 = 8.8541878128e-12  # Permisividad del vacío (F/m)
k = 1 / (4 * math.pi * epsilon0)  # Constante de Coulomb (N·m²/C²)
na = 6.02214076e23  # Número de Avogadro (1/mol)
conv = 1.602176634e-13  # Factor de conversión: 1 MeV = 1.602176634e-13 J

re = 2.8179403227e-13          # Classical electron radius (cm)
K = 4 * np.pi * na * re**2 * melectron
z_ion = 6

a0_cm = 0.529e-8  # cm
e_2 = 1.44e-13  # MeV * cm  unidad de carga elemental para altas energias
hbar_c = 197.3269804e-13  # MeV·cm
hbar   = 6.582119569e-22  # MeV·s


# Características del ion de carbono (¹²C)

Ereposo = 12 * 931.5  # Energía de reposo ~ 11178 MeV
Ei = 1350 * 12        # Energía cinética (1350 MeV/nucleón → 16200 MeV total)
E = Ei + Ereposo       # Energía total inicial (MeV)



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
    dE = - dEdx * np.abs(l)
    return dE


def wave_vector(beta,gamma):
    k = (beta * gamma * Ereposo) / hbar_c
    return k

def sigma(compuesto,k): #cm^2
    c1 = (2 * (m_reducida[compuesto])**2 * g2[compuesto]**2 ) / (hbar_c**4 * k**2 * mu[compuesto]**2 )
    c2 = (k**2) / (k**2 + mu[compuesto]**2)
    sigma = c1 * c2
    return sigma

def sigma_mix(sigma1,sigma2,medio,nano): #cm^2
    s1 = sigma1 * concentracion['medio'] * na * (density[medio]/A[medio])
    s2 = sigma2 * concentracion['nano']* na * (density[nano]/A[nano])
    sigma_mix = s1 + s2
    return sigma_mix

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
    'ZnO'   :  (30 + 8) ,
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

#relacion porcentual entre el medio y las nanoparticulas
concentracion = {
    'medio' : 0.99,
    'nano'  : 0.01
}



print(ZA_mezcla('H2O','Au'))
print(rho_mezcla('H2O','Au'))
print(I_mezcla('H2O','Au'))
print(K)
print(gamma(E,Ereposo))
print(beta(gamma(E,Ereposo)))
print(Tmax(beta(gamma(E,Ereposo)),gamma(E,Ereposo),Ereposo))
print("Agua dE/dx")
print(
    Energyloss_bethebloch(
        beta(gamma(E, Ereposo)),
        gamma(E, Ereposo),
        Z['H2O'],
        A['H2O'],
        Tmax(beta(gamma(E, Ereposo)), gamma(E, Ereposo), Ereposo),
        I['H2O']
    )
)
print(f"Agua y comp dE/dx a {concentracion['nano']}")
compuesto = 'W'
print(
    Energyloss_bethebloch_mix(
        beta(gamma(E,Ereposo)),
        gamma(E,Ereposo),
        ZA_mezcla('H2O',compuesto),
        rho_mezcla('H2O',compuesto),
        Tmax(beta(gamma(E,Ereposo)),gamma(E,Ereposo),Ereposo),
        I_mezcla('H2O',compuesto)
    )
)

print(Energyloss_percm(
    Energyloss_bethebloch(
    beta(gamma(E, Ereposo)),
        gamma(E, Ereposo),
        Z['H2O'],
        A['H2O'],
        Tmax(beta(gamma(E, Ereposo)), gamma(E, Ereposo), Ereposo),
        I['H2O']
    ),1)
)

print(Energyloss_percm(
Energyloss_bethebloch_mix(
        beta(gamma(E,Ereposo)),
        gamma(E,Ereposo),
        ZA_mezcla('H2O','Au'),
        rho_mezcla('H2O','Au'),
        Tmax(beta(gamma(E,Ereposo)),gamma(E,Ereposo),Ereposo),
        I_mezcla('H2O','Au')
    ),
    1
))

print('En teoria los valores bien ')
print(wave_vector(beta(gamma(E,Ereposo)),gamma(E,Ereposo)))
s1 = sigma('H2O',wave_vector(beta(gamma(E,Ereposo)),gamma(E,Ereposo)))
s2 = sigma('Au',wave_vector(beta(gamma(E,Ereposo)),gamma(E,Ereposo)))
s_mix = sigma_mix(s1,s2,'H2O','Au')
s1_medio = sigma_mix(s1,s1,'H2O','H2O')
print(s1)
print(s2)
print(s_mix)
print(s1_medio)
print(average_free_path(s1_medio))
print(average_free_path_mix(s_mix,'H2O','Au'))

print('--------------------------------------')
print(- np.log(np.random.rand()))


"""
        if (gen_xlim[0] <= x <= gen_xlim[1] and
                gen_ylim[0] <= y <= gen_ylim[1] and
                gen_zlim[0] <= z <= gen_zlim[1]):
            if valor_region < 0.4:
                dEdx = Energyloss_bethebloch(beta_val, gamma_val, Z[medio], A[medio],T_max,I[medio])
                dE = Energyloss_percm(dEdx, l)
                #dE = bethe_energy_loss(l, beta, gamma, params)
            elif 0.4 <= valor_region <= 0.5:
                dEdx = Energyloss_bethebloch_mix(beta_val, gamma_val, ZA_mix, rho_mix, T_max, I_mix)
                dE = Energyloss_percm(dEdx, l)
                #dE = energy_loss1(l, beta, gamma, params)
            else:
                dEdx = Energyloss_bethebloch(beta_val, gamma_val, Z[medio], A[medio], T_max, I[medio])
                dE = Energyloss_percm(dEdx, l)
        else:
            dEdx = Energyloss_bethebloch(beta_val, gamma_val, Z[medio], A[medio], T_max, I[medio])
            dE = Energyloss_percm(dEdx, l)
"""