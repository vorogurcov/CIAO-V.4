import pathlib
import pydot
import dsl_info_ciao as dsl_info
from syntax.core import *
import importlib


def __GetType(shape):
    if shape[0] == '"':
        shape = shape[1:-1]
    if "plaintext" == shape:
        return NodeType.START
    if "point" == shape:
        return NodeType.END
    if "box" == shape:
        return NodeType.NONTERMINAL
    if "diamond" == shape:
        return NodeType.TERMINAL
    if "oval" == shape:
        return NodeType.KEY
    print(f"Unsupported shape - {shape}")
    return None


# dsl_info - название нетерминалов - ключей и значений
# *.gv
# здесь работаем с файлами .гв и dsl_info
# возвращаем "Nonterminal.<name>"
def GetSyntaxDesription(diagramsDir, dsl_info_file):
    # print("ciao.json -> ciao_gv/ -> *.gv")
    files = pathlib.Path(diagramsDir).glob('**/*.gv')
    res = dict()
    for file in files:
        #print(f"Process {file.name}")
        source = pydot.graph_from_dot_file(file)
        diagram = source[0]
        a = diagram.get_type()
        if "digraph" != diagram.get_type():
            print("Virt diagram must be digraph")
            return None
        
        nodes = diagram.get_nodes()
        edges = diagram.get_edges()

        virtNodes = dict()
        startArray = []
        endArray = []
        for dotNode in nodes:
            attribs = dotNode.obj_dict["attributes"]
            
            str = "" if "label" not in attribs else attribs["label"]
            nodeType = __GetType("box" if "shape" not in attribs else attribs["shape"])
            if nodeType is None:
                return None
            if len(str) != 0 and str[0] == '"':
                str = str[1:-1]
            node = Node(nodeType, str)
            virtNodes[dotNode.get_name()] = node
            if NodeType.NONTERMINAL == nodeType:
                node.nonterminal = dsl_info.Nonterminal(str)
            elif NodeType.TERMINAL == nodeType:
                node.terminal = dsl_info.Terminal(str)
            elif NodeType.START == nodeType:
                startArray.append(node)
            elif NodeType.END == nodeType:
                endArray.append(node)
        if len(startArray) != 1:
            print(f"Incorrect number of starts")
            return None
        if len(endArray) != 1:
            print(f"Incorrect number of ends")
            return None
        for nodeName, node in virtNodes.items():
            outgoingEdges = [(edge.obj_dict["points"][1],
                              "" if "label" not in edge.obj_dict["attributes"] else edge.obj_dict["attributes"]["label"])
                             for edge in edges if edge.obj_dict["points"][0] == nodeName]
            for edge in outgoingEdges:
                if len(edge[1]) != 0 and edge[1][0] == '"':
                    code = edge[1][1:-1]
                else:
                    code = edge[1]
                node.nextNodes.append((virtNodes[edge[0]], code.replace('\\"', '"')))

        res[dsl_info.Nonterminal[diagram.get_name()]] = startArray[0]
    # print(res)
    return res
