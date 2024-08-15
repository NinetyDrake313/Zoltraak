import random
import secrets
import time

numm = 100000000
# Medir el tiempo para random
start_time = time.time()
[random.random() for _ in range(numm)]
end_random = time.time() - start_time

# Medir el tiempo para secrets
start_time = time.time()
[secrets.randbelow(100) / 100 for _ in range(numm)]
end_secrets = time.time() - start_time

print(f"Cantidad de numeros generados: {numm} segundos")
print(f"Tiempo para random: {end_random} segundos")
print(f"Tiempo para secrets: {end_secrets} segundos")
