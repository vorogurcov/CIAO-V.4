"""
Старый интерактивный интерпретатор (не очередная модель из статьи).
Запуск из корня репозитория: python legacy/run_interpreter.py
"""
import os
import sys

_LEGACY = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_LEGACY)
if _LEGACY not in sys.path:
    sys.path.insert(0, _LEGACY)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from build_ast import GetAST  # noqa: E402
from interpretator.interpreter import InterpretCode  # noqa: E402


def main() -> None:
    ciao_json = os.path.join(_REPO, "ciao.json")
    print("\nЗапуск legacy-интерпретатора...\n")
    print("Команда: help — справка\n")
    while True:
        command = input("> ").strip()
        command = command.replace(">", "")
        if command == "":
            continue
        if command == "exit":
            print("Завершение.")
            break
        ast = GetAST(ciao_json, command, False)
        if ast:
            InterpretCode(ast)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрервано.")
        sys.exit(0)
