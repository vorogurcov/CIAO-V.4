import threading
import time


class TimerManager:
    def __init__(self):
        self._stop_event = threading.Event()
        self._timer_thread = None
        self._callback = None
        self._completed = False

    def after(self, seconds, callback=None):
        """Запускает таймер и гарантированно вызывает callback"""
        self._stop_event.clear()
        self._completed = False
        self._callback = callback

        try:
            seconds = float(seconds)
        except (ValueError, TypeError):
            raise ValueError("Параметр 'seconds' должен быть числом")

        def timer():
            start_time = time.time()
            while True:
                if self._stop_event.is_set():
                    return
                if time.time() - start_time >= seconds:
                    break
                time.sleep(0.1)

            self._completed = True
            if self._callback:
                self._callback()

        self._timer_thread = threading.Thread(target=timer)
        self._timer_thread.daemon = True
        self._timer_thread.start()

    def cancel(self):
        """Останавливает таймер и предотвращает вызов callback"""
        self._stop_event.set()
        if self._timer_thread:
            self._timer_thread.join(timeout=0.1)

    def is_active(self):
        """Проверяет, активен ли таймер"""
        return not self._stop_event.is_set() and not self._completed