# Andy Castillo 18040

import os
import json
from clases import Log
from clases import CompilerDef

class ScannerGenerator:
    def __init__(self, atg_file, input_file):
        self.definition = None
        # self.FILE_LINES = []
        self.atg_file = atg_file
        self.input_file = input_file
        self.analyze_atg()
        self.build_scanner()
        self.run_scanner()

        self.non_terminals = []
        self.every_non_terminal = []
        self.get_simple_non_terminals()
        self.get_every_non_terminals()
        self.primeros = self.funcion_primero('EstadoInicial0')
        self.build_parser()

    def analyze_atg(self):
        print('\nLeyendo archivo atg...')

        try:
            input_file = open(self.atg_file, 'r')
        except IOError:
            Log.FAIL('\nArchivo no encontrado')
            exit()

        input_file_lines = input_file.readlines()
        input_file.close()

        self.definition = CompilerDef(input_file_lines)

        Log.OKGREEN('\nLectura de archivo completada!\n')

    def build_scanner(self):
        try:
            os.system('cp analizador.template.py analizador.py')

            characters_to_replace = ''
            characters_to_replace += 'CHARACTERS = {\n'
            for key, value in self.definition.CHARACTERS.items():
                characters_to_replace += f"    '{key}': '{value}',\n"
            characters_to_replace += '}'

            keywords_to_replace = ''
            keywords_to_replace += 'KEYWORDS = {\n'
            for key, value in self.definition.KEYWORDS.items():
                keywords_to_replace += f"    '{key}': '{value}',\n"
            keywords_to_replace += '}'

            tokens_re_to_replace = ''
            tokens_re_to_replace += 'TOKENS_RE = {\n'
            for key, value in self.definition.TOKENS_RE.items():
                tokens_re_to_replace += f"    '{key}': '{value}',\n"
            tokens_re_to_replace += '}'

            ignore_to_replace = ''
            ignore_to_replace += 'IGNORE = {\n'
            ignore_to_replace += f"    'char_numbers': {self.definition.WHITE_SPACE_DECL['char_numbers']},\n"
            ignore_to_replace += f"    'strings': {self.definition.WHITE_SPACE_DECL['strings']},\n"
            ignore_to_replace += '}'

            productions_to_replace = ''
            productions_to_replace += 'PRODUCTIONS = {\n'
            for key, value in self.definition.PRODUCTIONS.items():
                productions_to_replace += f"    '{key}': '{value}',\n"
            productions_to_replace += '}'

            with open('analizador.py', 'r') as file:
                data = file.read().replace('{{COMPILER_NAME}}', self.definition.COMPILER_NAME)
                data = data.replace('{{CHARACTERS}}', characters_to_replace)
                data = data.replace('{{KEYWORDS}}', keywords_to_replace)
                data = data.replace('{{TOKENS_RE}}', tokens_re_to_replace)
                data = data.replace('{{IGNORE}}', ignore_to_replace)
                data = data.replace('{{PRODUCTIONS}}', productions_to_replace)

            with open('analizador.py', 'w') as file:
                file.write(data)

            Log.OKGREEN('\nScanner generado.\n')
        except:
            Log.FAIL('\nError al construir scanner.\n')
            exit()

    def run_scanner(self):
        try:
            print('\nEjecutando scanner...')
            os.system(f'python3 analizador.py {self.input_file}')
        except:
            Log.FAIL('\nError ejecutando scanner.')
            exit()

    def get_every_non_terminals(self):
        for k, v in self.definition.PRODUCTIONS.items():
            nonTerminal = k
            if nonTerminal not in self.every_non_terminal:
                self.every_non_terminal.append(nonTerminal)

    def get_simple_non_terminals(self):
        for k, v in self.definition.PRODUCTIONS.items():
            nonTerminal = k[:-1]
            if nonTerminal not in self.non_terminals:
                self.non_terminals.append(nonTerminal)

    def funcion_primero(self, produccion, primeros = []):
        if produccion not in self.every_non_terminal:
            if produccion not in primeros:
                primeros.append(produccion)
        else:
            for k, prod in self.definition.PRODUCTIONS.items():
                string_production = self.definition.PRODUCTIONS[produccion].replace('«', '').replace('»', '').replace('±', '')
                if self.definition.CHARACTERS[string_production[0]] in k:
                    self.funcion_primero(k, primeros)
                elif self.definition.CHARACTERS[string_production[0]] not in self.non_terminals:
                    self.funcion_primero(self.definition.CHARACTERS[string_production[0]], primeros)
                
        return primeros

    def build_parser(self):
        parser_file_lines = []
        production_tokens = self.definition.get_production_tokens()

        starting_production = True
        tabs = 0
        on_if = False
        current_def = None
        for token in production_tokens:

            if starting_production:
                next_token = production_tokens[production_tokens.index(token) + 1]
                tabs = 1
                current_def = token.value
                if next_token.type == 'attrs':
                    ref = next_token.value.replace('<.', '').replace('.>', '').replace('ref', '').strip()
                    tabs_str = '\t' * tabs
                    parser_file_lines.append(f'{tabs_str}def {token.value}(self, {ref}):\n')
                else:
                    tabs_str = '\t' * tabs
                    parser_file_lines.append(f'{tabs_str}def {token.value}(self):\n')
                tabs = 2

            if token.type == 'iteration':
                if current_def == 'EstadoInicial':
                    while_condition = f"self.current_token['type'] in {self.primeros}"
                else:
                    strings_in_iteration = []
                    for t in production_tokens[production_tokens.index(token) + 1:]:
                        if t.type == 'string':
                            strings_in_iteration.append(t.value.replace('"', ''))
                        elif t.value == '}':
                            break

                    while_condition = f"self.current_token['value'] in {strings_in_iteration}"

                if token.value == '{':
                    tabs_str = '\t' * tabs
                    if current_def == 'EstadoInicial':
                        parser_file_lines.append(f'{tabs_str}if self.current_token["type"] not in {self.primeros}:\n')
                        tabs += 1
                        tabs_str = '\t' * tabs
                        parser_file_lines.append(f'{tabs_str}print("Error sintactico")\n')
                        tabs -= 1
                    tabs_str = '\t' * tabs
                    parser_file_lines.append(f'{tabs_str}while {while_condition}:\n')
                    tabs += 1
                elif token.value == '}':
                    tabs -= 1

            if token.type == 'semantic_action':
                action = token.value.replace('(.', '').replace('.)', '').strip()
                if 'return' in action and on_if:
                    tabs -= 1
                    parser_file_lines.append('\n')
                tabs_str = '\t' * tabs
                parser_file_lines.append(f'{tabs_str}{action}\n')

            if token.type == 'ident' and not starting_production:
                next_token = production_tokens[production_tokens.index(token) + 1]

                if next_token.type == 'attrs':
                    ref = next_token.value.replace('<.', '').replace('.>', '').replace('ref', '').strip()
                    tabs_str = '\t' * tabs
                    parser_file_lines.append(f'{tabs_str}{ref} = self.{token.value}({ref})\n')
                else:
                    tabs_str = '\t' * tabs
                    parser_file_lines.append(f'{tabs_str}self.{token.value}()\n')

            if token.type == 'token':
                tabs_str = '\t' * tabs
                parser_file_lines.append(f'{tabs_str}{token.value} = None\n')
                parser_file_lines.append(f'{tabs_str}if self.current_token["type"] == "{token.value}":\n')
                tabs += 1
                tabs_str = '\t' * tabs
                parser_file_lines.append(f'{tabs_str}{token.value} = float(self.current_token["value"])\n')
                parser_file_lines.append(f'{tabs_str}self.update_current_token()\n')
                tabs -= 1

            if token.type == 'string':
                if token.value != '")"':
                    if on_if:
                        tabs -= 1

                    on_if = True
                    parser_file_lines.append('\n')
                    tabs_str = '\t' * tabs
                    parser_file_lines.append(f'{tabs_str}if self.current_token["value"] == {token.value}:\n')
                    tabs += 1
                tabs_str = '\t' * tabs
                parser_file_lines.append(f'{tabs_str}self.update_current_token()\n')

            if token.type == 'option' and token.value == ']':
                on_if = False
                tabs -= 1
                parser_file_lines.append('\n')

            if token.type == 'final':
                tabs = 0
                on_if = False
                parser_file_lines.append('\n')
                starting_production = True
            else:
                starting_production = False

        self.build_parser_content(parser_file_lines)

    def build_parser_content(self, parser_file_lines):
        header = [
            '# Andy Castillo 18040\n',
            '\n',
        ]

        parser_class_header = [
            'class Parser():\n',
            '\tdef __init__(self, tokens):\n',
            '\t\tself.tokens = tokens\n',
            '\t\tself.current_token_index = 0\n',
            '\t\tself.current_token = self.tokens[self.current_token_index]\n',
            '\t\tself.EstadoInicial()\n',
            '\n',
            '\tdef update_current_token(self):\n',
            '\t\tif self.current_token_index < len(self.tokens) - 1:\n',
            '\t\t\tself.current_token_index += 1\n',
            '\t\t\tself.current_token = self.tokens[self.current_token_index]\n',
            '\n',
        ]

        try:

            with open('data.json', 'r') as file:
                instruction_json = json.load(file)

            class_init = [
                f'Parser({instruction_json})\n',
            ]

            with open('parser.py', 'w') as file:
                file.writelines(header)
                file.writelines(parser_class_header)
                file.writelines(parser_file_lines)
                file.writelines(class_init)
        except:
            Log.FAIL('\nError generando parser.')
            exit()
