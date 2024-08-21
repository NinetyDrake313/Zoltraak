import sqlite3
import cupy as cp  # CuPy para GPU
import pandas as pd
import matplotlib.pyplot as plt
import time
from mpl_toolkits.mplot3d import Axes3D
from multiprocessing import Pool


def process_batch(batch_ids, db_path):
    # Conectar a la base de datos SQLite dentro de cada proceso
    conn = sqlite3.connect(db_path)

    # Leer los datos para las partículas en el lote actual
    query = f"SELECT particle_id, x, y, z FROM particulas WHERE particle_id IN {tuple(batch_ids)} ORDER BY particle_id, N_iteracion"
    data = pd.read_sql_query(query, conn)

    conn.close()

    return data


def plot_batch(data):
    # Crear un stream de CUDA para operaciones asíncronas
    stream = cp.cuda.Stream(non_blocking=True)

    # Usar el stream para realizar operaciones asíncronas en la GPU
    with stream:
        # Convertir los datos a matrices CuPy para GPU
        x_gpu = cp.array(data['x'].values)
        y_gpu = cp.array(data['y'].values)
        z_gpu = cp.array(data['z'].values)
        particle_ids_gpu = cp.array(data['particle_id'].values)

    # Graficar cada trayectoria de manera individual
    unique_particles = cp.unique(particle_ids_gpu)
    fig = plt.figure(figsize=(20, 20))
    ax = fig.add_subplot(111, projection='3d')
    for particle_id in unique_particles:
        mask = particle_ids_gpu == particle_id
        x_cpu = cp.asnumpy(x_gpu[mask])
        y_cpu = cp.asnumpy(y_gpu[mask])
        z_cpu = cp.asnumpy(z_gpu[mask])

        # Graficar las líneas que conectan cada punto de la trayectoria de esta partícula
        ax.plot(x_cpu, y_cpu, z_cpu, marker='', linewidth=2)  # Ajusta el grosor con linewidth
        ax.scatter(x_cpu[-1], y_cpu[-1], z_cpu[-1], color='red', s=0.9)  # Agregar marcador en el último punto

    # Configurar los ángulos de visualización
    ax.view_init(elev=10, azim=50)  # Ajusta estos valores según necesites
    ax.set_xlabel('X', fontsize=25)  # Ajusta el tamaño de la fuente
    ax.set_ylabel('Y', fontsize=25)
    ax.set_zlabel('Z', fontsize=25)
    ax.tick_params(axis='both', which='major', labelsize=20)  # Ajusta el tamaño de las marcas
    ax.set_title('Trayectorias de Todas las Partículas', fontsize=50)

    plt.savefig(f'/home/ninetydrake313/Documentos/Tesis/plotes/trayectoriasCU_{time.time()}.png')
    plt.close(fig)


def main():
    start_time = time.time()

    # Ruta de la base de datos
    ruta_bd = "/home/ninetydrake313/Documentos/Tesis/SM/simulacion_particulas.db"

    # Conectar a la base de datos SQLite para obtener los IDs de las partículas
    conn = sqlite3.connect(ruta_bd)
    particle_ids = pd.read_sql_query("SELECT DISTINCT particle_id FROM particulas", conn)
    conn.close()

    batch_size = 1000  # Procesar en lotes de 100 partículas

    # Dividir los IDs de las partículas en lotes
    batches = [particle_ids['particle_id'][i:i + batch_size].tolist() for i in range(0, len(particle_ids), batch_size)]

    # Crear un pool de procesos utilizando 16 núcleos
    with Pool(processes=20) as pool:
        # Procesar cada lote en paralelo y graficar los resultados de manera independiente
        results = pool.starmap(process_batch, [(batch, ruta_bd) for batch in batches])
        pool.map(plot_batch, results)

    end_time = time.time() - start_time
    print(f"\nTiempo de Ploteo: {end_time} segundos")


if __name__ == "__main__":
    main()
