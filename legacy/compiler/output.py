# Сгенерированный код на Python из программы CIAO 3
import random
import inspect
import threading


class ResettableTimer:
    def __init__(self, parent_class, interval, function):
        self.parent_class = parent_class
        self.interval = interval    # Время ожидания в секундах
        self.function = function    # Функция для выполнения
        self.timer = None           # Ссылка на объект таймера
        self.is_running = False     # Флаг состояния таймера

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
            

class Person:
    def __init__(self, init_state):
        self.lightState = None  # type: Boolean
        self.state = init_state
        self.state_machine = self.build_state_machine()
        self.timers = self.build_timers()
        self.timer = None
        self.links = {}
        print(f"Person инициализирован с состоянием {init_state}")
        self.name = "Person"

    def addLink(self, name: str, func) -> None:
        self.links[name] = func

    def PressSwitch(self):
        print("Person: Event PressSwitch()")
        event = "PressSwitch"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'PressSwitch' in self.links:
            self.links['PressSwitch']()

    def SendTurnOn(self):
        print("Person: Effect SendTurnOn вызван")
        if 'SendTurnOn' in self.links:
            self.links['SendTurnOn']()

    def SendTurnOff(self):
        print("Person: Effect SendTurnOff вызван")
        if 'SendTurnOff' in self.links:
            self.links['SendTurnOff']()

    def IsLightOn(self):
        if "IsLightOn" in self.links:
            result = self.links['IsLightOn']()
        else:
            result = random.choice([True, False])
        print("Condition IsLightOn() =>", result)
        return result

    def build_state_machine(self):
        state_machine = {}
        if 'Idle' not in state_machine:
            state_machine['Idle'] = {}
        state_machine['Idle']['PressSwitch'] = (lambda self: (self.change_state('Idle'), self.SendTurnOff(), self.check_timer()) if self.IsLightOn() else (self.change_state('Idle'), self.SendTurnOn(), self.check_timer()))
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
            self.timer = ResettableTimer(self, getattr(self, self.timers[self.state]), self.state_machine[self.state]['After'])
            self.timer.start()

class Light:
    def __init__(self, init_state):
        self.state = init_state
        self.state_machine = self.build_state_machine()
        self.timers = self.build_timers()
        self.timer = None
        self.links = {}
        print(f"Light инициализирован с состоянием {init_state}")
        self.name = "Light"

    def addLink(self, name: str, func) -> None:
        self.links[name] = func

    def TurnOn(self):
        print("Light: Event TurnOn()")
        event = "TurnOn"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'TurnOn' in self.links:
            self.links['TurnOn']()

    def TurnOff(self):
        print("Light: Event TurnOff()")
        event = "TurnOff"
        if event in self.state_machine[self.state]:
            self.state_machine[self.state][event](self)
        else:
            print(f'Invalid event {event} for state {self.state}')
        if 'TurnOff' in self.links:
            self.links['TurnOff']()

    def IsOn(self):
        return self.state == "On"

    def build_state_machine(self):
        state_machine = {}
        if 'Off' not in state_machine:
            state_machine['Off'] = {}
        state_machine['Off']['TurnOn'] = (lambda self: (self.change_state('On'), self.check_timer()))
        if 'On' not in state_machine:
            state_machine['On'] = {}
        state_machine['On']['TurnOff'] = (lambda self: (self.change_state('Off'), self.check_timer()))
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
            self.timer = ResettableTimer(self, getattr(self, self.timers[self.state]), self.state_machine[self.state]['After'])
            self.timer.start()

def run(*args):
    for obj in args:
        try:
            obj.PressSwitch()
        except Exception as e:
            pass

def main():
    human = Person('Idle')
    bulb = Light('Off')
    human.addLink('SendTurnOn', bulb.TurnOn)
    human.addLink('SendTurnOff', bulb.TurnOff)
    human.addLink('IsLightOn', bulb.IsOn)


if __name__ == '__main__':
    main()
    # Функция run доступна, но не вызывается автоматически