grammar C;

@header {
    // #include <string>
    // #include <iostream>
}

/********************* PARSER *********************/

/*********** ENTRY ***********/

// 入口规则
compilationUnit
    : translationUnit? EOF
    ;

/*********** EXPRESSIONS ***********/

// 主表达式（primary-expression）
primaryExpression
    : Identifier
    | Constant
    | StringLiteral
    | LeftParen expression RightParen
    | genericSelection
    ;

// 泛型选择（generic-selection）
genericSelection
    : Generic LeftParen assignmentExpression Comma genericAssocList RightParen
    ;

// 泛型关联列表（generic-assoc-list）
// 消除了左递归
genericAssocList
    : genericAssociation (Comma genericAssociation)* // 消除了左递归
    ;

// 泛型关联（generic-association）
genericAssociation
    : typeName Colon assignmentExpression
    | Default Colon assignmentExpression
    ;

// 后缀表达式（postfix-expression）
// 消除了左递归
postfixExpression
    : primaryExpression ( 
        LeftBracket expression RightBracket 
        | LeftParen argumentExpressionList? RightParen 
        | Dot Identifier 
        | Arrow Identifier 
        | PlusPlus 
        | MinusMinus 
      )* // 消除了左递归
    | LeftParen typeName RightParen LeftBrace initializerList RightBrace 
    | LeftParen typeName RightParen LeftBrace initializerList Comma RightBrace 
    ;

// 参数表达式列表（argument-expression-list）
// 消除了左递归
argumentExpressionList
    : assignmentExpression (Comma assignmentExpression)* // 消除了左递归
    ;

// 一元表达式（unary-expression）
unaryExpression
    : postfixExpression
    | PlusPlus unaryExpression // 右递归
    | MinusMinus unaryExpression // 右递归
    | unaryOperator castExpression
    | Sizeof unaryExpression
    | Sizeof LeftParen typeName RightParen
    | Alignof LeftParen typeName RightParen
    ;

// 一元操作符（unary-operator）
unaryOperator
    : Ampersand
    | Asterisk
    | Plus
    | Minus
    | Tilde
    | Exclamation
    ;

// 类型转换表达式（cast-expression）
castExpression
    : unaryExpression
    | LeftParen typeName RightParen castExpression // 右递归
    ;

// 乘法表达式（multiplicative-expression）
// 消除了左递归
multiplicativeExpression
    : castExpression ( 
        Asterisk castExpression 
        | Slash castExpression 
        | Percent castExpression 
      )* // 消除了左递归
    ;

// 加法表达式（additive-expression）
// 消除了左递归
additiveExpression
    : multiplicativeExpression ( 
        Plus multiplicativeExpression 
        | Minus multiplicativeExpression 
      )* // 消除了左递归
    ;

// 移位表达式（shift-expression）
// 消除了左递归
shiftExpression
    : additiveExpression ( 
        LeftShift additiveExpression 
        | RightShift additiveExpression 
      )* // 消除了左递归
    ;

// 关系表达式（relational-expression）
// 消除了左递归
relationalExpression
    : shiftExpression ( 
        LessThan shiftExpression 
        | GreaterThan shiftExpression 
        | LessThanOrEqual shiftExpression 
        | GreaterThanOrEqual shiftExpression 
      )* // 消除了左递归
    ;

// 相等表达式（equality-expression）
// 消除了左递归
equalityExpression
    : relationalExpression ( 
        EqualEqual relationalExpression 
        | NotEqual relationalExpression 
      )* // 消除了左递归
    ;

// 按位与表达式（AND-expression）
// 消除了左递归
andExpression
    : equalityExpression ( Ampersand equalityExpression )* // 消除了左递归
    ;

// 异或表达式（exclusive-OR-expression）
// 消除了左递归
exclusiveOrExpression
    : andExpression ( Caret andExpression )* // 消除了左递归
    ;

// 按位或表达式（inclusive-OR-expression）
// 消除了左递归
inclusiveOrExpression
    : exclusiveOrExpression ( VerticalBar exclusiveOrExpression )* // 消除了左递归
    ;

// 逻辑与表达式（logical-AND-expression）
// 消除了左递归
logicalAndExpression
    : inclusiveOrExpression ( AndAnd inclusiveOrExpression )* // 消除了左递归
    ;

