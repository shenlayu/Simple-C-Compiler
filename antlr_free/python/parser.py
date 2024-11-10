import re
import pickle  # 用于加载解析表
from enum import Enum

class Item:
    """
    单个项目
    """
    def __init__(self, lhs, rhs, dot_position, lookahead):
        self.lhs = lhs  # 产生式左部
        self.rhs = rhs  # 产生式右部
        self.dot_position = dot_position  # 点的位置
        self.lookahead = lookahead  # 前瞻符号

    def __eq__(self, other):
        return (self.lhs == other.lhs and self.rhs == other.rhs and
                self.dot_position == other.dot_position and
                self.lookahead == other.lookahead)

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs), self.dot_position, tuple(self.lookahead)))

    def __repr__(self):
        rhs_with_dot = self.rhs.copy()
        rhs_with_dot.insert(self.dot_position, '·')
        lookahead_str = '/'.join(self.lookahead)
        return f"{self.lhs} -> {' '.join(rhs_with_dot)}, [{lookahead_str}]"

class ActionTable:
    """
    Action 表
    """
    def __init__(self, table):
        self.table = table  # 直接传入已加载的表

    def get(self, state_id, symbol):
        entry = self.table.get(state_id, {}).get(symbol)
        if entry:
            return entry[0]  # 返回动作
        else:
            return None

class GotoTable:
    """
    GOTO 表
    """
    def __init__(self, table):
        self.table = table  # 直接传入已加载的表

    def get(self, state_id, symbol):
        return self.table.get(state_id, {}).get(symbol)

class ParserStack:
    """
    状态栈
    """
    def __init__(self):
        self.stack = [0]  # 初始状态为0

    def push(self, state):
        self.stack.append(state)

    def pop(self):
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def __len__(self):
        return len(self.stack)

class IndentType(Enum):
    ADD = 1  # 缩进一格
    KEEP = 2  # 不变
    MINUS = 3  # 退缩进一格

class NodeType(Enum):
    MIDDLE = 1  # 中间节点
    LEAF = 2  # 叶子节点
    END = 3  # 表示结束

def lr1_parse(tokens, action_table: ActionTable, goto_table: GotoTable):
    """
    LR(1) 分析
    """
    stack = ParserStack()
    index = 0
    ast_stack = []
    while True:
        state = stack.top()
        token = tokens[index] if index < len(tokens) else ('EOF', 'EOF')
        print(token)
        action = action_table.get(state, token[0])
        print(action)
        if not action:
            raise SyntaxError(f"Unexpected token {token} at position {index}")
        if action[0] == 'shift':
            stack.push(action[1])
            ast_stack.append(token)
            index += 1
        elif action[0] == 'reduce':
            lhs, rhs = action[1]
            children = []
            if rhs != []:
                for _ in rhs:
                    stack.pop()
                    children.insert(0, ast_stack.pop())
            else:
                # 处理空产生式
                pass
            state = stack.top()
            goto_state = goto_table.get(state, lhs)
            print(goto_state)
            if goto_state is None:
                raise SyntaxError(f"No transition for non-terminal {lhs} from state {state}")
            stack.push(goto_state)
            ast_stack.append((lhs, children))
        elif action[0] == 'accept':
            return ast_stack[-1]

def indent(xml_lines):
    """
    格式化 XML 行列表，添加适当的缩进。
    """
    indent_level = 0
    indent_space = "    "
    indented_lines = []

    for line, indent_type in xml_lines:
        if indent_type == IndentType.MINUS:
            indent_level = max(indent_level - 1, 0)

        indented_line = f"{indent_space * indent_level}{line}"
        indented_lines.append(indented_line)

        if indent_type == IndentType.ADD:
            indent_level += 1

    return indented_lines

def ast_to_xml(node):
    """
    将 AST 节点转换为格式化的 XML 字符串。
    """
    xml_lines = []  # 元组形式 (节点, 是否缩进)
    stack = [(node, NodeType.MIDDLE)]  # 元组形式 (节点, 节点类型)

    while stack:
        current_node, node_type = stack.pop()
        if node_type == NodeType.MIDDLE:
            lhs, children = current_node
            xml_lines.append((f"<{lhs}>", IndentType.ADD))
            stack.append((f"</{lhs}>", NodeType.END))
            for child in reversed(children):
                if isinstance(child, tuple) and len(child) == 2:
                    if isinstance(child[1], list):
                        stack.append((child, NodeType.MIDDLE))
                    else:
                        stack.append((child, NodeType.LEAF))
                else:
                    # 处理叶子节点
                    stack.append(((child[0], child[1]), NodeType.LEAF))
        elif node_type == NodeType.END:
            xml_lines.append((current_node, IndentType.MINUS))
        else:
            lhs, value = current_node
            xml_lines.append((f"<{lhs}>{value}</{lhs}>", IndentType.KEEP))

    return xml_lines

