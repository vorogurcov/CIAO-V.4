import re
import random


class Ciao3Translator:
    def __init__(self, input_text):
        self.after_timers = []
        self.public_calls = []
        self.input_text = input_text
        self.classes = {}   # { className: {SectionName: content, ...} }
        self.scheme = {}    # { "Objects": ..., "Links": ..., "Public": ..., "Private": ... }
        self.private_methods = {}  # { className: set(FunctionNames) }

    def parse(self):
        class_pattern = re.compile(r'class\s+(\w+)(.*?)(?=(?:class\s+\w+)|scheme|$)', re.DOTALL)
        for cls_match in class_pattern.finditer(self.input_text):
            cls_name = cls_match.group(1)
            cls_body = cls_match.group(2)
            self.classes[cls_name] = self.parse_class(cls_body)
        scheme_match = re.search(r'scheme(.*)', self.input_text, re.DOTALL)
        if scheme_match:
            scheme_text = scheme_match.group(1)
            self.scheme = self.parse_scheme(scheme_text)
        self.process_private_methods()

    def parse_class(self, body):
        sections = {}
        section_names = ['events', 'effects', 'variables', 'conditions', 'states', 'assertions']
        for sec in section_names:
            pattern = sec + r'\s+(.*?)(?=\n\s*(?:' + "|".join(section_names) + r')\s+|$)'
            match = re.search(pattern, body, re.DOTALL)
            if match:
                # Название секции приводим к виду с заглавной буквы (например, Events, Effects, Assertions и т.д.)
                sections[self.capitalize(sec)] = match.group(1).strip()
        return sections

    def parse_scheme(self, text):
        scheme_sections = {}
        section_names = ['objects', 'links', 'public', 'private']
        for sec in section_names:
            pattern = sec + r'\s+(.*?)(?=\n\s*(?:' + "|".join(section_names) + r')\s+|$)'
            match = re.search(pattern, text, re.DOTALL)
            if match:
                scheme_sections[self.capitalize(sec)] = match.group(1).strip()
        return scheme_sections

    def process_private_methods(self):
        obj_map = {}
        if "Objects" in self.scheme:
            obj_lines = [line.strip() for line in self.scheme["Objects"].split('\n') if line.strip()]
            for line in obj_lines:
                m = re.match(r'(\w+)\s*=\s*new\s+(\w+)\s*\((.*?)\)', line)
                if m:
                    obj_name, cls_name, _ = m.groups()
                    obj_map[obj_name] = cls_name
        private_methods = {}
        if "Private" in self.scheme:
            priv_lines = [line.strip() for line in self.scheme["Private"].split('\n') if line.strip()]
            for line in priv_lines:
                m = re.match(r'(\w+)\.(\w+)\s*\(.*?\)', line)
                if m:
                    obj_name, func_name = m.groups()
                    func_name = self.capitalize(func_name)
                    if obj_name in obj_map:
                        cls_name = obj_map[obj_name]
                        if cls_name not in private_methods:
                            private_methods[cls_name] = set()
                        private_methods[cls_name].add(func_name)
        self.private_methods = private_methods

    def generate_python_code(self):
        code_lines = []
        code_lines.append("# Сгенерированный код на Python из программы CIAO 3")
        code_lines.append("import random")
        code_lines.append("import inspect")
        code_lines.append("import threading")
        code_lines.append("")
        code_lines.append(
            """
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
            
"""
        )
        for cls_name, sections in self.classes.items():
            code_lines.extend(self.generate_class_code(cls_name, sections))
            code_lines.append("")
        code_lines.extend(self.generate_main_code())
        return "\n".join(code_lines)

    def generate_class_code(self, cls_name, sections):
        lines = []
        lines.append(f"class {cls_name}:")
        # Конструктор
        lines.append("    def __init__(self, init_state):")
        if "Variables" in sections:
            var_lines = [v.strip() for v in sections["Variables"].split('\n') if v.strip()]
            for var in var_lines:
                parts = var.split(':')
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    var_type = parts[1].strip()
                    lines.append(f"        self.{var_name} = None  # type: {var_type}")
        lines.append("        self.state = init_state")
        lines.append("        self.state_machine = self.build_state_machine()")
        lines.append("        self.timers = self.build_timers()")
        lines.append("        self.timer = None")
        lines.append("        self.links = {}")
        lines.append(f"        print(f\"{cls_name} инициализирован с состоянием {{init_state}}\")")
        lines.append(f"        self.name = \"{cls_name}\"")
        lines.append("")
        lines.append("    def addLink(self, name: str, func) -> None:")
        lines.append("        self.links[name] = func")
        lines.append("")
        # Events
        if "Events" in sections:
            event_lines = [line.strip() for line in sections["Events"].split('\n') if line.strip()]
            for event in event_lines:
                m = re.match(r'(\w+)\s*\((.*?)\)', event)
                if m:
                    event_name = self.capitalize(m.group(1))
                    params = m.group(2).strip()
                else:
                    event_name = self.capitalize(event)
                    params = None
                param_names = [p.split(':')[0].strip() for p in params.split(',')] if params else []
                method_name = f"__{event_name}" if cls_name in self.private_methods and event_name in self.private_methods[cls_name] else event_name
                lines.append(f"    def {method_name}(self{', ' + ', '.join(param_names) if param_names else ''}):")
                if method_name.startswith("__"):
                    lines.append(f"        print('Запущен private event {event_name}')")
                lines.append(f"        print(\"{cls_name}: Event {event_name}({', '.join(param_names)})\")")
                lines.append(f"        event = \"{event_name}\"")
                lines.append(f"        if event in self.state_machine[self.state]:")
                call_params = ", ".join(param_names) if param_names else ""
                lines.append(f"            self.state_machine[self.state][event](self{', ' + call_params if call_params else ''})")
                lines.append("        else:")
                lines.append(f"            print(f'Invalid event {{event}} for state {{self.state}}')")
                lines.append(f"        if '{event_name}' in self.links:")
                if param_names:
                    lines.append(f"            self.links['{event_name}']({','.join(param_names)})")
                else:
                    lines.append(f"            self.links['{event_name}']()")
                lines.append("")
        # Effects
        if "Effects" in sections:
            effect_lines = [line.strip() for line in sections["Effects"].split('\n') if line.strip()]
            for effect in effect_lines:
                m = re.match(r'(\w+)\s*\((.*?)\)', effect)
                if m:
                    effect_name = self.capitalize(m.group(1))
                    args = m.group(2)
                else:
                    effect_name = self.capitalize(effect)
                    args = None
                if args:
                    args = args.split(',')
                    args = ['self.' + arg.split(':')[0].strip() for arg in args]
                method_name = f"__{effect_name}" if cls_name in self.private_methods and effect_name in self.private_methods[cls_name] else effect_name
                lines.append(f"    def {method_name}(self):")
                if method_name.startswith("__"):
                    lines.append(f"        print('Запущен private effect {effect_name}')")
                lines.append(f"        print(\"{cls_name}: Effect {effect_name} вызван\")")
                lines.append(f"        if '{effect_name}' in self.links:")
                if args:
                    lines.append(f"            self.links['{effect_name}']({','.join(args)})")
                else:
                    lines.append(f"            self.links['{effect_name}']()")
                lines.append("")
        # Conditions
        if "Conditions" in sections:
            cond_lines = [line.strip() for line in sections["Conditions"].split('\n') if line.strip()]
            for cond in cond_lines:
                m = re.match(r'(\w+)(?:\s*\((.*?)\))?', cond)
                if m:
                    cond_name = self.capitalize(m.group(1))
                    params = m.group(2)
                    if params is not None:
                        params = params.split(',')
                        params = [param.split(':')[0].strip() for param in params]
                        condition_expr = " and ".join([f"(self.{p} == {p})" for p in params])
                        lines.append(f"    def {cond_name}(self, {', '.join(params)}):")
                        lines.append(f"        result = {condition_expr}")
                        lines.append(f"        print(\"Condition {cond_name}({', '.join(params)}) =>\", result)")
                        lines.append("        return result")
                    else:
                        lines.append(f"    def {cond_name}(self):")
                        lines.append(f"        if \"{cond_name}\" in self.links:")
                        lines.append(f"            result = self.links['{cond_name}']()")
                        lines.append("        else:")
                        lines.append("            result = random.choice([True, False])")
                        lines.append(f"        print(\"Condition {cond_name}() =>\", result)")
                        lines.append("        return result")
                    lines.append("")
        # Assertions
        if "Assertions" in sections:
            assert_lines = [line.strip() for line in sections["Assertions"].split('\n') if line.strip()]
            for line in assert_lines:
                parts = line.split("<-")
                if len(parts) == 2:
                    func_name = self.capitalize(parts[0].strip())
                    expr = parts[1].strip()
                    expr = re.sub(r'(?<![=])=(?![=])', "==", expr)
                    # Для остальных идентификаторов добавляем self. (упрощенно)
                    expr = re.sub(r'\b([a-z]\w*)\b', r'self.\1', expr)
                    # Специальная обработка: если сравнение производится для self.state, то значение оборачивается в кавычки
                    expr = re.sub(r'self\.state\s*==\s*(\w+)', r'self.state == "\1"', expr)
                    lines.append(f"    def {func_name}(self):")
                    lines.append(f"        return {expr}")
                    lines.append("")
        # State Machine
        lines.append("    def build_state_machine(self):")
        lines.append("        state_machine = {}")
        if "States" in sections:
            state_lines = [line for line in sections["States"].split('\n') if line.strip()]
            index = 0
            while index < len(state_lines):
                line = state_lines[index].strip()
                if line.startswith("[else]"):
                    index += 1
                    continue
                if "/" in line:
                    regex = r'(\w+)\s*->\s*(\w+)(?:\s*\((.*?)\))?\s*(?:\[(.*?)\])?\s*/\s*(.*?)\s*->\s*(\w+)'
                    m = re.match(regex, line)
                    if m:
                        start_state, event, event_params, condition, effects_str, end_state = m.groups()
                    else:
                        lines.append(f"        # Не удалось разобрать: {line}")
                        index += 1
                        continue
                    if event == 'after':
                        self.after_timers.append((start_state, event_params))
                        event_params = None
                    param_names = []
                    if event_params and event_params.strip():
                        param_names = [p.split(':')[0].strip() for p in event_params.split(',')]
                    lambda_params = ", ".join(param_names)
                    effects = [e.strip() for e in effects_str.split(';') if e.strip()]
                    effect_calls = []
                    for eff in effects:
                        m_assign = re.match(r'(\w+)\s*:=\s*(.+)', eff)
                        if m_assign:
                            var, value = m_assign.groups()
                            effect_calls.append(f"setattr(self, '{var}', {value.strip()})")
                        else:
                            m_eff = re.match(r'(\w+)(?:\s*\((.*?)\))?', eff)
                            if m_eff:
                                eff_name = self.capitalize(m_eff.group(1))
                                if cls_name in self.private_methods and eff_name in self.private_methods[cls_name]:
                                    effect_calls.append(f"self.__{eff_name}()")
                                else:
                                    effect_calls.append(f"self.{eff_name}()")
                            else:
                                effect_calls.append(f"self.{self.capitalize(eff)}()")
                    effect_calls_str = ", ".join(effect_calls)
                    if condition:
                        if '(' not in condition:
                            condition += "()"
                        m_cond = re.match(r'(\w+)(.*)', condition)
                        if m_cond:
                            cond_func, rest = m_cond.groups()
                            condition = self.capitalize(cond_func) + rest
                        else:
                            condition = self.capitalize(condition)
                        else_effects = None
                        else_end_state = None
                        if index+1 < len(state_lines) and state_lines[index+1].strip().startswith("[else]"):
                            m_else = re.match(r'\[else\]\s*/\s*(.*?)\s*->\s*(\w+)', state_lines[index+1].strip())
                            if m_else:
                                else_effects, else_end_state = m_else.groups()
                                index += 1
                        if else_effects:
                            else_eff_list = [e.strip() for e in else_effects.split(';') if e.strip()]
                            else_calls = []
                            for eff in else_eff_list:
                                m_assign = re.match(r'(\w+)\s*:=\s*(.+)', eff)
                                if m_assign:
                                    var, value = m_assign.groups()
                                    else_calls.append(f"setattr(self, '{var}', {value.strip()})")
                                else:
                                    m_eff = re.match(r'(\w+)(?:\s*\((.*?)\))?', eff)
                                    if m_eff:
                                        eff_name = self.capitalize(m_eff.group(1))
                                        if cls_name in self.private_methods and eff_name in self.private_methods[cls_name]:
                                            else_calls.append(f"self.__{eff_name}()")
                                        else:
                                            else_calls.append(f"self.{eff_name}()")
                                    else:
                                        else_calls.append(f"self.{self.capitalize(eff)}()")
                            else_calls_str = ", ".join(else_calls)
                            lambda_expr = f"(lambda self{', ' + lambda_params if lambda_params else ''}: (self.change_state('{end_state}'), {effect_calls_str}, self.check_timer()) if self.{condition} else (self.change_state('{else_end_state}'), {else_calls_str}, self.check_timer()))"
                        else:
                            lambda_expr = f"(lambda self{', ' + lambda_params if lambda_params else ''}: (self.change_state('{end_state}'), {effect_calls_str}, self.check_timer()) if self.{condition} else None)"
                    else:
                        lambda_expr = f"(lambda self{', ' + lambda_params if lambda_params else ''}: (self.change_state('{end_state}'), {effect_calls_str}, self.check_timer()))"
                else:
                    regex2 = r'(\w+)\s*->\s*(\w+)(?:\s*\((.*?)\))?\s*(?:\[(.*?)\])?\s*->\s*(\w+)'
                    m = re.match(regex2, line)
                    if m:
                        start_state, event, event_params, condition, end_state = m.groups()
                    else:
                        lines.append(f"        # Не удалось разобрать: {line}")
                        index += 1
                        continue
                    if event == 'after':
                        self.after_timers.append((start_state, event_params))
                        event_params = None
                    param_names = []
                    if event_params and event_params.strip():
                        param_names = [p.split(':')[0].strip() for p in event_params.split(',')]
                    lambda_params = ", ".join(param_names)
                    if condition:
                        if '(' not in condition:
                            condition += "()"
                        m_cond = re.match(r'(\w+)(.*)', condition)
                        if m_cond:
                            cond_func, rest = m_cond.groups()
                            condition = self.capitalize(cond_func) + rest
                        else:
                            condition = self.capitalize(condition)
                        else_effects = None
                        else_end_state = None
                        if index + 1 < len(state_lines) and state_lines[index + 1].strip().startswith("[else]"):
                            m_else = re.match(r'\[else\]\s*/\s*(.*?)\s*->\s*(\w+)', state_lines[index + 1].strip())
                            if m_else:
                                else_effects, else_end_state = m_else.groups()
                                index += 1
                        if else_effects:
                            else_eff_list = [e.strip() for e in else_effects.split(';') if e.strip()]
                            else_calls = []
                            for eff in else_eff_list:
                                m_assign = re.match(r'(\w+)\s*:=\s*(.+)', eff)
                                if m_assign:
                                    var, value = m_assign.groups()
                                    else_calls.append(f"setattr(self, '{var}', {value.strip()})")
                                else:
                                    m_eff = re.match(r'(\w+)(?:\s*\((.*?)\))?', eff)
                                    if m_eff:
                                        eff_name = self.capitalize(m_eff.group(1))
                                        if cls_name in self.private_methods and eff_name in self.private_methods[
                                            cls_name]:
                                            else_calls.append(f"self.__{eff_name}()")
                                        else:
                                            else_calls.append(f"self.{eff_name}()")
                                    else:
                                        else_calls.append(f"self.{self.capitalize(eff)}()")
                            else_calls_str = ", ".join(else_calls)
                            lambda_expr = f"(lambda self{', ' + lambda_params if lambda_params else ''}: (self.change_state('{end_state}'), self.check_timer()) if self.{condition} else (self.change_state('{else_end_state}'), {else_calls_str}, self.check_timer()))"
                        else:
                            lambda_expr = f"(lambda self{', ' + lambda_params if lambda_params else ''}: (self.change_state('{end_state}'), self.check_timer()) if self.{condition} else None)"
                    else:
                        lambda_expr = f"(lambda self{', ' + lambda_params if lambda_params else ''}: (self.change_state('{end_state}'), self.check_timer()))"
                lines.append(f"        if '{start_state}' not in state_machine:")
                lines.append(f"            state_machine['{start_state}'] = {{}}")
                lines.append(f"        state_machine['{start_state}']['{self.capitalize(event)}'] = {lambda_expr}")
                index += 1
        lines.append("        return state_machine")
        lines.append("")
        # Timers
        lines.append("    def build_timers(self):")
        lines.append("        timers = {}")
        for state, t in self.after_timers:
            lines.append(f"        timers[\"{state}\"] = \"{t}\"")
        lines.append("        return timers")
        lines.append("")
        lines.append("    def change_state(self, new_state):")
        lines.append("        if self.timer:")
        lines.append("            self.timer.cancel()")
        lines.append("        print(f\"{self.__class__.__name__}: смена состояния {self.state} -> {new_state}\")")
        lines.append("        self.state = new_state")
        lines.append("")
        lines.append("    def check_timer(self):")
        lines.append("        if self.state in self.timers:")
        lines.append("            self.timer = ResettableTimer(self, getattr(self, self.timers[self.state]), self.state_machine[self.state]['After'])")
        lines.append("            self.timer.start()")
        return lines

    def generate_run_code(self):
        lines = []
        lines.append("def run(*args):")
        lines.append("    for obj in args:")
        lines.append("        try:")
        for call in self.public_calls:
            lines.append(f"            obj.{call}")
        lines.append("        except Exception as e:")
        lines.append("            pass")
        lines.append("")
        return lines

    def generate_main_code(self):
        lines = []
        lines.append("def main():")
        obj_map = {}
        if "Objects" in self.scheme:
            obj_lines = [line.strip() for line in self.scheme["Objects"].split('\n') if line.strip()]
            for line in obj_lines:
                m = re.match(r'(\w+)\s*=\s*new\s+(\w+)\s*\((.*?)\)', line)
                if m:
                    obj_name, cls_name, init_state = m.groups()
                    obj_map[obj_name] = cls_name
                    lines.append(f"    {obj_name} = {cls_name}('{init_state}')")
        if "Links" in self.scheme:
            link_lines = [line.strip() for line in self.scheme["Links"].split('\n') if line.strip()]
            for line in link_lines:
                m = re.match(r'(\w+)\.(\w+)\s*<-\s*(\w+)\.(\w+)(?:\s*\((.*?)\))?', line)
                if m:
                    target, link_name, source, func_name, params = m.groups()
                    cls = obj_map.get(source, "")
                    if cls in self.private_methods and self.capitalize(func_name) in self.private_methods[cls]:
                        func_ref = f"{source}.__{self.capitalize(func_name)}"
                    else:
                        func_ref = f"{source}.{self.capitalize(func_name)}"
                    lines.append(f"    {target}.addLink('{self.capitalize(link_name)}', {func_ref})")
        if "Public" in self.scheme:
            public_lines = [line.strip() for line in self.scheme["Public"].split('\n') if line.strip()]
            # Собираем список строк вызова public-функций
            pub_calls = []
            for line in public_lines:
                m = re.match(r'(\w+)\.(\w+)\s*\((.*?)\)', line)
                if m:
                    obj_name, event, params = m.groups()
                    params = params.strip()
                    if params:
                        call_str = f"{self.capitalize(event)}({random.randint(0,100)})"
                    else:
                        call_str = f"{self.capitalize(event)}()"
                    pub_calls.append(call_str)
                else:
                    m = re.match(r'(\w+)\.(\w+)', line)
                    if m:
                        obj_name, event = m.groups()
                        call_str = f"{self.capitalize(event)}()"
                        pub_calls.append(call_str)
            self.public_calls.extend(pub_calls)
        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    main()")
        lines.append("    # Функция run доступна, но не вызывается автоматически")
        run_lines = self.generate_run_code()
        run_lines.extend(lines)
        return run_lines

    def capitalize(self, name):
        return name[0].upper() + name[1:] if name else name

def main_translator():
    input_filename = "input.ciao"
    with open(input_filename, 'r', encoding='utf-8') as f:
        input_text = f.read()
    translator = Ciao3Translator(input_text)
    translator.parse()
    output_code = translator.generate_python_code()
    output_filename = "output.py"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(output_code)
    print(f"Translation complete. Output written to {output_filename}")
    print("Executing generated code:")
    with open(output_filename, 'r', encoding='utf-8') as f:
        code = f.read()
    exec(code, globals())


if __name__ == '__main__':
    main_translator()