// 逻辑或表达式（logical-OR-expression）
// 消除了左递归
logicalOrExpression
    : logicalAndExpression ( OrOr logicalAndExpression )* // 消除了左递归
    ;

// 条件表达式（conditional-expression）
conditionalExpression
    : logicalOrExpression
    | logicalOrExpression Question expression Colon conditionalExpression // 右递归
    ;

// 赋值表达式（assignment-expression）
assignmentExpression
    : conditionalExpression
    | unaryExpression assignmentOperator assignmentExpression // 右递归
    ;

// 赋值操作符（assignment-operator）
assignmentOperator
    : Assign
    | StarAssign
    | SlashAssign
    | PercentAssign
    | PlusAssign
    | MinusAssign
    | LeftShiftAssign
    | RightShiftAssign
    | AndAssign
    | XorAssign
    | OrAssign
    ;

// 表达式（expression）
// 消除了左递归
expression
    : assignmentExpression ( Comma assignmentExpression )* // 消除了左递归
    ;

// 常量表达式（constant-expression）
constantExpression
    : conditionalExpression
    ;

/*********** DECLARATIONS ***********/

// 声明（declaration）
declaration
    : declarationSpecifiers initDeclaratorList? SemiColon // 此处有二义性 e.g. int a; 或许可以ban掉 int; 这种写法
    | staticAssertDeclaration
    ;

// 声明说明符（declaration-specifiers）
declarationSpecifiers
    :
    (
        storageClassSpecifier
        | typeSpecifier
        | typeQualifier
        | functionSpecifier
        | alignmentSpecifier
    )+
    ;

// 初始化声明列表（init-declarator-list）
// 消除了左递归
initDeclaratorList
    : initDeclarator ( Comma initDeclarator )* // 消除了左递归
    ;

// 初始化声明符（init-declarator）
initDeclarator
    : declarator
    | declarator Assign initializer
    ;

// 存储类说明符（storage-class-specifier）
storageClassSpecifier
    : Typedef
    | Extern
    | Static
    | ThreadLocal
    | Auto
    | Register
    ;

// 类型说明符（type-specifier）
typeSpecifier
    : Void
    | Char
    | Short
    | Int
    | Long
    | Float
    | Double
    | Signed
    | Unsigned
    | Bool
    | Complex
    | atomicTypeSpecifier
    | structOrUnionSpecifier
    | enumSpecifier
    | typedefName
    ;

// 结构或联合说明符（struct-or-union-specifier）
structOrUnionSpecifier
    : structOrUnion Identifier? LeftBrace structDeclarationList RightBrace
    | structOrUnion Identifier
    ;

// 结构或联合（struct-or-union）
structOrUnion
    : Struct
    | Union
    ;

// 结构声明列表（struct-declaration-list）
// 消除了左递归
structDeclarationList
    : structDeclaration+ // 消除了左递归
    ;

// 结构声明（struct-declaration）
structDeclaration
    : specifierQualifierList structDeclaratorList? SemiColon
    | staticAssertDeclaration
    ;

// 说明符限定符列表（specifier-qualifier-list）
specifierQualifierList
    : typeSpecifier specifierQualifierList?
    | typeQualifier specifierQualifierList?
    ;

// 结构声明符列表（struct-declarator-list）
// 消除了左递归
structDeclaratorList
    : structDeclarator ( Comma structDeclarator )* // 消除了左递归
    ;

// 结构声明符（struct-declarator）
structDeclarator
    : declarator
    | declarator? Colon constantExpression
    ;

// 枚举说明符（enum-specifier）
enumSpecifier
    : Enum Identifier? LeftBrace enumeratorList RightBrace
    | Enum Identifier? LeftBrace enumeratorList Comma RightBrace
    | Enum Identifier
    ;

// 枚举器列表（enumerator-list）
// 消除了左递归
enumeratorList
    : enumerator ( Comma enumerator )* // 消除了左递归
    ;

// 枚举器（enumerator）
enumerator
    : EnumerationConstant
    | EnumerationConstant Assign constantExpression
    ;

// 原子类型说明符（atomic-type-specifier）
atomicTypeSpecifier
    : Atomic LeftParen typeName RightParen
    ;

