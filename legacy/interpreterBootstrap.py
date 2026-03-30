# Сгенерированный код на Python из программы CIAO 3
import threading
from automatonInfo import callTable


class ResettableTimer:
    def __init__(self, parent_class, interval, function):
        self.parent_class = parent_class
        self.interval = interval  # Время ожидания в секундах
        self.function = function  # Функция для выполнения
        self.timer = None  # Ссылка на объект таймера
        self.is_running = False  # Флаг состояния таймера

    def _start_timer(self):
        # Внутренний метод для запуска таймера
        self.timer = threading.Timer(self.interval, self._on_complete)
        self.timer.start()
        self.is_running = True

    def _on_complete(self):
        # Вызывается по истечении времени
        self.is_running = False
        self.function(self.parent_class)

    def start(self):
        # Запуск или перезапуск таймера
        if self.is_running:
            self.timer.cancel()
        self._start_timer()

    def reset(self):
        # Сброс и перезапуск таймера
        self.start()

    def cancel(self):
        # Полная отмена таймера
        if self.is_running:
            self.timer.cancel()
            self.is_running = False


class Interpreter:
    def __init__(self, init_state):
        self.a = None  # type: String
        self.e = None  # type: String
        self.p = None  # type: String
        self.state = init_state
        self.state_machine = self.build_state_machine()
        self.timers = self.build_timers()
        self.timer = None
        self.links = {}
        print(f"Interpreter инициализирован с состоянием {init_state}")
        self.name = "Interpreter"
        self.isEnd = False

    def addLink(self, name: str, func) -> None:
        self.links[name] = func

    def Set(self, a, e, p):
        print("Interpreter: Event Set(a, e, p)")
        event = "Set"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self, a, e, p)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Set' in self.links:
            self.links['Set'](a, e, p)

    def Tick(self, a, e, p):
        print("Interpreter: Event Tick(a, e, p)")
        event = "Tick"
        if event in self.state_machine[self.state]:
            a, e, p, self.isEnd = callTable(a, e, p)
            self.state_machine[self.state][event](self, a, e, p)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Tick' in self.links:
            self.links['Tick'](a, e, p)

    def Exit(self):
        print("Interpreter: Event Exit()")
        event = "Exit"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Exit' in self.links:
            self.links['Exit']()

    def Restart(self):
        print("Interpreter: Event Restart()")
        event = "Restart"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'Restart' in self.links:
            self.links['Restart']()

    def Trigger_stop(self):
        print("Interpreter: Effect Trigger_stop вызван")
        if 'Trigger_stop' in self.links:
            self.links['Trigger_stop']()

    def IsEnd(self):
        if "IsEnd" in self.links:
            result = self.links['IsEnd']()
        else:
            result = False
        print("Condition IsEnd() =>", result)
        return result

    def build_state_machine(self):
        state_machine = {}
        if 'start' not in state_machine:
            state_machine['start'] = {}
        state_machine['start']['Set'] = (
            lambda self, a, e, p: (self.change_state('ready'), self.Tick(a, e, p), self.check_timer()))
        if 'ready' not in state_machine:
            state_machine['ready'] = {}
        state_machine['ready']['Tick'] = (
            lambda self, a, e, p: (self.change_state('ready'), self.Tick(a, e, p), self.check_timer()) if not self.isEnd else (
            self.change_state('stop'), self.Trigger_stop(), self.check_timer()))
        if 'stop' not in state_machine:
            state_machine['stop'] = {}
        state_machine['stop']['Restart'] = (lambda self: (self.change_state('start'), self.check_timer()))
        return state_machine

    def build_timers(self):
        timers = {}
        return timers

    def change_state(self, new_state):
        if self.timer:
            self.timer.cancel()
        print(f"{self.__class__.__name__}: смена состояния {self.state} -> {new_state}")
        self.state = new_state

    def check_timer(self):
        if self.state in self.timers:
            self.timer = ResettableTimer(self, getattr(self, self.timers[self.state]),
                                         self.state_machine[self.state]['After'])
            self.timer.start()


def run(*args):
    for obj in args:
        try:
            obj.Set("automate", "start", "")
        except Exception as e:
            print(e)


def main():
    interpreter = Interpreter('start')
    interpreter.addLink('Trigger_stop', interpreter.Restart)
    run(interpreter)


if __name__ == '__main__':
    main()
    # Функция run доступна, но не вызывается автоматически