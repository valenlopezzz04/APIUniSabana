# circuit_breaker.py
import time

class CircuitBreaker:
    def __init__(self, failure_threshold=0.5, request_window=10, half_open_timeout=30):
        self.failure_threshold = failure_threshold   # 50%
        self.request_window = request_window         # 10 solicitudes
        self.half_open_timeout = half_open_timeout   # 30s

        self.state = 'CLOSED'
        self.last_failure_time = None
        self.request_history = []  # True=ok, False=error

    def get_state(self):
        return self.state

    def log(self, message):
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"[{ts}] [STATE: {self.state}] {message}")

    def execute(self, call_fn):
        # Si está OPEN, solo dejamos pasar cuando cumpla el timeout → HALF_OPEN
        if self.state == 'OPEN':
            if (time.time() - self.last_failure_time) > self.half_open_timeout:
                self.log("Temporizador expirado. Cambiando a HALF-OPEN para una prueba.")
                self.state = 'HALF_OPEN'
            else:
                self.log("Circuito en OPEN. Rechazando la llamada para evitar sobrecarga.")
                return False, "Rechazado por Circuit Breaker"

        try:
            # Intento al servicio (debe lanzar excepción si falla)
            result = call_fn()
            self.log("Llamada al servicio exitosa.")
            if self.state == 'CLOSED':
                self._handle_closed(True)
            elif self.state == 'HALF_OPEN':
                self._handle_half_open(True)
            return True, result
        except Exception as e:
            self.log(f"Llamada fallida con error: {e}")
            if self.state == 'CLOSED':
                self._handle_closed(False)
            elif self.state == 'HALF_OPEN':
                self._handle_half_open(False)
            return False, str(e)

    # --- Estados internos ---
    def _handle_closed(self, success: bool):
        self.request_history.append(success)
        if len(self.request_history) > self.request_window:
            self.request_history.pop(0)

        if len(self.request_history) >= self.request_window:
            failures = self.request_history.count(False)
            failure_rate = failures / self.request_window
            if failure_rate >= self.failure_threshold:
                self.state = 'OPEN'
                self.last_failure_time = time.time()
                self.log(f"¡ALERTA! Tasa de fallo {failure_rate*100:.0f}% (>=50%). Cambia a OPEN.")
                self.request_history = []  # opcional: limpiar ventana

    def _handle_half_open(self, success: bool):
        if success:
            self.state = 'CLOSED'
            self.request_history = []
            self.last_failure_time = None
            self.log("Prueba exitosa en HALF-OPEN. Vuelve a CLOSED.")
        else:
            self.state = 'OPEN'
            self.last_failure_time = time.time()
            self.log("Prueba fallida en HALF-OPEN. Vuelve a OPEN.")
