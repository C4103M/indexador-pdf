import threading
from typing import Callable

class Debouncer:
    def __init__(self, delay: float, function: Callable):
        """
        Um 'debouncer' que atrasa a execução de uma função.

        :param delay: O tempo de espera em segundos após a última chamada.
        :param function: A função a ser executada após o atraso.
        """
        self.delay = delay
        self.function = function
        self.timer = None

    def call(self, *args, **kwargs):
        """
        Chama o debouncer. Cancela qualquer temporizador pendente e
        inicia um novo.
        """
        # Cancela o temporizador anterior, se houver um
        if self.timer is not None and self.timer.is_alive():
            self.timer.cancel()
        
        # Inicia um novo temporizador
        self.timer = threading.Timer(
            self.delay, self.function, args=args, kwargs=kwargs
        )
        self.timer.start()

    def cancel(self):
        """Cancela o temporizador pendente."""
        if self.timer is not None and self.timer.is_alive():
            self.timer.cancel()