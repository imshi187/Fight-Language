import re

from typing import List, Tuple

"""

大类别：
    ID: 标识符
字面量：
    NUMBER: 数字(整数)
    FLOAT: 浮点数
    STRING: 字符串，可以使用"string"双引号 
    BOOLEAN: 布尔值，True 或 False
    ARRAY: 数组，[1, 2, 3]   数组在tokenizer中会被解析为很多token，
         比如 [,1,2,3,] 会被解析为[LBRACKET, NUMBER, COMMA, NUMBER, COMMA, NUMBER, RBRACKET]
    OBJECT: 对象，{name: 'Alice', age: 25}
         对象在tokenizer中会被解析为很多token，比如 {name: 'Alice', age: 25} 会被解析为[LBRACE, ID, COLON, STRING, COMMA, ID, COLON, NUMBER, RBRACE]

布尔：(完成)  在identifier_or_keyword（）中添加和判断
    True: 布尔值 True
逻辑运算(LOGIC): 完成（在identifier_or_keyword（）中添加和判断） 
    AND: 与
    OR: 或
    NOT: 非
关键字：(完成)
   LET: 声明变量
   IF: 条件判断
   ELIF: 条件判断 elif
   ELSE: 条件判断
   BREAK: 跳出循环
   LOOP: 循环
   FUNCTION:: 定义函数
   RETURN: 返回值

运算符号：(完成)
    ASSIGN: 赋值符号  =
    PLUS: 加号 + 
    MINUS: 减号 -
    MUL: 乘号 * 
    DIV: 除号 / 
    MOD: %  取余运算符
    FLOOR_DIV: //   (向下取整)
    POW: 幂运算符 ^ 
    
比较运算符(comparison)： 完成
    EQ: 等于 ==
    NEQ: 不等于 !=
    LT: 小于 <
    LE: 小于等于 <=
    GT: 大于 >
    GE: 大于等于 >=
    
括号(done)：完成
    END: 语句结束符
    LPAREN: 左括号 （
    RPAREN: 右括号 ） 
    COMMA: 逗号
    END: 语句结束符 ;，
    LBRACKET: 左方括号 [。
    RBRACKET: 右方括号 ]。
    COLON: 冒号 :，用于字典键值对
    LBRACE: 左花括号 {
    RBRACE: 右花括号 }

"""


