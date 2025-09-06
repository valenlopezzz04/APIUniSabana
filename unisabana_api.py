# unisabana_api.py
from flask import Flask, jsonify, request
import requests
from circuit_breaker import CircuitBreaker

PRIMARY = "http://127.0.0.1:5000/score"
SECONDARY = "http://127.0.0.1:5001/score"
TIMEOUT = 1.5  # segundos

app = Flask(__name__)
cb = CircuitBreaker(failure_threshold=0.5, request_window=10, half_open_timeout=30)

def call_primary(q: str):
    r = requests.get(PRIMARY, params={"q": q}, timeout=TIMEOUT)
    if r.status_code >= 500:
        raise RuntimeError(f"HTTP {r.status_code} en primario")
    return r.json()

def call_secondary(q: str):
    r = requests.get(SECONDARY, params={"q": q}, timeout=TIMEOUT)
    if r.status_code >= 500:
        raise RuntimeError(f"HTTP {r.status_code} en secundario")
    return r.json()

@app.get("/consulta")
def consulta():
    user = request.args.get("user", "demo")

    ok, res = cb.execute(lambda: call_primary(user))
    if ok:
        # Devolvemos SOLO el nombre de la API (buró) como pide el enunciado
        return jsonify({"api": res.get("bureau", "primary")}), 200

    # Si falla o está en OPEN (rechazado), intentamos secundario
    if cb.get_state() == 'OPEN' or "Rechazado" in str(res):
        try:
            fb = call_secondary(user)
            return jsonify({"api": fb.get("bureau", "secondary")}), 200
        except Exception as e:
            return jsonify({"error": f"Secundario también falló: {e}"}), 503

    # Si falló estando CLOSED (no alcanzó umbral aún), reportamos fallo
    return jsonify({"error": str(res)}), 503

if __name__ == "__main__":
    # UniSabana API en 8000
    app.run(host="127.0.0.1", port=8000)
