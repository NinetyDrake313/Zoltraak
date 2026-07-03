import pandas as pd
import matplotlib.pyplot as plt

# Listado de archivos y etiquetas
files = ['SN.csv', 'a1.csv', 'a2.csv', 'a5.csv', 'a10.csv', 'a630.csv']
labels = ['Sin NPs', 'a = 1', 'a = 2', 'a = 5', 'a = 10', 'a = 630']

colors = {
    "Sin NPs"  : "#1f1f1f",
    "a = 1"        : "#DD00E6",  # Magenta brillante
    "a = 2"        : "#2C97EB",  # Azul claro
    "a = 5"        : "#E6006B",  # Rosa intenso
    "a = 10"        : "#9200E6",  # Púrpura
    "a = 630"       : "#FFD700",  # Gris medio (anteriormente casi negro)
}
# Cargar todos los CSV
dfs = []
for file in files:
    path = f'/home/ninetydrake313/Documentos/Tesis/La vie est drôle/csv/A_Val/Comparativos/{file}'
    try:
        dfs.append(pd.read_csv(path))
    except FileNotFoundError:
        print(f"Archivo no encontrado: {path}")
        dfs.append(pd.DataFrame())

# Determinar nombres de ejes según el primer CSV válido
for df in dfs:
    if not df.empty:
        x_col, y_col = df.columns[0], df.columns[1]
        break

plt.figure(figsize=(10, 6))
for df, label in zip(dfs, labels):
    if df.empty:
        continue
    plt.plot(df[x_col], df[y_col], marker='', linestyle='-', label=label, color=colors[label], linewidth=2 if label == "Sin Nano" else 1.5)

#plt.xlim(2.7, 5.8)
#plt.ylim(5, 70)
#plt.yscale("log", base=10)
plt.xlabel('Depth z (cm)')
plt.ylabel('Radius (cm)')
#plt.ylabel(f'Energy per unit area (MeV/cm$^2$)')
#plt.ylabel(r"dE/dx $\left(\mathrm{MeV}/\mathrm{mm}\right) $") #energía por área  energía promedio
plt.title(f'Comparison of nanoparticles in tissue for average radius with 10% concentration.')
plt.grid(True)
plt.legend(title='Nanoparticles')
plt.tight_layout()
plt.savefig(f'/home/ninetydrake313/Documentos/Tesis/La vie est drôle/csv/NANO/Comparativos/eVal_Nano_Comparacion_{y_col}.png')
plt.show()


"""
# Listado de archivos y etiquetas
files = ['SN.csv', 'Ag.csv', 'Au.csv', 'Bi.csv', 'Fe3O4.csv', 'Pb.csv','Pt.csv','SiO2.csv','Ta.csv','TiO2.csv','W.csv','ZnO.csv']
labels = ['Sin Nano', 'Ag', 'Au', 'Bi', 'Fe3O4', 'Pb','Pt','SiO2','Ta','TiO2','W','ZnO']

colors = {
    "Sin Nano"  : "#1f1f1f",
    "Ag"        : "#DD00E6",  # Magenta brillante
    "Au"        : "#2C97EB",  # Azul claro
    "Bi"        : "#E6006B",  # Rosa intenso
    "Fe3O4"     : "#9200E6",  # Púrpura
    "Pb"        : "#7F7F7F",  # Gris medio (anteriormente casi negro)
    "Pt"        : "#FFD700",  # Dorado (platino estilizado)
    "SiO2"      : "#FF8C00",  # Naranja oscuro (cuarzo)
    "Ta"        : "#00CED1",  # Turquesa (tantalio)
    "TiO2"      : "#DC143C",  # Rojo carmesí (dióxido de titanio)
    "W"         : "#228B22",  # Verde bosque (tungsteno)
    "ZnO"       : "#4169E1",  # Azul real (óxido de zinc)
}
# Cargar todos los CSV
dfs = []
for file in files:
    path = f'/home/ninetydrake313/Documentos/Tesis/La vie est drôle/csv/NANO/Comparativos/{file}'
    try:
        dfs.append(pd.read_csv(path))
    except FileNotFoundError:
        print(f"Archivo no encontrado: {path}")
        dfs.append(pd.DataFrame())


# Listado de archivos y etiquetas
files = ['SN.csv', 'a1.csv', 'a2.csv', 'a5.csv', 'a10.csv', 'a630.csv']
labels = ['Sin Nano', 'a = 1', 'a = 2', 'a = 5', 'a = 10', 'a = 630']

colors = {
    "Sin Nano"  : "#1f1f1f",
    "a = 1"        : "#DD00E6",  # Magenta brillante
    "a = 2"        : "#2C97EB",  # Azul claro
    "a = 5"        : "#E6006B",  # Rosa intenso
    "a = 10"        : "#9200E6",  # Púrpura
    "a = 630"       : "#FFD700",  # Gris medio (anteriormente casi negro)
}
# Cargar todos los CSV
dfs = []
for file in files:
    path = f'/home/ninetydrake313/Documentos/Tesis/La vie est drôle/csv/A_Val/Comparativos/{file}'
    try:
        dfs.append(pd.read_csv(path))
    except FileNotFoundError:
        print(f"Archivo no encontrado: {path}")
        dfs.append(pd.DataFrame())



# Listado de archivos y etiquetas
files = ['SN.csv', 'a1.csv', 'a2.csv', 'a5.csv', 'a10.csv', 'a630.csv']
labels = ['Sin NPs', 'a = 1', 'a = 2', 'a = 5', 'a = 10', 'a = 630']

colors = {
    "Sin NPs"  : "#1f1f1f",
    "a = 1"        : "#DD00E6",  # Magenta brillante
    "a = 2"        : "#2C97EB",  # Azul claro
    "a = 5"        : "#E6006B",  # Rosa intenso
    "a = 10"        : "#9200E6",  # Púrpura
    "a = 630"       : "#FFD700",  # Gris medio (anteriormente casi negro)
}
# Cargar todos los CSV
dfs = []
for file in files:
    path = f'/home/ninetydrake313/Documentos/Tesis/La vie est drôle/csv/A_Val/Comparativos/{file}'
    try:
        dfs.append(pd.read_csv(path))
    except FileNotFoundError:
        print(f"Archivo no encontrado: {path}")
        dfs.append(pd.DataFrame())
"""