import os
import subprocess
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

# ---------------------------------------------
# Runner depurado: muestra logs y comprueba CSV
# ---------------------------------------------
start_time = time.time()
def parse_args():
    p = argparse.ArgumentParser(
        description="Runner paralelo con logging y verificación de CSV"
    )
    p.add_argument('-n', '--runs',  type=int, default=15,
                   help="Número de iteraciones (por defecto 1)")
    p.add_argument('-j', '--jobs',  type=int, default=15,
                   help="Procesos paralelos (por defecto 1)")
    p.add_argument('--sim-script', default='SM_MC_Auto.py',
                   help="Script de simulación (acepta --output-db)")
    p.add_argument('--post-script', default='curvaauto.py',
                   help="Script de postproceso (acepta --input-db, --radius-output, --bragg-output)")
    p.add_argument('--db-dir', default='BUENA_DATA/intercambio',
                   help="Directorio base para BD por hilo")
    p.add_argument('--rad-dir', default='csv/A_Val/a10/RAD',
                   help="Directorio de salida para radios")
    p.add_argument('--bragg-dir', default='csv/A_Val/a10/Ec',
                   help="Directorio de salida para Bragg")
    return p.parse_args()


def run_once(iter_index, args):
    """
    Corre simulación y post-proceso con logging detallado.
    """
    # asigna thread_id cíclico según jobs
    thread_id = ((iter_index - 1) % args.jobs) + 1
    db_path    = os.path.join(args.db_dir, f'PRUEBA_{thread_id}.db')
    radius_out = os.path.abspath(os.path.join(args.rad_dir,  f'i_{iter_index}.csv'))
    bragg_out  = os.path.abspath(os.path.join(args.bragg_dir, f'i_{iter_index}.csv'))

    # log paths
    print(f"[Iter {iter_index}] Usando DB: {db_path}")
    print(f"[Iter {iter_index}] Radios → {radius_out}")
    print(f"[Iter {iter_index}] Bragg  → {bragg_out}")

    # crear carpetas
    os.makedirs(os.path.dirname(db_path),    exist_ok=True)
    os.makedirs(os.path.dirname(radius_out), exist_ok=True)
    os.makedirs(os.path.dirname(bragg_out),  exist_ok=True)

    # 1) simulación
    cmd_sim = ['python3', args.sim_script, '--output-db', db_path]
    print("  Ejecutando simulación:", ' '.join(cmd_sim))
    res = subprocess.run(cmd_sim, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("  ➥ sim stdout:\n", res.stdout)
    if res.returncode != 0:
        print("  ✖ sim stderr:\n", res.stderr)
        return False

    # 2) post-proceso
    cmd_post = [
        'python3', args.post_script,
        '--input-db',      db_path,
        '--radius-output', radius_out,
        '--bragg-output',  bragg_out
    ]
    print("  Ejecutando post-proceso:", ' '.join(cmd_post))
    res2 = subprocess.run(cmd_post, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("  ➥ post stdout:\n", res2.stdout)
    if res2.returncode != 0:
        print("  ✖ post stderr:\n", res2.stderr)
        return False

    # 3) Verificar que los CSV existan y no estén vacíos
    for f in (radius_out, bragg_out):
        if os.path.isfile(f) and os.path.getsize(f) > 0:
            print(f"  ✔ {os.path.basename(f)} guardado correctamente ({os.path.getsize(f)} bytes)")
        else:
            print(f"  ✖ ¡{os.path.basename(f)} NO se creó o está vacío!")
            return False

    return True


def main():
    args = parse_args()
    # Ejecutar en paralelo o en serie según jobs
    results = []
    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(run_once, idx, args): idx for idx in range(1, args.runs+1)}
        for fut in as_completed(futures):
            idx = futures[fut]
            ok = fut.result()
            if not ok:
                print(f"[Iter {idx}] Falló proceso, revisar logs anteriores.")
    end_time = time.time() - start_time
    print(f"\nTiempo de total de simulación: {end_time} segundos")
    print("\n→ Kept you waiting, huh?, Proceso finalizado.")

if __name__ == '__main__':
    main()
