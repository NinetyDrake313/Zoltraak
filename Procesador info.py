import os
import GPUtil

# Número de núcleos de CPU disponibles
num_cores = os.cpu_count()
print("Número de núcleos de CPU:", num_cores)

# Listar todas las GPU disponibles y sus características principales
gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(f"ID de GPU: {gpu.id}")
    print(f"Nombre: {gpu.name}")
    print(f"Total de memoria: {gpu.memoryTotal} MB")
    print(f"Memoria libre: {gpu.memoryFree} MB")
    print(f"Memoria usada: {gpu.memoryUsed} MB")
    print(f"Utilización de GPU: {gpu.load*100}%")
    print(f"Temperatura: {gpu.temperature} C")
    print("------")