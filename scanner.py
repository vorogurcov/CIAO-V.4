#import dsl_info
import dsl_info_ciao as dsl_info
from dsl_token import Token
import sys
import re
from colorama import Fore, init, Style


init(autoreset=True)


def __SkipSpaces(code, pos):
    for i in range(pos, len(code)):
        if not code[i].isspace():
            return i
    return len(code)


def __GetCurrentToken(code, pos):
    for terminal, regex in dsl_info.tokenRegularExpressions:
        result = re.match(regex, code[pos:])
        if not result:
            continue
        token = Token(Token.Type.TERMINAL)
        token.terminalType = terminal
        token.str = result.group(0)
        return token, pos + len(token.str)
    print(Fore.RED + f"Failed to recognize token in pos {pos}")
    return None, None


def Tokenize(code):
    size = len(code)
    pos = 0
    tokens = []
    pos = __SkipSpaces(code, pos)
    while pos < size:
        token, pos = __GetCurrentToken(code, pos)
        if token is None and pos is None:
            return None
        tokens.append(token)
        pos = __SkipSpaces(code, pos)
    return tokens


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Need only one argument: program text path")
        sys.exit()
    with open(sys.argv[1], 'r') as file:
        tokenList = Tokenize(file.read())
        print("tokens:")
        for token in tokenList:
            print(f"TYPE: '{token.terminalType.name}', STRING: '{token.str}'.")
