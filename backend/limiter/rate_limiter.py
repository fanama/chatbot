import time
import threading


# -----------------------------------------------------
# 0. UTILITAIRE DE RATE LIMITING (TOKEN BUCKET)
# -----------------------------------------------------


class RateLimiter:
    """
    Implémente un algorithme de Token Bucket pour limiter le débit.
    Thread-safe pour utilisation avec Flask/FastAPI.
    """

    def __init__(self, max_calls_per_second=10):
        self.rate = max_calls_per_second
        self.tokens = max_calls_per_second  # Capacité initiale
        self.last_update = time.time()
        self.lock = threading.Lock()

    def wait_for_slot(self):
        """
        Bloque l'exécution jusqu'à ce qu'un token soit disponible.
        Agit comme une file d'attente temporelle.
        """
        with self.lock:
            current_time = time.time()
            time_passed = current_time - self.last_update

            # Recharge les tokens en fonction du temps passé
            self.tokens += time_passed * self.rate

            # On ne peut pas avoir plus de tokens que le taux max (pas de burst infini)
            if self.tokens > self.rate:
                self.tokens = self.rate

            self.last_update = current_time

            if self.tokens >= 1:
                # Slot disponible immédiatement
                self.tokens -= 1
                return
            else:
                # Pas de slot, on doit attendre
                needed = 1 - self.tokens
                wait_time = needed / self.rate

                # On "réserve" le token futur et on met à jour le temps
                self.tokens -= 1

        # On dort en dehors du lock pour ne pas bloquer les autres threads
        # qui voudraient juste vérifier l'état, mais ici c'est séquentiel pour l'appelant
        if wait_time > 0:
            print(f"⏳ Rate limit atteint. Attente de {wait_time:.4f}s...")
            time.sleep(wait_time)