class Tokenizer:
    def __init__(self, source_code):
        # source_code: 待解析的源代码
        self.source_code: str = source_code
        # pos: 当前位置
        self.pos: int = 0
        # current_char: 当前字符
        self.current_char: str = self.source_code[self.pos] if self.source_code else None
        """
               LET: 声明变量 let
               IF: 条件判断 if
               ELIF: 条件判断 elif
               ELSE: 条件判断 else
               BREAK: 跳出循环 break
               LOOP: 循环 loop
               FUNCTION: 定义函数 function
               RETURN: 返回值 return
               
              
        """

        self.keywords: List[str] = ["const", 'lambda', 'let', 'if', "for", "in", 'else', "elif", 'break', 'loop', "def",
                                    'function', 'return', "package", "module", "from", "import", "class", "init", "new",
                                    "fields", "methods",
                                    "this", "static", "match", "switch", "case", "default", "extends", "interface",
                                    "implements", "range", "to",
                                    "catch", "try", "finally", "as","set","struct","enum"
                                    ]
        self.logic_operators: List[str] = ['and', 'or', 'not']
        self.bool = ['True', 'False']

    def advance(self):
        # 指向下一个字符
        self.pos += 1
        if self.pos < len(self.source_code):
            # index方式获取下一个字符
            self.current_char = self.source_code[self.pos]
        else:
            self.current_char = None

    def get_boolean_token(self, result):
        if result == 'True':
            return 'True'
        if result == 'False':
            return "False"

    def logic(self, result):
        if result == 'and':
            return 'AND', result
        elif result == 'or':
            return 'OR', result
        elif result == 'not':
            return 'NOT', result

    def identifier_or_keyword(self):
        # 标识符: 字母开头，后面可以是字母、数字
        result = ''
        # 第一个字符必须是字母,该方法会一直读取当前字符，直到遇到一个不是字母或数字的字符为止
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        # 判断是否是关键字（因为关键字和标识符不能都采用字母开头，然后是字母、数字）
        if result in self.keywords:
            return 'KEYWORD', result
        # and or not
        if result in self.logic_operators:
            return self.logic(result)
        # true false
        if result in self.bool:
            return 'BOOL', self.get_boolean_token(result)
        else:
            return 'ID', result

    def number(self):
        # result = ''
        # while self.current_char is not None and self.current_char.isdigit() or self.current_char == '.':
        #     result += self.current_char
        #     self.advance()
        # if '.' in result:
        #     # 浮点数
        #     return ('NUMBER', result,"FLOAT")
        # else:
        #     # 整数
        #     return 'NUMBER', result
        result = ''
        if self.current_char == '-':
            result += self.current_char
            self.advance()
        while self.current_char is not None and (self.current_char.isdigit() or (self.current_char == '.')):
            result += self.current_char
            self.advance()
        if '.' in result:
            return 'NUMBER', result, "FLOAT"
        else:
            return 'NUMBER', result

    def get_string_token(self):
        result = ''
        self.pos += 1
        self.current_char = self.source_code[self.pos]
        while self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()
        return str(result)

    def tokenize(self):
        '''
            通过第一个字符判断是说明，然后进入具体的判断方法
            token的元素的格式为(token_type, token_value), 可以考虑设计为：
                (token_type, token_value,field)
                field指的是更大的范围，比如operator, comparison, logic, brackets等,
                实现粗粒度和细粒度的token分类
            token_type:
                    标识符: ID
                    关键字: KEYWORD
                        比如 let, if, else, break, loop, function, return
                    字面量(CONSTANT)：
                        数字: NUMBER
                        字符串: STRING
                        布尔值: BOOLEAN
                    运算符(OPERATOR)
                        算术符号: PLUS, MINUS, MUL, DIV, MOD, FLOOR_DIV, POW
                    比较运算符(COMPARISON):
                            EQ, NEQ, LT, LE, GT, GE
                    逻辑运算符(LOGIC):
                            AND, OR, NOT
                    括号(BRACKETS)：
                        ( ) [ ] { }
                    其他：
                        赋值符号: ASSIGN
            token_value: 具体的token值

        '''
        tokens: List[Tuple[str, any]] = []

        while self.current_char is not None:
            if self.current_char.isspace():
                self.advance()

            elif self.current_char.isalpha():
                tokens.append(self.identifier_or_keyword())


            elif self.current_char.isdigit():
                tokens.append(self.number())

            # --
            elif self.current_char == '-' and self.source_code[self.pos + 1] == "-":
                tokens.append(("MINUS", self.current_char))
                self.advance()
                tokens.append(("MINUS", self.current_char))
                self.advance()

            elif self.current_char == '-':
                # tokens[-1]表示上一个token，如果上一个token是赋值、加、减、乘、除、等于、不等于、小于、小于等于、大于、大于等于、左括号、逗号
                # 、语句结束符，则认为是负号，否则认为是减号

                if (len(tokens) == 0 or tokens[-1][0] in {'ASSIGN', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EQ',
                                                          'NEQ', 'LT', 'LE', 'GT', 'GE', 'LPAREN',
                                                          'COMMA', 'END', "LBRACE"}):
                    tokens.append(self.number())  # Treat as negative number


                else:
                    tokens.append(('MINUS', self.current_char))  # Treat as subtraction
                    self.advance()


            # $美元符号
            elif self.current_char == '$':
                tokens.append(('DOLLAR', self.current_char))
                self.advance()

            # # 函数调用
            elif self.current_char == '@':
                tokens.append(('FUNCTION_CALL_PREFIX', self.current_char))
                self.advance()

            # ******************字符串**********
            elif self.current_char == '"':
                tokens.append(('STRING', self.get_string_token()))

            # ***********************逻辑运算符**********************************************
            elif self.current_char == '=' and self.source_code[self.pos + 1] != '=':
                # =
                tokens.append(('ASSIGN', self.current_char))
                self.advance()
            elif self.current_char == '=' and self.source_code[self.pos + 1] == '=':
                # ==
                tokens.append(('EQ', '=='))
                self.advance()
                self.advance()
            elif self.current_char == '!' and self.source_code[self.pos + 1] == '=':
                # !=
                tokens.append(('NEQ', '!='))
                self.advance()
                self.advance()
            elif self.current_char == '<' and self.source_code[self.pos + 1] == '=':
                # <=
                tokens.append(('LE', '<='))
                self.advance()
                self.advance()
            elif self.current_char == '>' and self.source_code[self.pos + 1] == '=':
                # >=
                tokens.append(('GE', '>='))
                self.advance()
                self.advance()
            elif self.current_char == '<':
                # <
                tokens.append(('LT', '<'))
                self.advance()
            elif self.current_char == '>':
                # >
                tokens.append(('GT', '>'))
                self.advance()

            # ***************** ****算术运算符号****************************************
            elif self.current_char == '+':
                tokens.append(('PLUS', self.current_char))
                self.advance()
            # elif self.current_char == '-':
            #     tokens.append(('MINUS', self.current_char))
            #     self.advance()
            elif self.current_char == '*':
                tokens.append(('MUL', self.current_char))
                self.advance()
            elif self.current_char == '/' and self.source_code[self.pos + 1] != '/':
                tokens.append(('DIV', self.current_char))
                self.advance()
            elif self.current_char == '^':
                # 幂运算符
                tokens.append(('POW', self.current_char))
                self.advance()
            elif self.current_char == '%':
                # 取余运算符
                tokens.append(('MOD', self.current_char))
                self.advance()
            elif self.current_char == '/' and self.source_code[self.pos + 1] == '/':
                # 向下取整  比如 10//3 = 3
                tokens.append(('FLOOR_DIV', "//"))
                self.advance()
                self.advance()

            # ******************几种括号****************************************
            elif self.current_char == ';':
                tokens.append(('END', self.current_char))
                self.advance()
            elif self.current_char == ',':
                tokens.append(('COMMA', self.current_char))
                self.advance()
            elif self.current_char == ':':
                tokens.append(('COLON', self.current_char))
                self.advance()
            elif self.current_char == '(':
                tokens.append(('LPAREN', self.current_char))
                self.advance()
            elif self.current_char == ')':
                tokens.append(('RPAREN', self.current_char))
                self.advance()
            elif self.current_char == '[':
                tokens.append(('LBRACKET', self.current_char))
                self.advance()
            elif self.current_char == ']':
                tokens.append(('RBRACKET', self.current_char))
                self.advance()
            elif self.current_char == '{':
                tokens.append(('LBRACE', self.current_char))
                self.advance()
            elif self.current_char == '}':
                tokens.append(('RBRACE', self.current_char))
                self.advance()
            elif self.current_char == '.':
                tokens.append(('DOT', self.current_char))
                self.advance()
            elif self.current_char == '_':
                tokens.append(('UNDERLINE', self.current_char))
                self.advance()
            elif self.current_char == '#':
                tokens.append(('COMMENT', self.current_char))
                self.advance()
            elif self.current_char == '?':
                tokens.append(('QUESTION', self.current_char))
                self.advance()
            elif self.current_char == '&':
                tokens.append(('COMBINE', self.current_char))
                self.advance()
            else:
                raise SyntaxError(f"Unexpected character: {self.current_char}")
                # tokens.append(('Nothing', self.current_char))
                # self.advance()
        return tokens
"""
    负数的解析是相对复杂的，需要考虑多种情况，现在基本考虑完全了，但是还有一些细节需要完善，
    如果遇到不能解析符号的，需要完善解析机制
"""
# 测试tokenizer
if __name__ == '__main__':

    source_code = """
         enum Color {
                Red, Green, Blue
        };
             
    """

    tokenizer = Tokenizer(source_code)
    tokens = tokenizer.tokenize()
    for token in tokens:
        print(token)
