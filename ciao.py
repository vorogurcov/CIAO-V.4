import graphviz
from copy import deepcopy
from build_ast import GetAST
from R_ast import GenerateCode
import sys
from interpretator.interpreter import InterpretCode


def handle_command(command):
    if command == "":
        return True
    if command == "exit":
        print("Завершение программы.")
        return False
    elif command == "help":
        print("Доступные команды:")
        print("  help - показать список команд")
        print("  exit - завершить программу")
    # elif command == "re-translate":
    #     ast = GetAST(ciao_json_file, command, False)
        # print(GenerateCode(ast, "_debug\\out.ciao")
    else:
        ast = GetAST(ciao_json_file, command, False)
        # print(GenerateCode(ast, "_debug\\out.ciao")
        if ast:
            InterpretCode(ast)
    return True


if __name__ == "__main__":
    ciao_json_file = 'ciao.json'
    print("Начало работы программы...")
    while True:
        print("\nВведите путь к файлу с кодом или команду")
        command = input("> ").strip()
        command = command.replace(">", "")
        if not handle_command(command):
            break