// 类型限定符（type-qualifier）
typeQualifier
    : Const
    | Restrict
    | Volatile
    | Atomic
    ;

// 函数说明符（function-specifier）
functionSpecifier
    : Inline
    | Noreturn
    ;

// 对齐说明符（alignment-specifier）
alignmentSpecifier
    : Alignas LeftParen typeName RightParen
    | Alignas LeftParen constantExpression RightParen
    ;

// 声明符（declarator）
declarator
    : pointer? directDeclarator
    ;

// 直接声明符（direct-declarator）
// 消除了左递归
directDeclarator
    : directDeclaratorBase directDeclaratorSuffix*
    ;

// 直接声明符基础（direct-declarator-base）
directDeclaratorBase
    : Identifier
    | LeftParen declarator RightParen
    ;

// 直接声明符后缀（direct-declarator-suffix）
directDeclaratorSuffix
    : LeftBracket typeQualifierList? assignmentExpression? RightBracket
    | LeftBracket Static typeQualifierList? assignmentExpression RightBracket
    | LeftBracket typeQualifierList Static assignmentExpression RightBracket
    | LeftBracket typeQualifierList? Asterisk RightBracket
    | LeftParen parameterTypeList RightParen
    | LeftParen identifierList? RightParen
    ;

// 指针（pointer）
pointer
    : Asterisk typeQualifierList?
    | Asterisk typeQualifierList? pointer // 右递归
    ;

// 类型限定符列表（type-qualifier-list）
// 消除了左递归
typeQualifierList
    : typeQualifier+ // 消除了左递归
    ;

// 参数类型列表（parameter-type-list）
parameterTypeList
    : parameterList
    | parameterList Comma Ellipsis
    ;

// 参数列表（parameter-list）
// 消除了左递归
parameterList
    : parameterDeclaration ( Comma parameterDeclaration )* // 消除了左递归
    ;

// 参数声明（parameter-declaration）
parameterDeclaration
    : declarationSpecifiers declarator
    | declarationSpecifiers abstractDeclarator?
    ;

// 标识符列表（identifier-list）
// 消除了左递归
identifierList
    : Identifier ( Comma Identifier )* // 消除了左递归
    ;

// 类型名称（type-name）
typeName
    : specifierQualifierList abstractDeclarator?
    ;

// 抽象声明符（abstractDeclarator）
abstractDeclarator
    : pointer
    | pointer? directAbstractDeclarator
    ;

// 直接抽象声明符（direct-abstract-declarator）
// 消除了左递归
directAbstractDeclarator
    : directAbstractDeclaratorBase directAbstractDeclaratorSuffix*
    ;

// 直接抽象声明符基础（direct-abstract-declarator-base）
directAbstractDeclaratorBase
    : LeftParen abstractDeclarator RightParen
    ;

// 直接抽象声明符后缀（direct-abstract-declarator-suffix）
directAbstractDeclaratorSuffix
    : LeftBracket typeQualifierList? assignmentExpression? RightBracket
    | LeftBracket Static typeQualifierList? assignmentExpression? RightBracket
    | LeftBracket typeQualifierList Static assignmentExpression RightBracket
    | LeftBracket Asterisk RightBracket
    | LeftParen parameterTypeList? RightParen
    ;

// 类型定义名称（typedef-name）
typedefName
    : Identifier
    ;

// 初始化器（initializer）
initializer
    : assignmentExpression
    | LeftBrace initializerList RightBrace
    | LeftBrace initializerList Comma RightBrace
    ;

// 初始化器列表（initializer-list）
// 消除了左递归
initializerList
    : designation? initializer ( Comma designation? initializer )* // 消除了左递归
    ;

// 指定符（designation）
designation
    : designatorList Assign
    ;

// 指定符列表（designator-list）
// 消除了左递归
designatorList
    : designator+ // 消除了左递归
    ;

// 指定符（designator）
designator
    : LeftBracket constantExpression RightBracket
    | Dot Identifier
    ;

// 静态断言声明（static-assert-declaration）
staticAssertDeclaration
    : StaticAssert LeftParen constantExpression Comma StringLiteral RightParen SemiColon
    ;

/*********** STATEMENTS ***********/

