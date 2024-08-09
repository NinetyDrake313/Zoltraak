import cupy as cp
import time

numm = 100000000

# Medir el tiempo para generación de números aleatorios en GPU con CuPy
start_time = time.time()
random_numbers_gpu = cp.random.rand(numm)
cp.cuda.Stream.null.synchronize()  # Asegura que todos los cálculos en GPU se completen
end_gpu = time.time() - start_time

print(f"Cantidad de números generados: {numm}")
print(f"Tiempo para generación en GPU: {end_gpu} segundos")
