import logging
import threading
import time

logger = logging.getLogger(__name__)

# -----------------------------------------------------
# 0. UTILITAIRE DE RATE LIMITING (TOKEN BUCKET)
# -----------------------------------------------------


class RateLimiter:
    """
    Algorithme de Token Bucket pour limiter le débit. Thread-safe.

    Le temps est mesuré avec `time.monotonic` : un saut de l'horloge système
    (NTP, DST) ne doit pas pouvoir recharger ou vider le seau.
    """

    def __init__(self, max_calls_per_second=10, max_wait_seconds=2.0):
        self.rate = max_calls_per_second
        self.tokens = float(max_calls_per_second)  # Capacité initiale
        self.last_update = time.monotonic()
        self.max_wait_seconds = max_wait_seconds
        self.lock = threading.Lock()

    def _reserve(self) -> float:
        """Recharge le seau et réserve un token. Retourne le temps d'attente."""
        current_time = time.monotonic()
        self.tokens += (current_time - self.last_update) * self.rate
        self.last_update = current_time

        # Pas de burst infini.
        if self.tokens > self.rate:
            self.tokens = self.rate

        if self.tokens >= 1:
            self.tokens -= 1
            return 0.0

        # On ne réserve que ce que l'on est réellement capable d'attendre :
        # sans plafond, `self.tokens` devenait arbitrairement négatif et une
        # rafale de requêtes pouvait immobiliser un thread indéfiniment.
        deficit = 1 - self.tokens
        if deficit > self.max_wait_seconds * self.rate:
            self.tokens = 0.0
            return self.max_wait_seconds
        self.tokens -= 1
        return deficit / self.rate

    def wait_for_slot(self):
        """
        Bloque jusqu'à ce qu'un token soit disponible (file d'attente temporelle).
        La réservation est faite sous le lock, la pause hors du lock.
        """
        with self.lock:
            wait_time = self._reserve()
        if wait_time > 0:
            logger.info("Rate limit atteint, attente de %.4fs", wait_time)
            time.sleep(wait_time)