// 语句（statement）
statement
    : labeledStatement
    | compoundStatement
    | expressionStatement
    | selectionStatement
    | iterationStatement
    | jumpStatement
    ;

// 标号语句（labeled-statement）
labeledStatement
    : Identifier Colon statement
    | Case constantExpression Colon statement
    | Default Colon statement
    ;

// 复合语句（compound-statement）
compoundStatement
    : LeftBrace blockItemList? RightBrace
    ;

// 代码块项列表（block-item-list）
// 消除了左递归
blockItemList
    : blockItem+ // 消除了左递归
    ;

// 代码块项（block-item）
blockItem
    : declaration
    | statement
    ;

// 表达式语句（expression-statement）
expressionStatement
    : expression? SemiColon
    ;

// 选择语句（selection-statement）
selectionStatement
    : If LeftParen expression RightParen statement
    | If LeftParen expression RightParen statement Else statement
    | Switch LeftParen expression RightParen statement
    ;

// 循环语句（iteration-statement）
iterationStatement
    : While LeftParen expression RightParen statement
    | Do statement While LeftParen expression RightParen SemiColon
    | For LeftParen expression? SemiColon expression? SemiColon expression? RightParen statement
    | For LeftParen declaration expression? SemiColon expression? RightParen statement
    ;

// 跳转语句（jump-statement）
jumpStatement
    : Goto Identifier SemiColon
    | Continue SemiColon
    | Break SemiColon
    | Return expression? SemiColon
    ;

/*********** EXTERNAL DEFINITIONS ***********/

// 翻译单元（translation-unit）
// 消除了左递归
translationUnit
    : externalDeclaration+ // 消除了左递归
    ;

// 外部声明（external-declaration）
externalDeclaration
    : functionDefinition
    | declaration
    ;

// 函数定义（function-definition）
functionDefinition
    : declarationSpecifiers declarator declarationList? compoundStatement
    ;

// 声明列表（declaration-list）
// 消除了左递归
declarationList
    : declaration+ // 消除了左递归
    ;


/********************* LEXER *********************/

/*********** KEYWORDS ***********/

// 关键字 (keyword)
Auto: 'auto';
Break: 'break';
Case: 'case';
Char: 'char';
Const: 'const';
Continue: 'continue';
Default: 'default';
Do: 'do';
Double: 'double';
Else: 'else';
Enum: 'enum';
Extern: 'extern';
Float: 'float';
For: 'for';
Goto: 'goto';
If: 'if';
Inline: 'inline';
Int: 'int';
Long: 'long';
Register: 'register';
Restrict: 'restrict';
Return: 'return';
Short: 'short';
Signed: 'signed';
Sizeof: 'sizeof';
Static: 'static';
Struct: 'struct';
Switch: 'switch';
Typedef: 'typedef';
Union: 'union';
Unsigned: 'unsigned';
Void: 'void';
Volatile: 'volatile';
While: 'while';
Alignas: '_Alignas';
Alignof: '_Alignof';
Atomic: '_Atomic';
Bool: '_Bool';
Complex: '_Complex';
Generic: '_Generic';
Imaginary: '_Imaginary';
Noreturn: '_Noreturn';
StaticAssert: '_Static_assert';
ThreadLocal: '_Thread_local';

/*********** IDENTIFIERS ***********/

// 标识符（identifier）
// 消除了左递归
Identifier
    : IdentifierNondigit (IdentifierNondigit | Digit)* // 消除了左递归
    ;

// 标识符-非数字（identifier-nondigit）
fragment IdentifierNondigit
    : Nondigit | UniversalCharacterName
    ;

// 非数字（nondigit）
fragment Nondigit
    : [a-zA-Z_] // 小写字母、大写字母和下划线
    ;

// 数字（digit）
fragment Digit
    : [0-9] // 0到9的数字
    ;

// 通用字符名（universal-character-name）
fragment UniversalCharacterName
    : '\\u' HexQuad // 4位16进制数字
    | '\\U' HexQuad HexQuad // 8位16进制数字
    ;

// 16进制四位数（hex-quad）
fragment HexQuad
    : HexDigit HexDigit HexDigit HexDigit
    ;

