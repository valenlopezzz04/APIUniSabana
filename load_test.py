# load_test.py
import threading, time, requests, collections

URL = "http://127.0.0.1:8000/consulta?user=stress"
TIMEOUT = 2.0
NUM_THREADS = 20      # cuántos hilos en paralelo
REQS_PER_THREAD = 10  # cuántas solicitudes hace cada hilo
SLEEP_BETWEEN = 0.05  # pausa pequeña entre solicitudes, por hilo

lock = threading.Lock()
counts = collections.Counter()

def worker(tid):
    for i in range(REQS_PER_THREAD):
        try:
            r = requests.get(URL, timeout=TIMEOUT)
            data = {}
            try:
                data = r.json()
            except Exception:
                pass
            api = data.get("api") or data.get("error") or f"HTTP{r.status_code}"
            with lock:
                counts[api] += 1
        except Exception as e:
            with lock:
                counts[f"EXC:{type(e).__name__}"] += 1
        time.sleep(SLEEP_BETWEEN)

def run_burst():
    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(NUM_THREADS)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    dt = time.time() - t0
    print("\n=== Resumen ===")
    total = sum(counts.values())
    for k, v in counts.most_common():
        print(f"{k:20s}: {v}")
    print(f"Total              : {total}")
    print(f"Duración (s)       : {dt:.2f}")

if __name__ == "__main__":
    print(f"Lanzando {NUM_THREADS} hilos x {REQS_PER_THREAD} reqs (≈ {NUM_THREADS*REQS_PER_THREAD} solicitudes)…")
    run_burst()
