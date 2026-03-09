from enum import Enum


class Terminal(Enum):
    number = "number"
    name = "name"
    char_key = "char_key"
    string = "string"


tokenRegularExpressions = [
    (Terminal.number, r"-?\d+(?:\.\d*)?"),
    (Terminal.name, r"[\w^\d][\w]*"),
    (Terminal.char_key, r"\(|\)|\,|\.|\:\=|\:|\[|\]|\-\>|\<\-|\;|\=|\||\&|\/|\*|\-|\+|\!"),
    (Terminal.string, r"\"(?:\\\"|[^\"])*\"")
]


keys = [
    ("ciao", Terminal.name),
    ("class", Terminal.name),
    ("scheme", Terminal.name),
    ("events", Terminal.name),
    ("effects", Terminal.name),
    ("conditions", Terminal.name),
    ("assertions", Terminal.name),
    ("variables", Terminal.name),
    ("states", Terminal.name),
    ("objects", Terminal.name),
    ("links", Terminal.name),
    ("else", Terminal.name),
    ("new", Terminal.name),
    ("public", Terminal.name),
    ("private", Terminal.name),
    ("[", Terminal.char_key),
    ("]", Terminal.char_key),
    ("(", Terminal.char_key),
    (")", Terminal.char_key),
    ("!", Terminal.char_key),
    ("+", Terminal.char_key),
    ("-", Terminal.char_key),
    ("*", Terminal.char_key),
    ("/", Terminal.char_key),
    ("->", Terminal.char_key),
    ("<-", Terminal.char_key),
    ("&", Terminal.char_key),
    ("|", Terminal.char_key),
    ("=", Terminal.char_key),
    (":=", Terminal.char_key),
    (":", Terminal.char_key),
    (";", Terminal.char_key),
    (",", Terminal.char_key),
    (".", Terminal.char_key),
]

keywords = [
            "class",
            "scheme",
            "events",
            "effects",
            "conditions",
            "assertions",
            "variables",
            "states",
            "objects",
            "links",
            "else",
            "public",
            "private",
]

class Nonterminal(Enum):
    CIAO_PROGRAM = "CIAO_PROGRAM"
    AUTO_CLASS = "AUTO_CLASS"
    AUTO_SCHEME = "AUTO_SCHEME"
    EVENTS = "EVENTS"
    EFFECTS = "EFFECTS"
    CONDITIONS = "CONDITIONS"
    ASSERTIONS = "ASSERTIONS"
    BOOLEXPR = "BOOLEXPR"
    ASSERT = "ASSERT"
    INTERFACE = "INTERFACE"
    DECLARATION = "DECLARATION"
    VARIABLES = "VARIABLES"
    STATES = "STATES"
    STATE = "STATE"
    TRANSITION = "TRANSITION"
    DIRECT = "DIRECT"
    CHOICE = "CHOICE"
    CALL = "CALL"
    ACTIONS = "ACTIONS"
    ASSIGN = "ASSIGN"
    OBJECTS = "OBJECTS"
    OBJECT = "OBJECT"
    INITIAL = "INITIAL"
    LINKS = "LINKS"
    LINK = "LINK"
    INTERFACES = "INTERFACES"
    EXPRESSION = "EXPRESSION"
    

axiom = Nonterminal.CIAO_PROGRAM


reserved_func = {"after": ["Integer"]}