// 16进制数字（hex-digit）
fragment HexDigit
    : [0-9a-fA-F] // 0到9和a-f/A-F的16进制数字
    ;

/*********** CONSTANTS ***********/

// 常量（constant）
Constant
    : IntegerConstant
    | FloatingConstant
    | EnumerationConstant
    | CharacterConstant
    ;

// 整数常量（integer-constant）
fragment IntegerConstant
    : DecimalConstant IntegerSuffix?
    | OctalConstant IntegerSuffix?
    | HexadecimalConstant IntegerSuffix?
    ;

// 十进制常量（decimal-constant）
// 消除了左递归
fragment DecimalConstant
    : NonzeroDigit Digit* // 消除了左递归
    ;

// 八进制常量（octal-constant）
// 消除了左递归
fragment OctalConstant
    : '0' OctalDigit* // 消除了左递归
    ;

// 十六进制常量（hexadecimal-constant）
// 消除了左递归
fragment HexadecimalConstant
    : HexadecimalPrefix HexadecimalDigit+ // 消除了左递归
    ;

// 十六进制前缀（hexadecimal-prefix）
fragment HexadecimalPrefix
    : '0x' | '0X'
    ;

// 非零数字（nonzero-digit）
fragment NonzeroDigit
    : [1-9]
    ;

// 八进制数字（octal-digit）
fragment OctalDigit
    : [0-7]
    ;

// 十六进制数字（hexadecimal-digit）
fragment HexadecimalDigit
    : [0-9a-fA-F]
    ;

// 整数后缀（integer-suffix）
fragment IntegerSuffix
    : UnsignedSuffix LongSuffix?
    | UnsignedSuffix LongLongSuffix
    | LongSuffix UnsignedSuffix?
    | LongLongSuffix UnsignedSuffix?
    ;

// 无符号后缀（unsigned-suffix）
fragment UnsignedSuffix
    : 'u' | 'U'
    ;

// 长整型后缀（long-suffix）
fragment LongSuffix
    : 'l' | 'L'
    ;

// 长长整型后缀（long-long-suffix）
fragment LongLongSuffix
    : 'll' | 'LL'
    ;

// 浮点常量（floating-constant）
fragment FloatingConstant
    : DecimalFloatingConstant
    | HexadecimalFloatingConstant
    ;

// 十进制浮点常量（decimal-floating-constant）
fragment DecimalFloatingConstant
    : FractionalConstant ExponentPart? FloatingSuffix?
    | DigitSequence ExponentPart FloatingSuffix?
    ;

// 十六进制浮点常量（hexadecimal-floating-constant）
fragment HexadecimalFloatingConstant
    : HexadecimalPrefix HexadecimalFractionalConstant BinaryExponentPart FloatingSuffix?
    | HexadecimalPrefix HexadecimalDigitSequence BinaryExponentPart FloatingSuffix?
    ;

// 小数部分（fractional-constant）
fragment FractionalConstant
    : DigitSequence? '.' DigitSequence
    | DigitSequence '.'
    ;

// 指数部分（exponent-part）
fragment ExponentPart
    : [eE] Sign? DigitSequence
    ;

// 符号（sign）
fragment Sign
    : '+' | '-'
    ;

// 数字序列（digit-sequence）
// 消除了左递归
fragment DigitSequence
    : Digit+
    ;

// 十六进制小数部分（hexadecimal-fractional-constant）
fragment HexadecimalFractionalConstant
    : HexadecimalDigitSequence? '.' HexadecimalDigitSequence
    | HexadecimalDigitSequence '.'
    ;

// 二进制指数部分（binary-exponent-part）
fragment BinaryExponentPart
    : [pP] Sign? DigitSequence
    ;

// 十六进制数字序列（hexadecimal-digit-sequence）
// 消除了左递归
fragment HexadecimalDigitSequence
    : HexadecimalDigit+ // 消除了左递归
    ;

// 浮点后缀（floating-suffix）
fragment FloatingSuffix
    : 'f' | 'F' | 'l' | 'L'
    ;

// 枚举常量（enumeration-constant）
EnumerationConstant
    : Identifier
    ;

// 字符常量（character-constant）
fragment CharacterConstant
    : '\'' CCharSequence '\''
    | 'L\'' CCharSequence '\''
    | 'u\'' CCharSequence '\''
    | 'U\'' CCharSequence '\''
    ;

