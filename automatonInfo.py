from interpretator.interpreter import Interpreter
from build_ast import GetAST
from colorama import Fore, init, Style

init(autoreset=True)


def Initialize():
    try:
        ciao_json_file = 'C:\labpython\ciao\CIAO-V.3\ciao.json'
        command = input("> ").strip()
        command = command.replace(">", "")
        ast = GetAST(ciao_json_file, command, False)
        inter = Interpreter(ast)  # инициализируем все таблицы
        if not inter.validation():
            return
        return inter

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return


inter = Initialize()


def callTable(a, e, p):
    objects = inter.objects
    obj = objects[a]

    table = inter.stateTable[obj.clas]
    # проверка end_state на конечность Idle

    state_name = [row[0] for row in table]
    state = obj.state
    ind_event = table[0].index(e)
    ind_state = state_name.index(state)
    cell = table[ind_state][ind_event]
    print(f"\n{Style.BRIGHT + a + Style.RESET_ALL} >> "
          f"Выполнение события: {Style.BRIGHT + e + Style.RESET_ALL}")
    print(f"{Style.BRIGHT + a + Style.RESET_ALL} >> "
          f"Переход: {Style.BRIGHT + obj.state + Style.RESET_ALL} -> "
          f"{Style.BRIGHT + cell.end_state + Style.RESET_ALL}")
    print(f"Вызов следующего такта\n")

    obj.state = cell.end_state
    act = None
    if cell.actions:
        act = cell.actions[0]
    new_a = None
    new_e = None
    if cell.end_state == "Idle":
        return None, None, None, True

    link_act = f"{a}.{act}"
    for link in inter.links:
        for key, value in link.items():
            if link_act not in key:
                continue
            event_link = value
            parts = event_link.split('.')
            new_a = parts[0]
            new_e = parts[1]
            break

    return new_a, new_e, p, False
