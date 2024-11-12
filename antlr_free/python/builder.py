import pickle  # 用于序列化解析表

class Grammar:
    """
    文法类
    """
    def __init__(self, productions):
        self.productions = productions  # 形如 {'E': [['E', '+', 'T'], ['T']], ...}
        self.non_terminals = set(productions.keys())
        self.terminals = self.get_terminals()
        self.start_symbol = list(productions.keys())[0]
        self.augmented_start_symbol = self.start_symbol + "'"

    def get_terminals(self):
        """
        构造文法的终结符集合
        """
        terminals = set()
        for rhs_list in self.productions.values():
            for rhs in rhs_list:
                for symbol in rhs:
                    if symbol not in self.productions:
                        terminals.add(symbol)
        return terminals

    def augment_grammar(self):
        """
        处理增广文法
        """
        self.productions[self.augmented_start_symbol] = [[self.start_symbol]]
        self.non_terminals.add(self.augmented_start_symbol)

class Item:
    """
    单个项目
    """
    def __init__(self, lhs, rhs, dot_position, lookahead):
        self.lhs = lhs  # 产生式左部
        self.rhs = rhs  # 产生式右部
        self.dot_position = dot_position  # 点的位置
        self.lookahead = lookahead  # 前瞻符号集合

    def core(self):
        """
        返回项目的核心部分（不包括 lookahead）
        """
        return (self.lhs, tuple(self.rhs), self.dot_position)

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

class ItemSet:
    """
    单个项目集
    """
    def __init__(self, items):
        self.items = frozenset(items)
        self.transitions = {}

    def core(self):
        """
        返回项目集的核心（不包含 lookahead）
        """
        core_items = set()
        for item in self.items:
            core_items.add(item.core())
        return frozenset(core_items)

    def __eq__(self, other):
        return self.items == other.items

    def __hash__(self):
        return hash(self.items)

    def __repr__(self):
        items_str = '\n'.join([str(item) for item in self.items])
        return f"ItemSet:\n{items_str}"

class Automaton:
    """
    LALR(1) 自动机
    """
    def __init__(self):
        self.states: list[ItemSet] = []  # 存储所有的ItemSet
        self.state_map = {}  # 从ItemSet到状态编号的映射

    def add_state(self, item_set: ItemSet):
        if item_set not in self.state_map:
            state_id = len(self.states)
            self.states.append(item_set)
            self.state_map[item_set] = state_id
            return state_id
        else:
            return self.state_map[item_set]

    def get_state_id(self, item_set):
        return self.state_map.get(item_set)

    def __repr__(self):
        result = ''
        for idx, state in enumerate(self.states):
            result += f"State {idx}:\n{state}\n\n"
        return result

class FirstSets:
    """
    First 集
    """
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.first_sets = {symbol: set() for symbol in grammar.non_terminals}
        # 对于终结符，First集合就是其自身
        for terminal in grammar.terminals:
            self.first_sets[terminal] = {terminal}
        self.compute_first_sets()

    def compute_first_sets(self):
        """
        计算 First 集
        """
        changed = True
        while changed:
            changed = False
            for lhs in self.grammar.productions:
                for rhs in self.grammar.productions[lhs]:
                    before = len(self.first_sets[lhs])
                    if not rhs:
                        self.first_sets[lhs].add('')
                        continue
                    for symbol in rhs:
                        self.first_sets[lhs].update(self.first_sets[symbol] - {''})
                        if '' not in self.first_sets[symbol]:
                            break
                    else:
                        self.first_sets[lhs].add('')
                    if len(self.first_sets[lhs]) != before:
                        changed = True

    def compute_string_first(self, symbols):
        result = set()
        for symbol in symbols:
            result.update(self.first_sets[symbol] - {''})
            if '' not in self.first_sets[symbol]:
                break
        else:
            result.add('')
        return result

    def get(self, symbol):
        return self.first_sets.get(symbol, set())

