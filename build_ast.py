from scanner import Tokenize
from afterscan import Afterscan
from dsl_token import *
import dsl_info_ciao as dsl_info
from syntax import *
import graphviz
import json
import pathlib
import os


def __RenderAst(diagramName, ast, debugInfoDir, view):
    if debugInfoDir is None:
        return
    h = graphviz.Digraph(diagramName, format='svg')
    i = 1
    nodes = [(ast, 0)]
    while len(nodes):
        node = nodes[0]
        if TreeNode.Type.NONTERMINAL == node[0].type:
            h.node(str(i),
                   f"{node[0].nonterminalType}",
                   # + (f"\nattribute: {node[0].attribute}" if node[0].attribute else ""),
                   shape='box')
            if node[1] != 0:
                h.edge(str(node[1]), str(i))
            nodes += [(child, i) for child in node[0].childs]
        else:
            token = node[0].token
            if Token.Type.TERMINAL == token.type:
                h.node(str(i),
                       f"{token.str}",
                       # +(f"\nattribute: {token.attribute}" if token.attribute else ""),
                       shape='diamond')
            elif Token.Type.KEY == token.type:
                h.node(str(i), f"{token.str}",
                       # +(f"\nattribute: {token.attribute}" if token.attribute else ""),
                       shape='oval')
            h.edge(str(node[1]), str(i))
        nodes = nodes[1:]
        i += 1

    # Рендерим граф в файл
    output_path = h.render(directory=debugInfoDir, view=False)  # Не открываем файл сразу
    print("AST построено")
    print("Путь до файла с AST: ", output_path)
    # Открываем файл, если параметр view=True
    if view:
        import webbrowser
        webbrowser.open(output_path)


def GetAST(jsonFile, codeFile, is_render):
    with open(jsonFile, 'r') as jsonFile:
        jsonData = json.loads(jsonFile.read())
    syntaxInfo = GetSyntaxDesription(jsonData["syntax"])
    if syntaxInfo is None:
        return
    if "debugInfoDir" in jsonData:
        debugInfoDir = pathlib.Path(jsonData["debugInfoDir"])
        if not debugInfoDir.exists():
            os.mkdir(debugInfoDir)
    else:
        debugInfoDir = None

    try:
        with open(codeFile, 'r') as file:
            code = file.read()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

    print("Строим AST...")
    tokenList = Tokenize(code)
    if tokenList is None:
        return None
    tokenList = Afterscan(tokenList)

    ast = BuildAst(syntaxInfo, dsl_info.axiom, tokenList)
    if ast is None:
        return None
    __RenderAst(codeFile, ast, debugInfoDir, is_render)
    return ast