def save_ast_to_xml(ast, output_path):
    """
    将 AST 保存为格式化的 XML 文件，不使用 xml 模块。
    """
    xml_lines = ast_to_xml(ast)
    indented_xml = indent(xml_lines)
    xml_declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
    xml_content = xml_declaration + "\n".join(indented_xml)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(xml_content)

def generate_ast(file_path, action_table, goto_table):
    tokens = parse_file(file_path)
    ast = lr1_parse(tokens, action_table, goto_table)
    return ast

# 定义 TOKEN_TYPES 列表，按照匹配优先级从高到低排序
TOKEN_TYPES = [
    # 忽略的字符（空白和注释）
    ('Whitespace', r'[ \t\r\n]+'),  # 空白字符
    ('BlockComment', r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'),  # 块注释
    ('LineComment', r'//.*'),  # 行注释
    # 预处理指令（可根据需要调整）
    ('Directive', r'\#[^\n]*'),  # 预处理指令

    # 标点符号（按长度排序，以避免歧义）
    ('Ellipsis', r'\.\.\.'),
    ('DoublePercentColon', r'%:%:'),
    ('DoublePound', r'\#\#'),
    ('LeftShiftAssign', r'<<='),
    ('RightShiftAssign', r'>>='),
    ('LeftShift', r'<<'),
    ('RightShift', r'>>'),
    ('LessThanOrEqual', r'<='),
    ('GreaterThanOrEqual', r'>='),
    ('EqualEqual', r'=='),
    ('NotEqual', r'!='),
    ('AndAnd', r'&&'),
    ('OrOr', r'\|\|'),
    ('PlusPlus', r'\+\+'),
    ('MinusMinus', r'--'),
    ('PlusAssign', r'\+='),
    ('MinusAssign', r'-='),
    ('StarAssign', r'\*='),
    ('SlashAssign', r'/='),
    ('PercentAssign', r'%='),
    ('AndAssign', r'&='),
    ('OrAssign', r'\|='),
    ('XorAssign', r'\^='),
    ('Arrow', r'->'),
    ('Assign', r'='),
    ('LessThan', r'<'),
    ('GreaterThan', r'>'),
    ('Plus', r'\+'),
    ('Minus', r'-'),
    ('Asterisk', r'\*'),
    ('Slash', r'/'),
    ('Percent', r'%'),
    ('Ampersand', r'&'),
    ('Caret', r'\^'),
    ('VerticalBar', r'\|'),
    ('Tilde', r'~'),
    ('Exclamation', r'!'),
    ('Question', r'\?'),
    ('Colon', r':'),
    ('SemiColon', r';'),
    ('Comma', r','),
    ('Dot', r'\.'),
    ('LeftParen', r'\('),
    ('RightParen', r'\)'),
    ('LeftBracket', r'\['),
    ('RightBracket', r'\]'),
    ('LeftBrace', r'\{'),
    ('RightBrace', r'\}'),
    ('Pound', r'\#'),
    ('LeftSquare', r'<:'),
    ('RightSquare', r':>'),
    ('LeftCurly', r'<%'),
    ('RightCurly', r'%>'),
    ('PercentColon', r'%:'),

    # 关键字（在标识符之前匹配）
    ('Auto', r'\bauto\b'),
    ('Break', r'\bbreak\b'),
    ('Case', r'\bcase\b'),
    ('Char', r'\bchar\b'),
    ('Const', r'\bconst\b'),
    ('Continue', r'\bcontinue\b'),
    ('Default', r'\bdefault\b'),
    ('Do', r'\bdo\b'),
    ('Double', r'\bdouble\b'),
    ('Else', r'\belse\b'),
    ('Enum', r'\benum\b'),
    ('Extern', r'\bextern\b'),
    ('Float', r'\bfloat\b'),
    ('For', r'\bfor\b'),
    ('Goto', r'\bgoto\b'),
    ('If', r'\bif\b'),
    ('Inline', r'\binline\b'),
    ('Int', r'\bint\b'),
    ('Long', r'\blong\b'),
    ('Register', r'\bregister\b'),
    ('Restrict', r'\brestrict\b'),
    ('Return', r'\breturn\b'),
    ('Short', r'\bshort\b'),
    ('Signed', r'\bsigned\b'),
    ('Sizeof', r'\bsizeof\b'),
    ('Static', r'\bstatic\b'),
    ('Struct', r'\bstruct\b'),
    ('Switch', r'\bswitch\b'),
    ('Typedef', r'\btypedef\b'),
    ('Union', r'\bunion\b'),
    ('Unsigned', r'\bunsigned\b'),
    ('Void', r'\bvoid\b'),
    ('Volatile', r'\bvolatile\b'),
    ('While', r'\bwhile\b'),
    ('Alignas', r'\b_Alignas\b'),
    ('Alignof', r'\b_Alignof\b'),
    ('Atomic', r'\b_Atomic\b'),
    ('Bool', r'\b_Bool\b'),
    ('Complex', r'\b_Complex\b'),
    ('Generic', r'\b_Generic\b'),
    ('Imaginary', r'\b_Imaginary\b'),
    ('Noreturn', r'\b_Noreturn\b'),
    ('StaticAssert', r'\b_Static_assert\b'),
    ('ThreadLocal', r'\b_Thread_local\b'),

    # 标识符
    ('Identifier', r'[a-zA-Z_][a-zA-Z0-9_]*'),

    # 常量
    # 整数常量（包括十进制、八进制、十六进制）
    ('Constant', r'''
        # IntegerConstant
        (0[xX][0-9a-fA-F]+)([uU]|[lL]|(ll|LL)|([uU][lL])|([uU](ll|LL))|([lL][uU])|((ll|LL)[uU]))? # 十六进制
        |
        (0[0-7]*)([uU]|[lL]|(ll|LL)|([uU][lL])|([uU](ll|LL))|([lL][uU])|((ll|LL)[uU]))? # 八进制或零
        |
        ([1-9][0-9]*)([uU]|[lL]|(ll|LL)|([uU][lL])|([uU](ll|LL))|([lL][uU])|((ll|LL)[uU]))? # 十进制
        |
        # FloatingConstant
        (([0-9]*\.[0-9]+|[0-9]+\.)[eE][+-]?[0-9]+|([0-9]*\.[0-9]+|[0-9]+\.))[fFlL]?|[0-9]+[eE][+-]?[0-9]+[fFlL]?
        |
        (0[xX](([0-9a-fA-F]*\.[0-9a-fA-F]+|[0-9a-fA-F]+\.)[pP][+-]?[0-9]+|[0-9a-fA-F]+[pP][+-]?[0-9]+))[fFlL]?
        |
        # CharacterConstant
        (L|u|U)?'([^\\'\n\r]|\\(['"\\?abfnrtv]|[0-7]{1,3}|x[0-9a-fA-F]+|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}))'
        |
        # EnumerationConstant
        [a-zA-Z_][a-zA-Z0-9_]*
    '''),

    ('StringLiteral', r'''
        (u8|u|U|L)?\"([^\\\"\n\r]|\\(['"\\?abfnrtv]|[0-7]{1,3}|x[0-9a-fA-F]+|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}))*\"
    '''),

    # 未知或无效的字符（放在最后）
    ('Invalid', r'.'),
]

class Lexer:
    def __init__(self, input_code):
        self.code = input_code
        self.tokens = []
        self.current_position = 0
        # 编译所有正则表达式
        self.compiled_token_types = [
            (token_name, re.compile(pattern, re.VERBOSE))
            for token_name, pattern in TOKEN_TYPES
        ]

    def tokenize(self):
        while self.current_position < len(self.code):
            match = None
            for token_type, pattern in self.compiled_token_types:
                match = pattern.match(self.code, self.current_position)
                if match:
                    lexeme = match.group(0)
                    # 忽略空白和注释
                    if token_type not in ['Whitespace', 'BlockComment', 'LineComment', 'Directive']:
                        if token_type == 'Invalid':
                            raise RuntimeError(f'Unexpected character: {lexeme} at position {self.current_position}')
                        self.tokens.append((token_type, lexeme))
                    self.current_position = match.end()
                    break
            if not match:
                raise RuntimeError(f'Unexpected character: {self.code[self.current_position]} at position {self.current_position}')
        return self.tokens

def parse_file(file_path):
    try:
        with open(file_path, 'r') as file:
            input_code = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

    lexer = Lexer(input_code)
    tokens = lexer.tokenize()
    token_list = [(token_type, lexeme) for token_type, lexeme in tokens]
    token_list.append(('EOF', 'EOF'))  # 结束符，根据需要保留
    return token_list

def parse():
    # 从文件中加载解析表
    with open('action_table.pkl', 'rb') as f:
        action_table_data = pickle.load(f)
    with open('goto_table.pkl', 'rb') as f:
        goto_table_data = pickle.load(f)

    action_table = ActionTable(action_table_data.table)
    goto_table = GotoTable(goto_table_data.table)

    file_path = input("Enter the file path: ")
    try:
        ast = generate_ast(file_path, action_table, goto_table)
        output_path = 'ast.xml'
        save_ast_to_xml(ast, output_path)
        print(f"抽象语法树已保存到 {output_path}")
    except Exception as e:
        print(f"解析过程中发生错误：{e}")

if __name__ == "__main__":
    parse()