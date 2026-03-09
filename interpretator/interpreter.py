from syntax import *
import dsl_info_ciao as dsl_info
import pprint
from interpretator.createTable import GetTable, create_link
from reservFunc.after import TimerManager

from tabulate import tabulate
import re
from colorama import Fore, init, Style

init(autoreset=True)


def print_table(matrix, headers):
    print(tabulate(matrix, headers, tablefmt="simple_grid", stralign='center'))


class Interpreter:
    class Cell:
        def __init__(self, actions, end_state):
            self.actions = actions
            self.end_state = end_state

        def __str__(self):
            cell_str = f"Actions: {self.actions}, End State: {self.end_state}"
            if hasattr(self, 'condition') and self.condition is not None:
                cell_str += f", Condition: {self.condition}"
            return cell_str

    class Object:
        def __init__(self, classInfo, className, currentState):
            self.clas = className
            self.state = currentState
            if "conditions" in classInfo:
                self.condition = {}
                for cond in classInfo["conditions"]:
                    self.condition[cond] = False
            if "variables" in classInfo:
                self.variables = dict.fromkeys(classInfo["variables"])
            if "assertions" in classInfo:
                self.assertion = classInfo["assertions"]

    def __init__(self, ast, maxDepth):
        self.table_code = GetTable(ast)

        # init classes
        self.events = {}
        self.effects = {}
        self.variables = {}
        self.condition = {}
        self.assertion = {}
        self.classInitialization()
        self.stateTable = self.getStateTable()

        # for clas in list(self.stateTable.keys()):
        #     print_table(self.stateTable[clas][1:], self.stateTable[clas][0])

        # init scheme
        self.objects = {}
        self.links = {}
        if not self.stateTable:
            return

        self.initObject()
        self.initLink()
        self.initInterface()
        self.maxDepth = maxDepth
        self.currentDepth = 0
        self.isLimitedTime = False

    def classInitialization(self):
        for clas in list(self.table_code["classes"].keys()):
            self.events[clas] = self.table_code["classes"][clas]["events"]
            if "effects" in list(self.table_code["classes"][clas].keys()):
                self.effects[clas] = self.table_code["classes"][clas]["effects"]
            if "variables" in list(self.table_code["classes"][clas].keys()):
                self.variables[clas] = self.table_code["classes"][clas]["variables"]
            if "conditions" in list(self.table_code["classes"][clas].keys()):
                self.condition[clas] = self.table_code["classes"][clas]["conditions"]
            if "assertions" in list(self.table_code["classes"][clas].keys()):
                self.assertion[clas] = self.table_code["classes"][clas]["assertions"]

    def initObject(self):
        dict_object = self.table_code["scheme"]["objects"]
        classes_init = list(self.table_code["classes"].keys())

        for obj, value in dict_object.items():
            name = value["class"]
            if name not in classes_init:
                print(Fore.RED + f"Класс {name} - не объявлен")
                self.objects = None
                return

            state = value["state"]
            states = [row[0] for row in self.stateTable[name]]
            states = states[1:]
            if state not in states:
                print(Fore.RED + f"Состояние {state} - не объявлено")
                self.objects = None
                return

            self.objects[obj] = self.Object(className=name,
                                            classInfo=self.table_code["classes"][name],
                                            currentState=state)
            print(f"Создан объект {Style.BRIGHT + obj + Style.RESET_ALL} класса {name} в начальном состоянии {state}.")

    def validationLink(self, link):
        objects_init = list(self.objects.keys())
        link_split = link.split('.')
        link_obj = link_split[0]
        if link_obj not in objects_init:
            print(Fore.RED + f"Объект {link_obj} не определён", end=" ")
            self.links = None
            return False

        link_func = link_split[1]

        index_ = None
        if "(" in link_func:
            index_ = link_func.index("(")
        if index_:
            link_list = ["".join(link_func[:index_])] + [link_func[index_:]]
        else:
            link_list = ["".join(link_func)]
        link_dict = {}
        if "(" in link_func:
            elements_after_colons = re.findall(r":([^,)]+)", link_list[1])
            link_dict[link_list[0]] = elements_after_colons
        else:
            link_dict[link_list[0]] = []

        class_obj = self.objects[link_obj].clas
        if link_dict.items() <= self.events[class_obj].items():
            return True
        if class_obj in self.effects:
            if link_dict.items() <= self.effects[class_obj].items():
                return True
        if class_obj in self.condition:
            if link_dict.items() <= self.condition[class_obj].items():
                return True
        if class_obj in self.assertion:
            if link_func in self.assertion[class_obj]:
                return True

        print(Fore.RED + f"Ошибка в {link_func}", end=" ")
        return False

    def validationInterface(self, interface, var_type):
        objects_init = list(self.objects.keys())
        interface_split = interface.split('.')
        interface_obj = interface_split[0]
        if interface_obj not in objects_init:
            print(Fore.RED + f"Объект {interface_obj} не определён", end=" ")
            self.links = None
            return False

        interface_func = interface_split[1]

        interface_dict = {interface_func: var_type}

        class_obj = self.objects[interface_obj].clas
        if interface_dict.items() <= self.events[class_obj].items():
            return True
        if class_obj in self.effects:
            if interface_dict.items() <= self.effects[class_obj].items():
                return True
        if class_obj in self.condition:
            if interface_dict.items() <= self.condition[class_obj].items():
                return True
        if class_obj in self.assertion:
            if interface_dict.items() <= self.assertion[class_obj].items():
                return True

        print(Fore.RED + f"Ошибка в {interface_func}", end=" ")
        return False

    def initLink(self):
        self.links = self.table_code["scheme"]["links"]
        print()
        for link in self.links:
            for key, value in link.items():
                if not self.validationLink(key):
                    print(Fore.RED + f"в связи {key} <- {value}")
                    self.links = None
                    return
                if not self.validationLink(value):
                    print(Fore.RED + f"в связи {key} <- {value}")
                    self.links = None
                    return
                print("Установлена связь " + Style.BRIGHT + f"{key} <- {value}")
        print()

    def initInterface(self):
        if "public" in self.table_code["scheme"]:
            self.public = self.table_code["scheme"]["public"]
            for interface in self.public:
                for key, value in interface.items():
                    if not self.validationInterface(key, value):
                        print(Fore.RED + f"в интерфейсе public: {key}")
                        self.public = None
                        return
        if "private" in self.table_code["scheme"]:
            self.private = self.table_code["scheme"]["private"]
            for interface in self.private:
                for key, value in interface.items():
                    if not self.validationInterface(key, value):
                        print(Fore.RED + f"в интерфейсе public: {key}")
                        self.private = None
                        return

    def validation(self):
        if not self.stateTable:
            return False
        if not self.objects:
            return False
        if not self.links:
            return False
        if hasattr(self, "public"):
            if not self.public:
                return False
        if hasattr(self, "private"):
            if not self.private:
                return False
        return True

    def validateAct(self, actions, clas):
        if actions is None:
            return True
        for act in actions:
            if ":=" in act:
                parts_assign = act.split(":=")
                var = parts_assign[0]
                if var not in self.variables[clas]:
                    return False
                continue
            if not self.checkVariable(act, clas):
                print(Fore.RED + f"Ошибка в {clas} - {act}", end=" ")
                return False
        return True

    def createCell(self, valueState, clas):
        if len(valueState) == 1:
            cell = self.Cell(actions=valueState[0]["actions"], end_state=valueState[0]["end_state"])
            return cell
        actions = []
        end_states = []
        for value in valueState:
            if not self.validateAct(value["actions"], clas):
                return None
            actions.append(value["actions"])
            end_states.append(value["end_state"])

        cell = self.Cell(actions=actions, end_state=end_states)
        condition = valueState[0]["condition"]
        if not self.checkVariable(condition, clas):
            print(Fore.RED + f"Ошибка в условии в {clas} {condition}", end=" ")
            return None
        cell.condition = condition
        return cell

    def checkVariable(self, event_name, clas):
        event = event_name
        if "(" in event_name:
            ind_start = event_name.index("(")
            ind_end = event_name.index(")")
            event = event_name[:ind_start]
            variablesList = event_name[ind_start + 1:ind_end]
            if "," in variablesList:
                variables = variablesList.split(',')
            else:
                variables = [variablesList]
        else:
            variables = []

        var_type = []
        for var in variables:
            typeV = None
            for varCl, varType in self.variables[clas].items():
                if var == varCl:
                    typeV = varType
                    break
            if not typeV:
                print(Fore.RED + f"Используется необъвленная переменная")
                return False
            var_type.append(typeV)

        reservfunc = list(dsl_info.reserved_func.keys())
        types_var_ev = []
        if event in reservfunc:
            types_var_ev = dsl_info.reserved_func[event]
        elif event in self.events[clas]:
            types_var_ev = self.events[clas][event]
        elif event in self.effects[clas]:
            types_var_ev = self.effects[clas][event]
        elif event in self.condition[clas]:
            types_var_ev = self.condition[clas][event]
        elif event in self.assertion[clas]:
            types_var_ev = self.assertion[clas][event]

        if var_type == types_var_ev:
            return True

        if not types_var_ev:
            print(Fore.RED + "Не принимает аргументы")
        elif not var_type:
            print(Fore.RED + "Ни один требуемый аргумент не передан")
        else:
            print(Fore.RED + "Неправильные типы переданных переменных")
        return False

    def createStateMatrix(self, events, states, clas):
        col_name = [""]
        col_name.extend(events)
        col_size = len(col_name)
        row_size = len(states)
        matrix = [[None for _ in range(col_size)] for _ in range(row_size)]
        matrix.insert(0, col_name)
        for i, state in enumerate(states):
            matrix[i + 1][0] = state
            for j in range(len(states[state])):
                event_name = list(states[state][j].keys())[0]
                # добавить проверку на соответсвие типов передаваемых variables
                ev_name = event_name
                if not self.checkVariable(event_name, clas):
                    print(Fore.RED + f"Ошибка в {clas} {state} {event_name}")
                    return None
                if "(" in event_name:
                    ind_b = event_name.index("(")
                    ev_name = event_name[:ind_b]

                if ev_name in col_name:
                    ind = col_name.index(ev_name)
                else:
                    if ev_name not in dsl_info.reserved_func:
                        print(Fore.RED + "Недопустимое событие")
                        return None
                    for row in matrix:
                        row.append(None)
                    ind = len(matrix[0]) - 1
                    matrix[0][ind] = ev_name
                cell = self.createCell(states[state][j][event_name], clas)
                if cell is None:
                    print(Fore.RED + f" в {state}")
                    return None
                matrix[i + 1][ind] = cell
        # print(matrix)
        return matrix

    def getStateTable(self):
        state_table = {}
        classes = list(self.table_code["classes"].keys())
        for clas in classes:
            events = list(self.table_code["classes"][clas]["events"].keys())
            states = self.table_code["classes"][clas]["states"]
            stateMatrix = self.createStateMatrix(events, states, clas)
            if not stateMatrix:
                return None
            state_table[clas] = stateMatrix
        return state_table

    def interpretCondition(self, obj, condition):
        link_conditions = f"{obj}.{condition}"
        obj_assert = None
        assertion = None
        for link in self.links:
            for key, value in link.items():
                if link_conditions not in key:
                    continue
                event_link = value
                parts = event_link.split('.')
                print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
                      f"Вычисление утверждения {Style.BRIGHT + parts[1] + Style.RESET_ALL} "
                      f"у объекта {Style.BRIGHT + parts[0] + Style.RESET_ALL} \n")
                obj_assert = parts[0]
                assertion = parts[1]
                break
        if not assertion:
            return not self.objects[obj].condition[condition]

        assert_ = self.objects[obj_assert].assertion[assertion]
        # нужно будет добавить проверку и других утверждений
        if "state" in assert_:
            parts = assert_.split("=")
            as_state = parts[1]
            if self.objects[obj_assert].state == as_state:
                print(f"{Style.BRIGHT + obj_assert + Style.RESET_ALL} >> "
                      f"{Style.BRIGHT + assertion} = True {Style.RESET_ALL}"
                      f"\n")
                return True
            else:
                print(f"{Style.BRIGHT + obj_assert + Style.RESET_ALL} >> "
                      f"{Style.BRIGHT + assertion} = False {Style.RESET_ALL}"
                      f"\n")
                return False

    def interpretActions(self, obj, actions):
        for act in actions:
            print(
                f"{Style.BRIGHT + obj + Style.RESET_ALL} >> Выполнение действия: {Style.BRIGHT + act + Style.RESET_ALL}...")
            if ":=" in act:
                parts = act.split(":=")
                var = parts[0]
                value = parts[1]  # по идее может быть сложным выражением, но пока будет для простых
                autoClass = self.objects[obj]
                autoClass.variables[var] = value
                print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> Действие: {Style.BRIGHT + act + Style.RESET_ALL} "
                      f"- выполнено")
                continue

            link_act = f"{obj}.{act}"
            for link in self.links:
                for key, value in link.items():
                    if link_act not in key:
                        continue
                    event_link = value
                    parts = event_link.split('.')
                    print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
                          f"Событие {Style.BRIGHT + parts[1] + Style.RESET_ALL} "
                          f"отправлено объекту {Style.BRIGHT + parts[0] + Style.RESET_ALL}\n")
                    self.interpret(event_link, False)
                    break

            print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> Действие: {Style.BRIGHT + act + Style.RESET_ALL} "
                  f"- выполнено")

    def interpret(self, interface, isUser):
        self.currentDepth += 1
        if self.currentDepth > self.maxDepth:
            print("Превышено времы исполнения программы")
            self.isLimitedTime = True
            return

        if hasattr(self, 'timer') and self.timer.is_active():
            obj_part = interface.split('.')[0]
            if interface in self._current_stop_commands:
                self.timer.cancel()
                print(f"{obj_part} >> Таймер отменён событием: {interface}")
                # return

        parts = interface.split('.')
        if len(parts) != 2:
            print(Fore.RED + "Некорректно введено событие. Вид: объект.событие")
            return

        if isUser:
            ev = parts[1]
            if "(" in ev:
                ind_b = ev.index("(")
                ev = ev[:ind_b]
            if ev in dsl_info.reserved_func:
                print(Fore.RED + "Введено зарезервированное состояние недоступное пользователю")
                return
            res = True
            if hasattr(self, "public"):
                public_interface = [list(interf.keys())[0] for interf in self.public]
                res = interface in public_interface
            if not res:
                if hasattr(self, "private"):
                    private_interface = [list(interf.keys())[0] for interf in self.private]
                    res = interface in private_interface
            if not res:
                print(Fore.RED + "Введена недопустимая команда. Повторите ещё раз")
                return

        # if hasattr(self, 'timer') and self.timer.is_active():
        #     return

        obj = parts[0]
        event = parts[1]
        print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
              f"Выполнение события {Style.BRIGHT + event + Style.RESET_ALL}...")
        if "(" in event:
            ind_b = event.index("(")
            event = event[:ind_b]

        autoClass = self.objects[obj]
        clas = autoClass.clas

        state_table = self.stateTable[clas]
        state_name = [row[0] for row in state_table]

        ind_event = state_table[0].index(event)
        ind_state = state_name.index(autoClass.state)
        cell = state_table[ind_state][ind_event]
        if not cell:
            print("Состояния не могут быть изменены, задайте другое событие")
            for obj in list(self.objects.keys()):
                print(f">> {obj}:{self.objects[obj].state}")
            print()
            return

        if hasattr(cell, "condition"):
            # посмотреть как учитывать условия в виде математического выражения
            if not autoClass.condition:
                print(Fore.RED + f"Класс не содержит условий. Проверьте код")
                return

            if cell.condition not in autoClass.condition:
                print(Fore.RED + f"Недопустимое условие")
                return

            print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
                  f"Проверка условия: {Style.BRIGHT + cell.condition + Style.RESET_ALL} ")
            autoClass.condition[cell.condition] = self.interpretCondition(obj, cell.condition)
            print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
                  f"{Style.BRIGHT + cell.condition} = {autoClass.condition[cell.condition]}")
            if autoClass.condition[cell.condition]:
                # autoClass.condition[cell.condition] = False
                end_state = cell.end_state[0]
                actions = cell.actions[0]
            else:
                # autoClass.condition[cell.condition] = True
                end_state = cell.end_state[1]
                actions = cell.actions[1]

        else:
            end_state = cell.end_state
            actions = cell.actions

        print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> "
              f"Переход: {Style.BRIGHT + autoClass.state + Style.RESET_ALL} -> "
              f"{Style.BRIGHT + end_state + Style.RESET_ALL}")
        autoClass.state = end_state

        if actions:
            self.interpretActions(obj, actions)

        print(f"{Style.BRIGHT + obj + Style.RESET_ALL} >> Cобытиe: {Style.BRIGHT + event + Style.RESET_ALL} "
              f"- выполнено\n")

        self.isAfter(autoClass.state, state_table, obj)

    def isAfter(self, state, stateTable, obj):
        if "after" not in stateTable[0]:
            return

        after_ind = stateTable[0].index("after")
        nameStates = [row[0] for row in stateTable[1:]]
        state_ind = nameStates.index(state) + 1
        cell = stateTable[state_ind][after_ind]
        if cell is None:
            return

        var_name = ""
        className = self.objects[obj].clas
        for triggerEv in self.table_code["classes"][className]['states'][state]:
            trigger = list(triggerEv.keys())[0]
            if 'after' not in trigger:
                continue
            start = trigger.find("(") + 1
            end = trigger.find(")")
            var_name = trigger[start:end] if start > 0 and end > start else None

        var_value = self.objects[obj].variables[var_name]
        if var_value is None:
            print(Fore.RED + f"Переменная {var_name} в объекте {obj} не проинициализирована")
            return

        # Функция для выполнения по завершении таймера
        def timer_complete():
            print(f"\n{obj} >> Таймер after завершился!")
            self.objects[obj].state = cell.end_state
            if cell.actions:
                self.interpretActions(obj, cell.actions)
            print(f"{Style.BRIGHT + obj+ Style.RESET_ALL} >> Переход: {Style.BRIGHT + state + Style.RESET_ALL} -> "
                  f"{Style.BRIGHT + cell.end_state + Style.RESET_ALL}\n")
            self.isAfter(cell.end_state, stateTable, obj)
            print(">>> ", end='', flush=True)

        # Запускаем таймер в отдельном потоке
        self.timer = TimerManager()
        self.timer.after(var_value, timer_complete)

        # Сохраняем команды для остановки
        self._current_stop_commands = [f"{obj}.{name_event}"
                                       for ind, name_event in enumerate(stateTable[0])
                                       if stateTable[state_ind][ind] is not None
                                       and name_event != "after"
                                       and name_event != ""]

        # current_stop_commands = []
        # for ind, name_event in enumerate(stateTable[0]):
        #     if stateTable[state_ind][ind] is not None and name_event != "after" and name_event != "":
        #         command = f"{obj}.{name_event}"
        #         new_command = None
        #         for link in self.links:
        #             for key, value in link.items():
        #                 if command not in value:
        #                     continue
        #                 new_command = key
        #                 break
        #         if new_command is None:
        #             current_stop_commands.append(command)
        #         else:
        #             current_stop_commands.append(new_command)
        #
        # self._current_stop_commands = current_stop_commands

        print(f"\n{obj} >> Таймер {Style.BRIGHT} after({var_value}) {Style.RESET_ALL} запущен. Команды остановки:")
        for cmd in self._current_stop_commands:
            print(f"        {cmd}")

        return

    def print_command(self, interface):
        for key, value in interface.items():
            if not value:
                print(f"{Style.BRIGHT + key + Style.RESET_ALL}")
                continue
            variable = ""
            for i in range(len(value)):
                if i == len(value) - 1:
                    variable += f"t{i}: {value[i]}"
                    continue
                variable += f"t{i}: {value[i]}, "
            print(Style.BRIGHT + f"{key}({variable})" + Style.RESET_ALL)

    def available_commands(self):
        if "public" in self.table_code["scheme"]:
            for interface in self.public:
                self.print_command(interface)

        if "private" in self.table_code["scheme"]:
            for interface in self.public:
                self.print_command(interface)

    def handle_command(self, command):
        if command == "":
            return True

        # Проверка команд остановки таймера
        if hasattr(self, '_current_stop_commands') and hasattr(self, 'timer') and self.timer.is_active():
            if command in self._current_stop_commands:
                self.timer.cancel()
                print(f"Таймер отменён командой: {command}")
                # Обрабатываем команду как обычное событие
                self.interpret(command, True)
                return True

        # if hasattr(self, 'timer') and self.timer.is_active():
        #     return True

        # Остальные команды...
        if command == "exitCode":
            print("Завершение текущей программы.")
            return False
        if command == "help":
            print("Доступные команды:")
            print(Fore.GREEN + "  exitCode - завершить текущую программу")
            print(Fore.GREEN + "  interfaces - получить список доступных интерфейсов")
            if hasattr(self, '_current_stop_commands') and hasattr(self, 'timer') and self.timer.is_active():
                print(Fore.GREEN + "  Команды для остановки таймера:")
                for cmd in self._current_stop_commands:
                    print(Fore.GREEN + f"  {cmd}")
            return True
        if command == "interfaces":
            print("Доступные интерфейсы:")
            self.available_commands()
            return True
        self.interpret(command, True)
        if self.isLimitedTime:
            return False
        return True


def InterpretCode(ast):
    try:
        # print("\nПостроение таблиц...")
        print("\nЗапуск интерпретатора...\n")
        print("Команда: " + Fore.GREEN + "help" + Fore.RESET + " - показать список команд\n")
        maxDepth = 120
        inter = Interpreter(ast, maxDepth)
        if not inter.validation():
            return

        while True:
            if hasattr(inter, 'timer') and not inter.timer.is_active() and inter.timer._completed:
                inter.timer._completed = False

            command = input(">>> ").strip()
            command = command.replace(">>>", "")
            if not inter.handle_command(command):
                break

    except RuntimeError as e:
        error_msg = f"Code generation error: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return
