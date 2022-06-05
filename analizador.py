# Andy Castillo 18040

import sys
import json
from clases import AFD
from clases import Log

ANY_BUT_QUOTES = '«««««««««««««««l¦d»¦s»¦o»¦ »¦(»¦)»¦/»¦*»¦=»¦.»¦|»¦[»¦]»¦{»¦}»'

entry_file_name = sys.argv[1]

# CHARACTERS
CHARACTERS = {
    'A': '0123456789',
    'B': 'D',
    ' ': ' ',
    'S': ';',
    'T': '+',
    'U': '*',
    'b': 'Instruccion',
    'c': 'Expresion',
    'd': 'Termino',
    'e': 'Factor',
    'f': 'Numero',
    'g': 'numeroToken',
}

# KEYWORDS
KEYWORDS = {
    'NEWLINE': '\\n',
}

# TOKENS RE
TOKENS_RE = {
    'f': 'S',
    '+': 'T',
    'por': 'U',
    'numeroToken': 'A«A»±',
    'space': ' ',
}

# Whitespace definition
IGNORE = {
    'char_numbers': [9, 20],
    'strings': [],
}

# PRODUCTIONS
PRODUCTIONS = {
    'EstadoInicial0': '«bS»±',
    'Instruccion0': 'c',
    'Expresion0': 'd«Td»±',
    'Termino0': 'e«Ue»±',
    'Factor0': 'f',
    'Numero0': 'g',
}


TOKENS = []

class Token():
    def __init__(self, value, line, column):
        self.value = value
        self.line = line + 1
        self.column = column + 1
        self.type = Token.get_type_of(value)

    def __str__(self):
        return f'Token({self.value}, {self.type}, {self.line}, {self.column})'

    @classmethod
    def get_type_of(cls, word):
        if word in KEYWORDS.values():
            return 'KEYWORD'
        elif word in [chr(number) for number in IGNORE['char_numbers']] or word in IGNORE['strings']:
            return 'IGNORE'
        else:
            for token_type, re in TOKENS_RE.items():
                if AFD(re.replace('a', ANY_BUT_QUOTES)).accepts(word, CHARACTERS):
                    return token_type
        return 'ERROR'

def eval_line(entry_file_lines, line, line_index):
    analyzed_lines = 1
    line_position = 0
    current_line_recognized_tokens = []
    while line_position < len(line):
        current_token = None
        next_token = None
        avance = 0
        continuar = True
        while continuar:
            if current_token and next_token:
                if current_token.type != 'ERROR' and next_token.type == 'ERROR':
                    avance -= 1
                    continuar = False
                    break

            if line_position + avance > len(line):
                continuar = False
                break

            if line_position + avance <= len(line):
                current_token = Token(line[line_position:line_position + avance], line_index, line_position)

            avance += 1

            if line_position + avance <= len(line):
                next_token = Token(line[line_position:line_position + avance], line_index, line_position)

        line_position = line_position + avance


        if current_token and current_token.type != 'ERROR':
            TOKENS.append(current_token)
            current_line_recognized_tokens.append(current_token)
        else:
            print()

            if line_position == len(line) + 1 and len(current_line_recognized_tokens) != 0:
                TOKENS.append(current_token)

            if line_position == len(line) + 1 and len(current_line_recognized_tokens) == 0:
                if line_index < len(entry_file_lines) - 1:
                    new_line = line + ' ' + entry_file_lines[line_index + 1].replace('\n', '\\n')
                    line_index += 1
                    analyzed_lines += eval_line(entry_file_lines, new_line, line_index)

    return analyzed_lines

def run():
    try:
        entry_file = open(entry_file_name, 'r')
    except Exception as e:
        print('Error: ', e)
        exit()

    entry_file_lines = entry_file.readlines()
    entry_file.close()

    line_index = 0
    while line_index < len(entry_file_lines):
        line = entry_file_lines[line_index].replace('\n', '\\n')
        analyzed_lines = eval_line(entry_file_lines, line, line_index)
        line_index += analyzed_lines

    # Log.OKGREEN('\n\nTokens generados')
    # for token in TOKENS:
    #     if token.type == 'ERROR':
    #         Log.WARNING(token)
    #     else:
    #         Log.INFO(token)

    lexical_errors = False
    for token in TOKENS:
        if token.type == 'ERROR':
            Log.FAIL(f'Error lexico en la linea {token.line} columna {token.column}: {token.value}')
            lexical_errors = True

    if lexical_errors:
        Log.FAIL('\nErrores lexicos en el archivo atg')

    # -------------------------------------------------------
    # WRITE TOKEN FLOW FILE
    # -------------------------------------------------------
    try:
        tokens_flow_file = open('tokens-flow', 'w+')

        for token in TOKENS:
            if token.type == 'IGNORE':
                continue
            if token.type == 'KEYWORD':
                if token.value == '\\n':
                    continue
                    # tokens_flow_file.write('\n')
                else:
                    tokens_flow_file.write(f'{token.value}')
            elif token.type == 'space':
                # tokens_flow_file.write(f'{token.value}')
                continue
            else:
                tokens_flow_file.write(f'{token.type}')
            tokens_flow_file.write(' ')

        Log.OKGREEN('\nTokens generados')
    except:
        Log.FAIL('\nError al escribir archivo de tokens.')
        exit()
    finally:
        tokens_flow_file.close()


try:
    run()
except Exception as e:
    Log.FAIL('Error: ', e)

# Generate tokens file
instruction = []
for token in TOKENS:
    if token.type == 'IGNORE':
        continue
    if token.type == 'KEYWORD':
        if token.value == '\\n':
            continue
        else:
            instruction.append({
                'type': token.type,
                'value': token.value,
            })
    elif token.type == 'space':
        continue
    else:
        instruction.append({
            'type': token.type,
            'value': token.value,
        })

with open('data.json', 'w', encoding='utf-8') as file:
    json.dump(instruction, file, ensure_ascii = False, indent = 4)