class ActionTable:
    """
    Action 表
    """
    def __init__(self):
        self.table = {}

    def set(self, state_id, symbol, action, item):
        if state_id not in self.table:
            self.table[state_id] = {}
        self.table[state_id][symbol] = (action, item)

    def get(self, state_id, symbol):
        entry = self.table.get(state_id, {}).get(symbol)
        if entry:
            return entry[0]  # 返回动作
        else:
            return None

    def get_entry(self, state_id, symbol):
        return self.table.get(state_id, {}).get(symbol)

    def items(self):
        return self.table.items()

class GotoTable:
    """
    GOTO 表
    """
    def __init__(self):
        self.table = {}

    def set(self, state_id, symbol, next_state):
        if state_id not in self.table:
            self.table[state_id] = {}
        self.table[state_id][symbol] = next_state

    def get(self, state_id, symbol):
        return self.table.get(state_id, {}).get(symbol)

    def items(self):
        return self.table.items()
    
class ItemComparison:
    """
    定义某次 移进-归约冲突 / 归约-归约冲突 中的优先级
    """
    def __init__(self):
        # list 中每一项代表一串优先级大于关系
        self.comparison_table = [
            # const Example; 中的移进-归约冲突
            [{'lhs': 'declarationSpecifiers', 'rhs': ['typeSpecifier', '·']},
             {'lhs': 'typedefName', 'rhs': ['·', 'Identifier']}],
            # 上述情况在结构体中情形
            [{'lhs': 'specifierQualifierList', 'rhs': ['typeSpecifier', '·']},
             {'lhs': 'typedefName', 'rhs': ['·', 'Identifier']}],
            # Example (x); 中的归约-归约冲突
            [{'lhs': 'primaryExpression', 'rhs': ['Identifier', '·']},
             {'lhs': 'typedefName', 'rhs': ['Identifier', '·']}],
            # LALR(1) 疑似会引入悬挂 else 二义性
            [{'lhs': 'selectionStatement', 'rhs': ['If', 'LeftParen', 'expression', 'RightParen', 'statement', '·', 'Else', 'statement']},
             {'lhs': 'selectionStatement', 'rhs': ['If', 'LeftParen', 'expression', 'RightParen', 'statement', '·']}],
        ]

    def compare_items(self, item1: Item, item2: Item):
        """
        比较两个项目，返回：
        -1: item1 优先级高
         1: item2 优先级高
         0: 无法确定优先级
        """
        for sequence in self.comparison_table:
            for i in range(len(sequence) - 1):
                higher = sequence[i]
                lower = sequence[i + 1]
                if (self.item_matches(item1, higher) and self.item_matches(item2, lower)):
                    return -1
                if (self.item_matches(item2, higher) and self.item_matches(item1, lower)):
                    return 1
        # # 移进比归约优先
        # if (item1.dot_position == len(item1.rhs)) and (item1.dot_position < len(item1.rhs)):
        #     return 1
        # elif (item1.dot_position < len(item1.rhs)) and (item1.dot_position == len(item1.rhs)):
        #     return -1
        return 1 # XXX 改为0以检查其他冲突

    def item_matches(self, item, pattern):
        """
        检查项目是否匹配给定的模式
        """
        if item.lhs != pattern['lhs']:
            return False
        rhs_with_dot = item.rhs.copy()
        rhs_with_dot.insert(item.dot_position, '·')
        return rhs_with_dot == pattern['rhs']

def compute_lookaheads(item: Item, first_sets: FirstSets):
    beta = item.rhs[item.dot_position + 1:]
    if beta:
        first_beta = first_sets.compute_string_first(beta)
    else:
        first_beta = set()
    if '' in first_beta or not beta:
        first_beta.discard('')
        first_beta.update(item.lookahead)
    return first_beta

def closure(item_set: ItemSet, grammar: Grammar, first_sets):
    """
    计算闭包
    """
    closure_set: set[Item] = set(item_set.items)
    added = True
    while added:
        added = False
        new_items = set()
        for item in closure_set:
            if item.dot_position < len(item.rhs):
                symbol = item.rhs[item.dot_position]
                if symbol in grammar.non_terminals:
                    lookaheads = compute_lookaheads(item, first_sets)
                    for production in grammar.productions[symbol]:
                        new_item = Item(symbol, production, 0, lookaheads)
                        # 合并具有相同核心的项目的 lookahead 集合
                        for existing_item in closure_set.union(new_items):
                            if (existing_item.lhs == new_item.lhs and
                                existing_item.rhs == new_item.rhs and
                                existing_item.dot_position == new_item.dot_position):
                                if not new_item.lookahead.issubset(existing_item.lookahead):
                                    existing_item.lookahead.update(new_item.lookahead)
                                    added = True
                                break
                        else:
                            new_items.add(new_item)
                            added = True
        closure_set.update(new_items)
    return ItemSet(closure_set)

