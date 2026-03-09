from syntax import *
import dsl_info_ciao as dsl_info


def __GetRCode(node):
    # Обработка терминалов
    if TreeNode.Type.NONTERMINAL != node.type:
        # Возвращаем токен как элемент списка
        return [node.token.str]

    # Обработка нетерминалов
    result = []

    # Рекурсивная обработка дочерних узлов
    for i in range(len(node.childs)):
        child_code = __GetRCode(node.childs[i])
        result.extend(child_code)

    return result


def GenerateCode(ast, output_file=None):
    """
    Генерирует исполняемый код из AST
    Args:
        ast (TreeNode): Корень абстрактного синтаксического дерева
        output_file (str/None): Путь для сохранения результата (если требуется)
    Returns:
        str: Сгенерированный код или сообщение об ошибке
    """
    try:
        print("\nЗапуск ретранслятора...")
        generated_code = __GetRCode(ast)
        print("Восстановление кода...")
        code = format_text(generated_code)
        with open(output_file, 'w') as f:
            f.write(code)
        print(f"Путь до файла с восстановленным кодом: {output_file}")
        print("Результат работы ретранслятора:\n")
        return code

    except RuntimeError as e:
        error_msg = f"Code generation error: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return error_msg


def format_text(words):
    formatted_text = []
    indent_level = 0
    i = 0
    n = len(words)

    list_key = [info[0] for info in dsl_info.keys if info[1] == dsl_info.Terminal.char_key]
    list_key.extend(["new", "else"])
    third_level = [info[0] for info in dsl_info.keys if info[1] == dsl_info.Terminal.name]

    while i < n:
        word = words[i]

        # Первый уровень: начинается с "ciao"
        if word == "ciao":
            formatted_text.append(word + " " + words[i + 1])
            i += 2
            indent_level = 1

        # Второй уровень: начинается с "class" или "scheme"
        elif word == "class":
            indent_level = 1
            formatted_text.append("  " * indent_level + word + " " + words[i + 1])
            i += 2
            indent_level = 2

        elif word == "scheme":
            indent_level = 1
            formatted_text.append("  " * indent_level + word)
            i += 1
            indent_level = 2

        # Третий уровень: ключевые слова после "class" и "scheme"
        elif word in third_level:
            indent_level = 2
            formatted_text.append("  " * indent_level + word)
            i += 1
            indent_level = 3

        # Четвертый уровень: обработка строк после ключевых слов
        else:
            line = "  " * indent_level + word
            i += 1
            # list_key = ["->", "<-", "=", ":=", ":", ";", ",", ".", "new", "else", "(", ")", "[", "]", "/"]
            list_non_space = [".", ")", "[", "]"]
            is_last = False
            while i < n and (words[i] in list_key or
                             words[i - 1] in list_key):
                if i == n - 1:
                    is_last = True
                    break

                line += ("" if words[i] in list_non_space or
                               words[i - 1] in (list_non_space + ["("]) else " ") \
                        + words[i]
                if words[i] == ")" and not (words[i+1] in list_key):
                    i += 1
                    break
                i += 1

            formatted_text.append(line)
            if is_last:
                formatted_text.append(words[-1])
                break

    return "\n".join(formatted_text)

