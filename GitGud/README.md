# Simulación de hadronterapia con nanoárticulas micelaneas  en tejido modelado usando metodo Monte-Carlo.
![Estado](https://img.shields.io/badge/Estado-Activo-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Licencia](https://img.shields.io/badge/License-MIT-yellow)

Este archivo tiene como fin explicar cómo ejecutar los scripts que se usaron para los resultados finales en este proyecto.  
Aunque el nombre es **provisional**, contiene la descripción de las intenciones de este proyecto de investigación.  

Inicialmente, hay que colocar todos los archivos en una sola carpeta y tener correctamente configurado el entorno `.venv` con los paquetes necesarios.  

---

## Paquetes utilizados

- `os`
- `subprocess`
- `argparse`
- `concurrent.futures` 
- `time`
- `numpy`
- `math`
- `sqlite3`
- `pandas`
- `matplotlib.pyplot`
- `glob`

---

## Preparación de carpetas

Para ejecutar por primera vez, es necesario que existan carpetas con rutas modificadas.  
Las más importantes y necesarias antes de comenzar son:  

- `BUENA_DATA/intercambio`: almacenamiento temporal de bases de datos de simulación.  
- `csv/A_Val/a10/RAD`: guarda `.csv` con el radio de la envolvente del haz con dirección en **z**.  
- `csv/A_Val/a10/Ec`: guarda `.csv` con la relación entre la profundidad en **z** y la energía cinética promedio depositada.  

---

## Archivo principal de automatización

Estas rutas se encuentran especificadas en `Auto_P.py`.  
Este archivo es el que automatiza las simulaciones para generar hilos de procesamiento en paralelo.  

Desde este se especifican las rutas donde se almacenarán los archivos que se generen y con los que se trabajará para el procesado de los datos.  
Con estas rutas modificadas y el entorno configurado, se explicará cómo funciona el ciclo de simulación.



## Ciclo de simulación 

1.	Configurar los valores en `SM_MC_Auto.py` :

-	`--n` es el numero total de particulas a simular.
-	`--nc` es el numero maximo de colisiones por particula.
-	`--block` es el tamaño de escritura por bloque en la base de datos.