def goto(item_set: ItemSet, symbol, grammar: Grammar, first_sets):
    """
    计算 GOTO 集合
    """
    goto_items = set()
    for item in item_set.items:
        if item.dot_position < len(item.rhs) and item.rhs[item.dot_position] == symbol:
            new_item = Item(item.lhs, item.rhs, item.dot_position + 1, item.lookahead.copy())
            goto_items.add(new_item)
    if goto_items:
        return closure(ItemSet(goto_items), grammar, first_sets)
    else:
        return None

def items(grammar: Grammar):
    """
    计算项目集规范族
    """
    automaton = Automaton()
    first_sets = FirstSets(grammar)

    start_item = Item(grammar.augmented_start_symbol, [grammar.start_symbol], 0, {'EOF'})
    start_state = closure(ItemSet({start_item}), grammar, first_sets)
    automaton.add_state(start_state)

    added = True
    while added:
        added = False
        for state in automaton.states:
            for symbol in grammar.terminals.union(grammar.non_terminals):
                target_state = goto(state, symbol, grammar, first_sets)
                if target_state:
                    existing_state_id = automaton.get_state_id(target_state)
                    # if len(target_state.items) == 1:
                    #     for item in target_state.items:
                    #         target_item = item
                    #     if target_item.lhs == 'primaryExpression' and target_item.rhs == ['Identifier'] and target_item.dot_position == 1:
                    #         print(target_state.items)
                    #         print(automaton.get_state_id(target_state))
                    if existing_state_id is None:
                        # 检查是否有相同核心的状态
                        for existing_state in automaton.states:
                            if existing_state.core() == target_state.core():
                                # print(1)
                                # 合并 lookahead 集合
                                for target_item in target_state.items:
                                    for existing_item in existing_state.items:
                                        if (existing_item.lhs == target_item.lhs and
                                            existing_item.rhs == target_item.rhs and
                                            existing_item.dot_position == target_item.dot_position):
                                            # if target_item.lhs == 'primaryExpression' and target_item.rhs == ['Identifier'] and target_item.dot_position == 1:
                                            #     # print(target_item.lookahead)
                                            #     # print(existing_item.lookahead)
                                            #     print(target_state)
                                            #     print(existing_state)
                                            #     print(automaton.get_state_id(target_state))
                                            if not target_item.lookahead.issubset(existing_item.lookahead):
                                                existing_item.lookahead.update(target_item.lookahead)
                                                added = True # 如果有新 lookhead 符号, 也要重新扫描
                                            # if target_item.lhs == 'primaryExpression' and target_item.rhs == ['Identifier'] and target_item.dot_position == 1:
                                            #     print(target_item.lookahead)
                                            #     print(existing_item.lookahead)
                                            #     print("\n")
                                existing_state_id = automaton.get_state_id(existing_state)
                                break
                        if existing_state_id is None: # 没有同芯状态
                            existing_state_id = automaton.add_state(target_state)
                            added = True
                    state.transitions[symbol] = existing_state_id
    return automaton, first_sets