// 字符序列（c-char-sequence）
// 消除了左递归
fragment CCharSequence
    : CChar+ // 消除了左递归
    ;

// 字符（c-char）
fragment CChar
    : ~[\\'\n\r] // 任何非反斜杠、单引号或换行符的字符
    | EscapeSequence
    ;

// 转义序列（escape-sequence）
fragment EscapeSequence
    : SimpleEscapeSequence
    | OctalEscapeSequence
    | HexadecimalEscapeSequence
    | UniversalCharacterName
    ;

// 简单转义序列（simple-escape-sequence）
fragment SimpleEscapeSequence
    : '\\' ['"\\?abfnrtv]
    ;

// 八进制转义序列（octal-escape-sequence）
fragment OctalEscapeSequence
    : '\\' OctalDigit
    | '\\' OctalDigit OctalDigit
    | '\\' OctalDigit OctalDigit OctalDigit
    ;

// 十六进制转义序列（hexadecimal-escape-sequence）
fragment HexadecimalEscapeSequence
    : '\\x' HexadecimalDigit+
    ;


/*********** STRING_LITERALS ***********/

// 字符串字面量（string-literal）
StringLiteral
    : EncodingPrefix? '"' SCharSequence? '"'
    ;

// 编码前缀（encoding-prefix）
fragment EncodingPrefix
    : 'u8' 
    | 'u'
    | 'U'
    | 'L'
    ;

// 字符序列（s-char-sequence）
// 消除了左递归
fragment SCharSequence
    : SChar+ // 消除了左递归
    ;

// 字符（s-char）
fragment SChar
    : ~[\\"\n\r] // 任何非双引号、反斜杠或换行符的字符
    | EscapeSequence
    ;


/*********** PUNCTUATORS ***********/

// 标点符号（punctuator）
LeftBracket : '[' ;
RightBracket : ']' ;
LeftParen : '(' ;
RightParen : ')' ;
LeftBrace : '{' ;
RightBrace : '}' ;
Dot : '.' ;
Arrow : '->' ;
PlusPlus : '++' ;
MinusMinus : '--' ;
Ampersand : '&' ;
Asterisk : '*' ;
Plus : '+' ;
Minus : '-' ;
Tilde : '~' ;
Exclamation : '!' ;
Slash : '/' ;
Percent : '%' ;
LeftShift : '<<' ;
RightShift : '>>' ;
LessThan : '<' ;
GreaterThan : '>' ;
LessThanOrEqual : '<=' ;
GreaterThanOrEqual : '>=' ;
EqualEqual : '==' ;
NotEqual : '!=' ;
Caret : '^' ;
VerticalBar : '|' ;
AndAnd : '&&' ;
OrOr : '||' ;
Question : '?' ;
Colon : ':' ;
SemiColon : ';' ;
Ellipsis : '...' ;
Assign : '=' ;
StarAssign : '*=' ;
SlashAssign : '/=' ;
PercentAssign : '%=' ;
PlusAssign : '+=' ;
MinusAssign : '-=' ;
LeftShiftAssign : '<<=' ;
RightShiftAssign : '>>=' ;
AndAssign : '&=' ;
XorAssign : '^=' ;
OrAssign : '|=' ;
Comma : ',' ;
Pound : '#' ;
DoublePound : '##' ;
LeftSquare : '<:' ;
RightSquare : ':>' ;
LeftCurly : '<%' ;
RightCurly : '%>' ;
PercentColon : '%:' ;
DoublePercentColon : '%:%:' ;

// 忽略的字符
MultiLineMacro
    : Pound (~[\n]*? '\\' '\r'? '\n')+ ~ [\n]+ -> channel (HIDDEN)
    ;
Directive
    : Pound ~ [\n]* -> channel (HIDDEN)
    ;
Whitespace
    : [ \t]+ -> channel(HIDDEN)
    ;
Newline
    : ('\r' '\n'? | '\n') -> channel(HIDDEN)
    ;
BlockComment
    : '/*' .*? '*/' -> channel(HIDDEN)
    ;
LineComment
    : '//' ~[\r\n]* -> channel(HIDDEN)
    ;
