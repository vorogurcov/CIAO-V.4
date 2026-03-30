"""
Точка входа: построение AST по грамматике CIAO (цепочка, согласованная с материалом статьи:
лексика → постобработка токенов → синтаксис → AST).

Интерпретатор с очередью событий (Dispatcher / Queue / Handler / Storage) в этом репозитории
не входит в костяк — см. каталог `legacy/`.
"""
import os
import sys

from build_ast import GetAST


def _repo_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    ciao_json = os.path.join(_repo_root(), "ciao.json")
    print("CIAO — построение AST (костяк по статье).\n")
    print("Команды: help — справка, exit — выход.\n")
    print("К старому интерпретатору/компилятору: см. legacy/README.md\n\n")
    while True:
        command = input("> ").strip()
        command = command.replace(">", "")
        if command == "":
            continue
        if command == "exit":
            print("Завершение.")
            break
        if command == "help":
            print("  Введите путь к файлу .ciao — будет построен AST.")
            print("  При задании debugInfoDir в ciao.json — SVG в каталог отладки.")
            print("  exit — выход.")
            continue
        ast = GetAST(ciao_json, command, False)
        if ast:
            print("OK: AST построен успешно.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрервано.")
        sys.exit(0)