def construct_parsing_table(automaton: Automaton, grammar: Grammar, item_comparison: ItemComparison):
    """
    构建 Action 表和 Goto 表，并处理冲突
    """
    action_table = ActionTable()
    goto_table = GotoTable()

    for state_id, state in enumerate(automaton.states):
        for item in state.items:
            if item.dot_position < len(item.rhs):
                symbol = item.rhs[item.dot_position]
                if symbol in grammar.terminals:
                    next_state_id = state.transitions.get(symbol)
                    if next_state_id is not None:
                        existing_entry = action_table.get_entry(state_id, symbol)
                        new_action = ('shift', next_state_id)
                        if existing_entry:
                            existing_action, existing_item = existing_entry
                            priority = item_comparison.compare_items(existing_item, item)
                            if priority == -1:
                                # 保留已有的动作
                                pass
                            elif priority == 1:
                                # 用新的动作替换
                                action_table.set(state_id, symbol, new_action, item)
                            else:
                                raise Exception(f"在状态 {state_id} 和符号 {symbol} 处发生无法解决的冲突")
                        else:
                            action_table.set(state_id, symbol, new_action, item)
            else:
                if item.lhs == grammar.augmented_start_symbol:
                    action_table.set(state_id, 'EOF', ('accept',), item)
                else:
                    for lookahead in item.lookahead:
                        existing_entry = action_table.get_entry(state_id, lookahead)
                        new_action = ('reduce', (item.lhs, item.rhs))
                        if existing_entry:
                            existing_action, existing_item = existing_entry
                            priority = item_comparison.compare_items(existing_item, item)
                            if priority == -1:
                                pass
                            elif priority == 1:
                                action_table.set(state_id, lookahead, new_action, item)
                            else:
                                raise Exception(f"在状态 {state_id} 和符号 {lookahead} 处发生无法解决的冲突")
                        else:
                            action_table.set(state_id, lookahead, new_action, item)
        for symbol in grammar.non_terminals:
            next_state_id = state.transitions.get(symbol)
            if next_state_id is not None:
                goto_table.set(state_id, symbol, next_state_id)
    return action_table, goto_table

def build_parsing_tables(grammar_rules):
    grammar = Grammar(grammar_rules)
    grammar.augment_grammar()
    automaton, first_sets = items(grammar)
    item_comparison = ItemComparison()
    action_table, goto_table = construct_parsing_table(automaton, grammar, item_comparison)

    # 将解析表保存到文件
    with open('action_table.pkl', 'wb') as f:
        pickle.dump(action_table, f)

    with open('goto_table.pkl', 'wb') as f:
        pickle.dump(goto_table, f)

    with open('automaton.pkl', 'wb') as f:
        pickle.dump(automaton, f)

    print("解析表已生成并保存到 'action_table.pkl' 和 'goto_table.pkl' 文件中。")

if __name__ == "__main__":
    grammar_rules = {
        'compilationUnit': [
            ['translationUnit', 'EOF'],
            ['EOF']
        ],
        'translationUnit': [
            ['externalDeclaration'],
            ['translationUnit', 'externalDeclaration']
        ],
        'externalDeclaration': [
            ['functionDefinition'],
            ['declaration']
        ],
        'functionDefinition': [
            ['declarationSpecifiers', 'declarator', 'declarationList', 'compoundStatement'],
            ['declarationSpecifiers', 'declarator', 'compoundStatement']
        ],
        'declarationList': [
            ['declaration'],
            ['declarationList', 'declaration']
        ],
        'primaryExpression': [
            ['Identifier'],
            ['Constant'],
            ['StringLiteral'],
            ['LeftParen', 'expression', 'RightParen'],
            ['genericSelection']
        ],
        'genericSelection': [
            ['Generic', 'LeftParen', 'assignmentExpression', 'Comma', 'genericAssocList', 'RightParen']
        ],
        'genericAssocList': [
            ['genericAssociation'],
            ['genericAssocList', 'Comma', 'genericAssociation']
        ],
        'genericAssociation': [
            ['typeName', 'Colon', 'assignmentExpression'],
            ['Default', 'Colon', 'assignmentExpression']
        ],
        'postfixExpression': [
            ['primaryExpression'],
            ['postfixExpression', 'LeftBracket', 'expression', 'RightBracket'],
            ['postfixExpression', 'LeftParen', 'argumentExpressionList', 'RightParen'],
            ['postfixExpression', 'LeftParen', 'RightParen'],
            ['postfixExpression', 'Dot', 'Identifier'],
            ['postfixExpression', 'Arrow', 'Identifier'],
            ['postfixExpression', 'PlusPlus'],
            ['postfixExpression', 'MinusMinus'],
            ['LeftParen', 'typeName', 'RightParen', 'LeftBrace', 'initializerList', 'RightBrace'],
            ['LeftParen', 'typeName', 'RightParen', 'LeftBrace', 'initializerList', 'Comma', 'RightBrace']
        ],
        'argumentExpressionList': [
            ['assignmentExpression'],
            ['argumentExpressionList', 'Comma', 'assignmentExpression']
        ],
        'unaryExpression': [
            ['postfixExpression'],
            ['PlusPlus', 'unaryExpression'],
            ['MinusMinus', 'unaryExpression'],
            ['unaryOperator', 'castExpression'],
            ['Sizeof', 'unaryExpression'],
            ['Sizeof', 'LeftParen', 'typeName', 'RightParen'],
            ['Alignof', 'LeftParen', 'typeName', 'RightParen']
        ],
        'unaryOperator': [
            ['Ampersand'],
            ['Asterisk'],
            ['Plus'],
            ['Minus'],
            ['Tilde'],
            ['Exclamation']
        ],
        'castExpression': [
            ['unaryExpression'],
            ['LeftParen', 'typeName', 'RightParen', 'castExpression']
        ],
        'multiplicativeExpression': [
            ['castExpression'],
            ['multiplicativeExpression', 'Asterisk', 'castExpression'],
            ['multiplicativeExpression', 'Slash', 'castExpression'],
            ['multiplicativeExpression', 'Percent', 'castExpression']
        ],
        'additiveExpression': [
            ['multiplicativeExpression'],
            ['additiveExpression', 'Plus', 'multiplicativeExpression'],
            ['additiveExpression', 'Minus', 'multiplicativeExpression']
        ],
        'shiftExpression': [
            ['additiveExpression'],
            ['shiftExpression', 'LeftShift', 'additiveExpression'],
            ['shiftExpression', 'RightShift', 'additiveExpression']
        ],
        'relationalExpression': [
            ['shiftExpression'],
            ['relationalExpression', 'LessThan', 'shiftExpression'],
            ['relationalExpression', 'GreaterThan', 'shiftExpression'],
            ['relationalExpression', 'LessThanOrEqual', 'shiftExpression'],
            ['relationalExpression', 'GreaterThanOrEqual', 'shiftExpression']
        ],
        'equalityExpression': [
            ['relationalExpression'],
            ['equalityExpression', 'EqualEqual', 'relationalExpression'],
            ['equalityExpression', 'NotEqual', 'relationalExpression']
        ],
        'andExpression': [
            ['equalityExpression'],
            ['andExpression', 'Ampersand', 'equalityExpression']
        ],
        'exclusiveOrExpression': [
            ['andExpression'],
            ['exclusiveOrExpression', 'Caret', 'andExpression']
        ],
        'inclusiveOrExpression': [
            ['exclusiveOrExpression'],
            ['inclusiveOrExpression', 'VerticalBar', 'exclusiveOrExpression']
        ],
        'logicalAndExpression': [
            ['inclusiveOrExpression'],
            ['logicalAndExpression', 'AndAnd', 'inclusiveOrExpression']
        ],
        'logicalOrExpression': [
            ['logicalAndExpression'],
            ['logicalOrExpression', 'OrOr', 'logicalAndExpression']
        ],
        'conditionalExpression': [
            ['logicalOrExpression'],
            ['logicalOrExpression', 'Question', 'expression', 'Colon', 'conditionalExpression']
        ],
        'assignmentExpression': [
            ['conditionalExpression'],
            ['unaryExpression', 'assignmentOperator', 'assignmentExpression']
        ],
        'assignmentOperator': [
            ['Assign'],
            ['StarAssign'],
            ['SlashAssign'],
            ['PercentAssign'],
            ['PlusAssign'],
            ['MinusAssign'],
            ['LeftShiftAssign'],
            ['RightShiftAssign'],
            ['AndAssign'],
            ['XorAssign'],
            ['OrAssign']
        ],
        'expression': [
            ['assignmentExpression'],
            ['expression', 'Comma', 'assignmentExpression']
        ],
        'constantExpression': [
            ['conditionalExpression']
        ],
        'declaration': [
            ['declarationSpecifiers', 'initDeclaratorList', 'SemiColon'],
            ['declarationSpecifiers', 'SemiColon'],
            ['staticAssertDeclaration']
        ],
        'declarationSpecifiers': [
            ['storageClassSpecifier'],
            ['storageClassSpecifier', 'declarationSpecifiers'],
            ['typeSpecifier'],
            ['typeSpecifier', 'declarationSpecifiers'],
            ['typeQualifier'],
            ['typeQualifier', 'declarationSpecifiers'],
            ['functionSpecifier'],
            ['functionSpecifier', 'declarationSpecifiers'],
            ['alignmentSpecifier'],
            ['alignmentSpecifier', 'declarationSpecifiers']
        ],
        'initDeclaratorList': [
            ['initDeclarator'],
            ['initDeclaratorList', 'Comma', 'initDeclarator']
        ],
        'initDeclarator': [
            ['declarator'],
            ['declarator', 'Assign', 'initializer']
        ],
        'storageClassSpecifier': [
            ['Typedef'],
            ['Extern'],
            ['Static'],
            ['ThreadLocal'],
            ['Auto'],
            ['Register']
        ],
        'typeSpecifier': [
            ['Void'],
            ['Char'],
            ['Short'],
            ['Int'],
            ['Long'],
            ['Float'],
            ['Double'],
            ['Signed'],
            ['Unsigned'],
            ['Bool'],
            ['Complex'],
            ['atomicTypeSpecifier'],
            ['structOrUnionSpecifier'],
            ['enumSpecifier'],
            ['typedefName']
        ],
        'structOrUnionSpecifier': [
            ['structOrUnion', 'Identifier', 'LeftBrace', 'structDeclarationList', 'RightBrace'],
            ['structOrUnion', 'LeftBrace', 'structDeclarationList', 'RightBrace'],
            ['structOrUnion', 'Identifier']
        ],
        'structOrUnion': [
            ['Struct'],
            ['Union']
        ],
        'structDeclarationList': [
            ['structDeclaration'],
            ['structDeclarationList', 'structDeclaration']
        ],
        'structDeclaration': [
            ['specifierQualifierList', 'structDeclaratorList', 'SemiColon'],
            ['specifierQualifierList', 'SemiColon'],
            ['staticAssertDeclaration']
        ],
        'specifierQualifierList': [
            ['typeSpecifier'],
            ['typeSpecifier', 'specifierQualifierList'],
            ['typeQualifier'],
            ['typeQualifier', 'specifierQualifierList']
        ],
        'structDeclaratorList': [
            ['structDeclarator'],
            ['structDeclaratorList', 'Comma', 'structDeclarator']
        ],
        'structDeclarator': [
            ['declarator'],
            ['declarator', 'Colon', 'constantExpression'],
            ['Colon', 'constantExpression']
        ],
        'enumSpecifier': [
            ['Enum', 'Identifier', 'LeftBrace', 'enumeratorList', 'RightBrace'],
            ['Enum', 'Identifier', 'LeftBrace', 'enumeratorList', 'Comma', 'RightBrace'],
            ['Enum', 'LeftBrace', 'enumeratorList', 'RightBrace'],
            ['Enum', 'LeftBrace', 'enumeratorList', 'Comma', 'RightBrace'],
            ['Enum', 'Identifier']
        ],
        'enumeratorList': [
            ['enumerator'],
            ['enumeratorList', 'Comma', 'enumerator']
        ],
        'enumerator': [
            ['Identifier'],
            ['Identifier', 'Assign', 'constantExpression'] # EnumerationConstant 改成 Identifier
        ],
        'atomicTypeSpecifier': [
            ['Atomic', 'LeftParen', 'typeName', 'RightParen']
        ],
        'typeQualifier': [
            ['Const'],
            ['Restrict'],
            ['Volatile'],
            ['Atomic']
        ],
        'functionSpecifier': [
            ['Inline'],
            ['Noreturn']
        ],
        'alignmentSpecifier': [
            ['Alignas', 'LeftParen', 'typeName', 'RightParen'],
            ['Alignas', 'LeftParen', 'constantExpression', 'RightParen']
        ],
        'declarator': [
            ['pointer', 'directDeclarator'],
            ['directDeclarator']
        ],
        'directDeclarator': [
            ['Identifier'],
            ['LeftParen', 'declarator', 'RightParen'],
            ['directDeclarator', 'LeftBracket', 'typeQualifierList', 'assignmentExpression', 'RightBracket'],
            ['directDeclarator', 'LeftBracket', 'typeQualifierList', 'RightBracket'],
            ['directDeclarator', 'LeftBracket', 'assignmentExpression', 'RightBracket'],
            ['directDeclarator', 'LeftBracket', 'RightBracket'],
            ['directDeclarator', 'LeftBracket', 'Static', 'typeQualifierList', 'assignmentExpression', 'RightBracket'],
            ['directDeclarator', 'LeftBracket', 'Static', 'assignmentExpression', 'RightBracket'],
            ['directDeclarator', 'LeftBracket', 'typeQualifierList', 'Static', 'assignmentExpression', 'RightBracket'],
            ['directDeclarator', 'LeftBracket', 'typeQualifierList', 'Asterisk', 'RightBracket'],
            ['directDeclarator', 'LeftBracket', 'Asterisk', 'RightBracket'],
            ['directDeclarator', 'LeftParen', 'parameterTypeList', 'RightParen'],
            ['directDeclarator', 'LeftParen', 'identifierList', 'RightParen'],
            ['directDeclarator', 'LeftParen', 'RightParen']
        ],
        'pointer': [
            ['Asterisk', 'typeQualifierList'],
            ['Asterisk', 'typeQualifierList', 'pointer'],
            ['Asterisk', 'pointer'],
            ['Asterisk'],
        ],
        'typeQualifierList': [
            ['typeQualifier'],
            ['typeQualifierList', 'typeQualifier']
        ],
        'parameterTypeList': [
            ['parameterList'],
            ['parameterList', 'Comma', 'Ellipsis']
        ],
        'parameterList': [
            ['parameterDeclaration'],
            ['parameterList', 'Comma', 'parameterDeclaration']
        ],
        'parameterDeclaration': [
            ['declarationSpecifiers', 'declarator'],
            ['declarationSpecifiers', 'abstractDeclarator'],
            ['declarationSpecifiers']
        ],
        'identifierList': [
            ['Identifier'],
            ['identifierList', 'Comma', 'Identifier']
        ],
        'typeName': [
            ['specifierQualifierList', 'abstractDeclarator'],
            ['specifierQualifierList']
        ],
        'abstractDeclarator': [
            ['pointer'],
            ['pointer', 'directAbstractDeclarator'],
            ['directAbstractDeclarator']
        ],
        'directAbstractDeclarator': [
            ['LeftParen', 'abstractDeclarator', 'RightParen'],
            ['directAbstractDeclarator', 'LeftBracket', 'typeQualifierList', 'assignmentExpression', 'RightBracket'],
            ['directAbstractDeclarator', 'LeftBracket', 'typeQualifierList', 'RightBracket'],
            ['directAbstractDeclarator', 'LeftBracket', 'assignmentExpression', 'RightBracket'],
            ['LeftBracket', 'typeQualifierList', 'assignmentExpression', 'RightBracket'],
            ['directAbstractDeclarator', 'LeftBracket', 'RightBracket'],
            ['LeftBracket', 'typeQualifierList', 'RightBracket'],
            ['LeftBracket', 'assignmentExpression', 'RightBracket'],
            ['LeftBracket', 'RightBracket'],

            ['directAbstractDeclarator', 'LeftBracket', 'Static', 'typeQualifierList', 'assignmentExpression', 'RightBracket'],
            ['directAbstractDeclarator', 'LeftBracket', 'Static', 'assignmentExpression', 'RightBracket'],
            ['LeftBracket', 'Static', 'typeQualifierList', 'assignmentExpression', 'RightBracket'],
            ['LeftBracket', 'Static', 'assignmentExpression', 'RightBracket'],

            ['directAbstractDeclarator', 'LeftBracket', 'typeQualifierList', 'Static', 'assignmentExpression', 'RightBracket'],
            ['LeftBracket', 'typeQualifierList', 'Static', 'assignmentExpression', 'RightBracket'],

            ['directAbstractDeclarator', 'LeftBracket', 'Asterisk', 'RightBracket'],
            ['LeftBracket', 'Asterisk', 'RightBracket'],

            ['directAbstractDeclarator', 'LeftParen', 'parameterTypeList', 'RightParen'],
            ['directAbstractDeclarator', 'LeftParen', 'RightParen'],
            ['LeftParen', 'parameterTypeList', 'RightParen'],
            ['LeftParen', 'RightParen'],
        ],
        'typedefName': [
            ['Identifier']
        ],
        'initializer': [
            ['assignmentExpression'],
            ['LeftBrace', 'initializerList', 'RightBrace'],
            ['LeftBrace', 'initializerList', 'Comma', 'RightBrace']
        ],
        'initializerList': [
            ['designation', 'initializer'],
            ['initializer'],
            ['initializerList', 'Comma', 'designation', 'initializer'],
            ['initializerList', 'Comma', 'initializer']
        ],
        'designation': [
            ['designatorList', 'Assign']
        ],
        'designatorList': [
            ['designator'],
            ['designatorList', 'designator']
        ],
        'designator': [
            ['LeftBracket', 'constantExpression', 'RightBracket'],
            ['Dot', 'Identifier']
        ],
        'staticAssertDeclaration': [
            ['StaticAssert', 'LeftParen', 'constantExpression', 'Comma', 'StringLiteral', 'RightParen', 'SemiColon']
        ],
        'statement': [
            ['labeledStatement'],
            ['compoundStatement'],
            ['expressionStatement'],
            ['selectionStatement'],
            ['iterationStatement'],
            ['jumpStatement']
        ],
        'labeledStatement': [
            ['Identifier', 'Colon', 'statement'],
            ['Case', 'constantExpression', 'Colon', 'statement'],
            ['Default', 'Colon', 'statement']
        ],
        'compoundStatement': [
            ['LeftBrace', 'blockItemList', 'RightBrace'],
            ['LeftBrace', 'RightBrace']
        ],
        'blockItemList': [
            ['blockItem'],
            ['blockItemList', 'blockItem']
        ],
        'blockItem': [
            ['declaration'],
            ['statement']
        ],
        'expressionStatement': [
            ['expression', 'SemiColon'],
            ['SemiColon']
        ],
        'selectionStatement': [
            ['If', 'LeftParen', 'expression', 'RightParen', 'statement'],
            ['If', 'LeftParen', 'expression', 'RightParen', 'statement', 'Else', 'statement'],
            ['Switch', 'LeftParen', 'expression', 'RightParen', 'statement']
        ],
        'iterationStatement': [
            ['While', 'LeftParen', 'expression', 'RightParen', 'statement'],
            ['Do', 'statement', 'While', 'LeftParen', 'expression', 'RightParen', 'SemiColon'],
            ['For', 'LeftParen', 'expression', 'SemiColon', 'expression', 'SemiColon', 'expression', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'expression', 'SemiColon', 'expression', 'SemiColon', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'expression', 'SemiColon', 'SemiColon', 'expression', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'SemiColon', 'expression', 'SemiColon', 'expression', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'expression', 'SemiColon', 'SemiColon', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'SemiColon', 'expression', 'SemiColon', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'SemiColon', 'SemiColon', 'expression', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'SemiColon', 'SemiColon', 'RightParen', 'statement'],

            ['For', 'LeftParen', 'declaration', 'expression', 'SemiColon', 'expression', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'declaration', 'expression', 'SemiColon', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'declaration', 'SemiColon', 'expression', 'RightParen', 'statement'],
            ['For', 'LeftParen', 'declaration', 'SemiColon', 'RightParen', 'statement']
        ],
        'jumpStatement': [
            ['Goto', 'Identifier', 'SemiColon'],
            ['Continue', 'SemiColon'],
            ['Break', 'SemiColon'],
            ['Return', 'expression', 'SemiColon'],
            ['Return', 'SemiColon']
        ]
    }

    build_parsing_tables(grammar_rules)