import uuid

from interpreter import Node
from interpreter.ClassRelevantNodes import ClassDeclarationNode, NewObjectNode, MethodCallNode, GetMemberNode, \
    CallClassInnerMethod, ThisNode, InterfaceNode
from interpreter.Nodes import (AssignmentNode, FunctionCallNode, BinaryOpNode,
                               NumberNode, VariableNode, IfStatementNode,
                               BooleanNode, StringNode, BreakNode, ReturnNode, ListNode, ObjectNode, UnaryOpNode,
                               ListIndexNode, ObjectIndexNode, ForInNode, PackageDeclarationNode, ImportModuleNode,
                               CommentNode, IfExprNode, MatchExprNode, SwitchNode, DecontructAssignNode,
                               ListDeconstructAssignNode, ForRangeNumberNode, TryCatchFinallyNode, IncrementNode,
                               DecrementNode, SetNode, CombineNode, MultiListIndexNode, StructDeclarationNode,
                               StructAssignNode, StructAccessNode, EnumDeclarationNode, EnumAccessNode, )
from interpreter.Tokenizer import Tokenizer
from interpreter.Nodes import LoopNode, FunctionDeclarationNode

"""
goal:
    解析器（parser）的主要任务是将从词法分析器（tokenizer）得到的token序列组装起来，
    构建出一棵表示程序结构的抽象语法树（AST，Abstract Syntax Tree）。这棵语法树能
    够展示出程序的语法和结构，而不仅仅是一个线性的token序列
    
    简单来说，就是将多个token连成一个xxxNode, 用于下一步执行,
    反正就是要得到xxNode!!!!!!!!


bnf:
    program: (statement)*
    statement: assignment | function_call | expr END
    let statement: let ID ASSIGN expr END
        比如 let x = 3;
    assignment: ID ASSIGN expr END
        比如：x = 12;  
    function_call: function 名称(参数){
            // statements
    }
    expr: term ((PLUS | MINUS) term)*
    term: factor ((MUL | DIV) factor)*
    factor: NUMBER | ID | LPAREN expr RPAREN
    if_statement: if expr then statement (elif expr then statement)* (else statement)? END
    loop_statement: loop condition (break)? body END
    logical_operations: NOT expr | expr (AND | OR) expr
    data_types: boolean | array | object | NUMBER 
    
需要实现的功能：

        1. 程序和语句
            Program (program): 由多个语句组成。
            Statement (statement): 由赋值语句、函数调用、表达式或关键字语句（如 let 语句）组成。
            
        2. 赋值和声明(完成)
            Assignment (assignment): 赋值语句，如 x = 12;。
            Let Statement (let_statement): 变量声明与赋值，如 let x = 3;。
            
        3. 函数调用（完成）
            Function Call (function_call): 函数调用语句，如 function 名称(参数) { // statements }。
            
        4. 表达式和运算
            Expression (expr): 由加法和减法运算符（PLUS 和 MINUS）连接的 term 组成。
            Term (term): 由乘法和除法运算符（MUL 和 DIV）连接的 factor 组成。
            Factor (factor): 可以是数字、标识符或者括号括起来的表达式。
            
        5. 条件判断（完成）
            If Statement (if_statement): 条件判断语句，如 if ... elif ... else ...。
            
        6. 循环和控制流 （完成）
            Loop Statement (loop_statement): 循环语句。
            Break Statement (break_statement): 跳出循环语句。
            
        7. 逻辑运算
            Logical Operations: 逻辑运算符 (AND, OR, NOT)。
            
        8. 数据类型
            Boolean (boolean): 布尔值。 （完成）
            Array (array): 数组解析。(完成)
            Object (object): 对象解析 （完成）
"""


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        # self.current_class = None  # 新增：跟踪当前正在解析的类
        # self.current_object = None

    def parse(self):
        return self.program()

    # 解析程序
    def program(self):
        statements = []
        while self.pos < len(self.tokens):
            statements.append(self.statement())
        return statements

    """
        解析语句, 包括赋值语句、函数调用语句、
        该方法是解析的根本方法
        statement: assignment | function_call_expr | if_statement | loop_statement 
                | break_statement | return_statement | let_statement | function_declaration
                | expr END (比如x+1;)
    """

    def statement(self):

        # keyword: ['let', 'if', 'else', "elif", 'break', 'loop', 'function', 'return']
        if self.current_token_type() == 'ID' and self.peek_next_token_type() == 'ASSIGN':
            return self.assignment()
        # 比如add()
        elif self.current_token_type() == 'ID' and self.peek_next_token_type() == 'LPAREN':
            return self.function_call_expr()
            # 解构赋值  let {x, y} = dict对象;
        elif self.current_token_value() == "let" and self.peek_next_token_type() == "LBRACE":
            return self.destruct_assignment()
        # 列表解构赋值  let [x, y] = list对象;
        elif self.current_token_value() == "let" and self.peek_next_token_type() == "LBRACKET":
            return self.list_destruct_assignment()
        # let id = expr;
        elif self.current_token_value() == 'let' and self.peek_next_token_type() != "LBRACE":
            return self.let_statement()

        elif self.current_token_value() == 'if':
            return self.if_statement()

        elif self.current_token_value() == 'loop':
            return self.loop_statement()
        elif self.current_token_value() == 'break':
            return self.break_statement()
        # elif self.current_token_type() == 'KEYWORD' and self.current_token_value() == 'function':
        elif self.current_token_value() == 'def':
            return self.function_declaration()

        # 注解或者函数调用
        elif self.current_token_value() == '@':
            # 注解  @annotation
            if self.tokens[self.pos + 1][1] == "annotation":
                return self.annotation()
            else:
                # 函数调用
                return self.function_call_statement()


        elif self.current_token_value() == 'return':
            return self.return_statement()
        elif self.current_token_value() == "for":
            return self.for_in_statement()

        elif self.current_token_value() == 'const':
            return self.const_statement()

        # package机制解析
        elif self.current_token_value() == "package":
            return self.package_statement()

        # module 引入
        elif self.current_token_value() == "import":
            return self.import_module_statement()

        # @Util.add(1,2);  @FUNCTION_CALL_PREFIX ID Dot ID ( )
        elif self.current_token_type() == "FUNCTION_CALL_PREFIX" and self.peek_next_token_type() == "ID":
            if self.tokens[self.pos + 2][0] == "DOT" and self.tokens[self.pos + 3][0] == "ID":
                return self.module_method_call()

        # 类声明
        elif self.current_token_value() == "class":
            return self.class_declaration()

            # 解析实例调用方法的表达式 比如 p->show();
        elif self.current_token_type() == 'ID' and self.peek_next_token_type() == 'MINUS' and self.tokens[self.pos + 2][
            0] == 'GT' and self.tokens[self.pos + 3][0] == "ID" and self.tokens[self.pos + 4][0] == "LPAREN":
            return self.method_method_call()

        # 解析注释
        elif self.current_token_type() == "COMMENT":
            return self.parse_comment()

        # 调用实例内部的方法  this->xxx();
        elif self.call_class_inner_method():
            return self.evaluate_call_class_inner_method()

        # switch statement
        elif self.current_token_value() == "switch":
            return self.switch_statement()


        # 接口
        elif self.current_token_value() == "interface":
            return self.interface_statement()
        # try catch finally
        elif self.current_token_value() == "try":
            return self.try_catch_finally_statement()

        elif self.current_token_type() == "ID" and self.tokens[self.pos + 1][1] == "+" and self.tokens[self.pos + 2][
            1] == "+":
            # id++;
            print('inc')
            return self.increment_statement()
        elif self.current_token_type() == "ID" and self.tokens[self.pos + 1][1] == "-" and self.tokens[self.pos + 2][
            1] == "-":
            # id--;
            print('dec')
            return self.decrement_statement()

        elif self.current_token_value() == "struct":
            return self.struct_statement()

        # enum Color{} 这样的声明语句
        elif self.current_token_value() == "enum" and self.peek_next_token_type() == "ID":
            return self.enum_statement()



        else:
            node = self.expr()
            if self.current_token_type() == 'END':
                self.eat_current_token_type('END')
            return node

    def annotation(self):
        # 解析注解
        self.eat_current_token_type("FUNCTION_CALL_PREFIX")  # @
        self.eat_current_token_type("KEYWORD")  # annotation
        self.eat_current_token_type("LPAREN")  # (
        properties = {}
        while self.current_token_type() != "RPAREN":

            # annotation(id = 1, name = "xxx")
            property_name = self.current_token_value()
            self.eat_current_token_type("ID")
            self.eat_current_token_type("ASSIGN")  # =
            property_value = self.expr()
            if self.current_token_type() == "COMMA":
                self.eat_current_token_type("COMMA")
            # 解析注解的属性
            properties.update({property_name: property_value})
        self.eat_current_token_type("RPAREN")  # )
        fnc_dec_node:FunctionDeclarationNode = self.function_declaration()
        fnc_dec_node.annotations = properties
        return fnc_dec_node



    def enum_access_expr(self):
        # let x= enum::Color::RED;
        self.eat_current_token_type("KEYWORD")  # enum
        self.eat_current_token_type("COLON")  # :
        self.eat_current_token_type("COLON")  # :
        # 比如Color
        enum_name = self.current_token_value()
        self.eat_current_token_type("ID")
        # 解析enum的属性 ::RED
        self.eat_current_token_type("COLON")  # :
        self.eat_current_token_type("COLON")  # :
        # 比如RED
        enum_property = self.current_token_value()
        self.eat_current_token_type("ID")
        print("xxx")
        return EnumAccessNode(enum_name, enum_property)

    def enum_statement(self):
        # 解析enum
        self.eat_current_token_type("KEYWORD")  # enum
        enum_name = self.current_token_value()
        self.eat_current_token_type("ID")
        self.eat_current_token_type("LBRACE")  # {
        # 解析属性
        properties = []
        while self.current_token_type() != "RBRACE":
            property_name = self.current_token_value()
            self.eat_current_token_type("ID")
            properties.append(property_name)
            if self.current_token_type() == "COMMA":
                self.eat_current_token_type("COMMA")
        self.eat_current_token_type("RBRACE")  # }
        return EnumDeclarationNode(enum_name, properties)

    def struct_statement(self):
        """
                struct 名称 {
                    属性名1, 属性名2;
                }
                每个属性的init_value = -1


        :return:
        """
        # 解析struct
        self.eat_current_token_type("KEYWORD")  # struct
        struct_name = self.current_token_value()
        self.eat_current_token_type("ID")
        self.eat_current_token_type("LBRACE")  # {
        # 解析属性
        properties = {}
        while self.current_token_type() != "RBRACE":
            property_name = self.current_token_value()
            self.eat_current_token_type("ID")
            properties.update({property_name: -1})
            if self.current_token_type() == "COMMA":
                self.eat_current_token_type("COMMA")

        self.eat_current_token_type("RBRACE")  # }
        return StructDeclarationNode(struct_name, properties)

    def decrement_statement(self):
        # id--;
        id_name = self.current_token_value()
        self.eat_current_token_type("ID")
        self.eat_current_token_type("MINUS")
        self.eat_current_token_type("MINUS")
        self.eat_current_token_type("END")  # ;
        return DecrementNode(id_name)

    def try_catch_finally_statement(self):
        # try catch finally 机制

        self.eat_current_token_type("KEYWORD")  # try
        self.eat_current_token_type("LBRACE")  # {
        # try的代码块
        try_blocks = []
        while self.current_token_type() != "RBRACE":
            stmt = self.statement()
            try_blocks.append(stmt)
        self.eat_current_token_type("RBRACE")  # }
        print("try_blocks", try_blocks)

        # catch 和finally blocks
        catch_block = []
        while self.current_token_value() == "catch":
            self.eat_current_token_type("KEYWORD")  # catch
            self.eat_current_token_type("LPAREN")  # (

            # 解析异常类型
            catch_type = self.current_token_value()
            self.eat_current_token_type("ID")
            self.eat_current_token_type("RPAREN")  # )
            self.eat_current_token_type("LBRACE")  # {
            blocks = []
            while self.current_token_type() != "RBRACE":
                stmt_catch = self.statement()
                # catch_block.append(stmt_catch)
                blocks.append(stmt_catch)
            self.eat_current_token_type("RBRACE")  # }  catch的后大括号
            # {错误类型: block_statements}
            catch_block.append({catch_type: blocks})

        # finally 代码解析
        finally_block = []
        if self.current_token_value() == "finally":
            self.eat_current_token_type("KEYWORD")  # finally
            self.eat_current_token_type("LBRACE")  # {
            finally_stmt = self.statement()
            finally_block.append(finally_stmt)
            self.eat_current_token_type("RBRACE")  # }
        return TryCatchFinallyNode(try_blocks, catch_block, finally_block)

    def increment_statement(self):
        # id++;
        id_name = self.current_token_value()
        self.eat_current_token_type("ID")
        self.eat_current_token_type("PLUS")
        self.eat_current_token_type("PLUS")
        self.eat_current_token_type("END")  # ;
        return IncrementNode(id_name)

    def interface_statement(self):
        # 解析interface

        """
            interface 名称 {
                方法名(参数);
            }

        :return:
        """
        self.eat_current_token_type("KEYWORD")  # interface
        interface_name = self.current_token_value()
        self.eat_current_token_type("ID")
        self.eat_current_token_type("LBRACE")  # {

        # 解析方法
        methods = []
        while self.current_token_value() != "}":
            # 解析方法
            method_name = self.current_token_value()
            self.eat_current_token_type("ID")
            methods.append(method_name)
            self.eat_current_token_type("LPAREN")  # (
            args = []
            while self.current_token_type() != 'RPAREN':
                args.append(self.current_token_value())
                self.eat_current_token_type("ID")
                if self.current_token_type() == 'COMMA':
                    self.eat_current_token_type("COMMA")
            self.eat_current_token_type("RPAREN")  # )
            self.eat_current_token_type("END")  # :
        self.eat_current_token_type("RBRACE")  # }
        return InterfaceNode(interface_name, methods)

    def list_destruct_assignment(self):
        # let [a,_,b] = [1,2,3];  list可以说变量或者list
        self.eat_current_token_type("KEYWORD")  # let
        self.eat_current_token_type("LBRACKET")  # [
        variables = {}  # {varname: index}
        index_count = 0  # 记录当前id的下标
        while self.current_token_type() == "ID" or self.current_token_type() == "UNDERLINE":
            if self.current_token_type() == "UNDERLINE":
                self.eat_current_token_type("UNDERLINE")  # _
            elif self.current_token_type() == "ID":
                # 使用列表存放变量名
                variables[self.current_token_value()] = index_count
                self.eat_current_token_type("ID")
            if self.current_token_type() == "COMMA":
                self.eat_current_token_type("COMMA")
            index_count += 1  # 下标自增
        self.eat_current_token_type("RBRACKET")  # ]
        self.eat_current_token_type("ASSIGN")  # =
        value = self.expr()  # 解析赋值表达式
        self.eat_current_token_type("END")  # ;
        # print(ListDeconstructAssignNode(variables, value))
        return ListDeconstructAssignNode(variables, value)

    def destruct_assignment(self):
        # let {a,b} = dict;  dict可以说变量或者dict
        self.eat_current_token_type("KEYWORD")  # let
        self.eat_current_token_type("LBRACE")  # {
        variables = []
        while self.current_token_type() == "ID":
            # 使用列表存放变量名
            variables.append(self.current_token_value())
            self.eat_current_token_type("ID")
            if self.current_token_type() == "COMMA":
                self.eat_current_token_type("COMMA")
        self.eat_current_token_type("RBRACE")  # }
        self.eat_current_token_type("ASSIGN")  # =
        value = self.expr()  # 解析赋值表达式
        self.eat_current_token_type("END")  # ;
        return DecontructAssignNode(variables, value)

    def switch_statement(self):
        self.eat_current_token_type("KEYWORD")  # switch
        self.eat_current_token_type("LPAREN")  # (
        expr = self.expr()  # 要比较的表达式
        self.eat_current_token_type("RPAREN")  # )
        self.eat_current_token_type("LBRACE")  # {
        cases = {}  # {case: statements}
        while self.current_token_value() != "}":

            # 解析case
            if self.current_token_value() == "case":
                self.eat_current_token_type("KEYWORD")  # case
                self.eat_current_token_type("LPAREN")  # :
                case_expr = self.expr()
                self.eat_current_token_type("RPAREN")  # )
                self.eat_current_token_type("LBRACE")  # {
                statements = []  # 语句列表
                while self.current_token_value() != "}":  # case的 }
                    statements.append(self.statement())  # 如果语句遇到},也会自己解析，所以最后case的}还在
                # cases.append((case_expr, {case_expr: statements}))
                cases[case_expr] = statements
                self.eat_current_token_type("RBRACE")  # }

            # 解析default
            elif self.current_token_value() == "default":
                self.eat_current_token_type("KEYWORD")  # default
                self.eat_current_token_type("LBRACE")  # {
                statements = []  # 语句列表
                while self.current_token_value() != "}":  # case的 }
                    statements.append(self.statement())  # 如果语句遇到},也会自己解析，所以最后case的}还在
                # cases.append((case_expr, {case_expr: statements}))
                cases[StringNode("default")] = statements
                self.eat_current_token_type("RBRACE")  # }
        self.eat_current_token_type("RBRACE")  # }
        return SwitchNode(expr, cases)

    def evaluate_call_class_inner_method(self):
        """
            使用this->xxx()解析调用时候，我觉得应该关注的是具体的类的实例上，毕竟实例的属性可能和类的默认值不同

        """
        # 解析实例内部的方法调用   this->xxx();
        # 进来的使用遇到的第一个token是this
        self.eat_current_token_type('KEYWORD')  # this
        self.eat_current_token_type('MINUS')  # -
        self.eat_current_token_type('GT')  # >
        method_name = self.current_token_value()  # 方法名
        self.eat_current_token_type('ID')
        self.eat_current_token_type('LPAREN')  # (
        args = []
        while self.current_token_type() != 'RPAREN':
            args.append(self.expr())
            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')
        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('END')  # ;

        return CallClassInnerMethod(method_name, args)

    def call_class_inner_method(self):
        # this->xxx();
        if self.current_token_value() == "this" and self.peek_next_token_type() == "MINUS" and \
                self.tokens[self.pos + 2][1] == ">":
            return True
        return False

    def method_method_call(self):
        # 解析实例调用方法的表达式 比如 p->show();
        instance_name = self.current_token_value()  # 实例名
        self.eat_current_token_type('ID')
        self.eat_current_token_type('MINUS')
        self.eat_current_token_type('GT')
        method_name = self.current_token_value()  # 方法名
        self.eat_current_token_type('ID')
        self.eat_current_token_type('LPAREN')  # (
        args = []
        while self.current_token_type() != 'RPAREN':
            args.append(self.expr())
            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')
        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('END')  # ;
        print("method_method_call: ", MethodCallNode(instance_name, method_name, args))

        return MethodCallNode(instance_name, method_name, args)

    # 解析类的声明  class 类名 { fields{} init{} methods{} }
    def class_declaration(self):
        # 进来的时候是class关键字
        global init_method
        self.eat_current_token_type("KEYWORD")  # class
        class_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 类名

        print("environment: ", )
        parent_name = ""
        # =======================extends=============================
        # extends 继承
        if self.current_token_value() == "extends":
            self.eat_current_token_type("KEYWORD")  # extends
            parent_name = self.current_token_value()
            self.eat_current_token_type('ID')  # 父类名
        # ====================================================

        # ===============解析接口实现=====================
        interfaces = []  # 接口列表
        if self.current_token_value() == "implements":
            self.eat_current_token_type("KEYWORD")  # implements
            while self.current_token_type() == "ID":
                interface_name = self.current_token_value()
                self.eat_current_token_type('ID')  # 接口名
                print("implements: ", interface_name)
                interfaces.append(interface_name)
                if self.current_token_type() == "COMMA":
                    self.eat_current_token_type("COMMA")

        # ===============解析接口实现=====================

        self.eat_current_token_type("LBRACE")  # {

        # =============static解析==========
        static_fields = {}  # 静态属性
        static_methods = {}  # 静态方法
        # =============static解析==========

        # 属性和方法
        fields = {}
        methods = {}
        while self.current_token_value() != "}":
            # 解析属性
            if self.current_token_value() == "fields":
                self.eat_current_token_type("KEYWORD")  # fields
                self.eat_current_token_type("LBRACE")  # {

                if_fields_parsed = False  # 是否解析过fields
                # name = value;
                while self.current_token_type() == "ID" or self.current_token_value() == "static":

                    # ======================static test========================
                    is_static = False
                    if self.current_token_value() == "static":
                        is_static = True
                        self.eat_current_token_type("KEYWORD")  # 消费 static

                    # ===============static test=============end==================

                    if_fields_parsed = True
                    field = self.current_token_value()  # 解析属性名
                    # 判断static修饰的属性名是否首字母大写，如果不是，报错

                    # ===========static== test==========================
                    if is_static and field[0].islower():
                        raise Exception(
                            "static field must be capitalized(static修饰的属性名必须首字母大写——表示public类型).")
                    # ===========static=======end=====================

                    self.eat_current_token_type("ID")
                    self.eat_current_token_type("ASSIGN")  # =
                    value = self.expr()  # 解析属性值

                    # ===========================static test=====================
                    if is_static:
                        static_fields[field] = value
                    else:
                        fields[field] = value
                    # ===========================static test============end========

                    # 解析属性值
                    # fields[field] = value  这里需要注释回来        (old version)
                    self.eat_current_token_type("END")  # ;
                if if_fields_parsed:
                    self.eat_current_token_type("RBRACE")  # }

            # 解析方法
            is_methods_parsed = False  # 是否解析过methods
            if self.current_token_value() == "methods":
                is_methods_parsed = True
                self.eat_current_token_type("KEYWORD")  # methods
                self.eat_current_token_type("LBRACE")  # {

                # =====================static method=======================
                while self.current_token_value() == "def" or self.current_token_value() == "static":
                    # method_def_node = self.function_declaration();
                    method_def_node = self.class_method_declaration()  # 解析方法定义节点
                    # SayHello': FunctionDeclarationNode(is_static=True,name=SayHello, args=['arg'],去哦他)

                    method_name = method_def_node.name  # 方法名
                    methods[method_name] = method_def_node  # 存入methods字典

                if is_methods_parsed:
                    self.eat_current_token_type("RBRACE")  # }

            # 解析构造方法, 只有一个，所以不需要while循环
            if_init_parsed = False  # 是否解析过init
            if self.current_token_value() == "init":
                if_init_parsed = True
                init_method = self.parse_init_method()
            if if_init_parsed:
                self.eat_current_token_type("RBRACE")  # }
        # 出来，遇到 }
        self.eat_current_token_type("RBRACE")  # 类声明的 }

        return ClassDeclarationNode(class_name, methods, fields,
                                    init_method, static_methods,
                                    static_fields, parent_name, interfaces)

    def parse_init_method(self):
        self.eat_current_token_type('KEYWORD')  # init
        self.eat_current_token_type('LPAREN')  # (

        # 默认值
        default_values = {}
        params = []
        while self.current_token_type() != 'RPAREN':
            # 解析参数
            params.append(self.current_token_value())
            self.eat_current_token_type('ID')

            # ===============解析默认值=========test=====
            if self.current_token_type() == 'ASSIGN':
                self.eat_current_token_type('ASSIGN')
                default_values[params[-1]] = self.expr()
            # ===============解析默认值=========test=====

            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')
        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('LBRACE')  # {
        body = []
        while self.current_token_type() != 'RBRACE':
            body.append(self.statement())
        node = FunctionDeclarationNode("init", params, body, default_values)

        return node

    def module_method_call(self):
        print("module_method_call: ")
        # 往函数调用方向凑 模块.方法(参数)
        name = self.current_token_value()  # 模块名称
        self.eat_current_token_type('ID')

        name += self.current_token_type()  # .
        self.eat_current_token_type('ID')

        name += self.current_token_value()  # 方法名称
        self.eat_current_token_type('ID')
        # print("name: ", name)
        self.eat_current_token_type('LPAREN')  # (

        named_arg_values = {}
        # 解析函数参数
        args = []
        if self.current_token_type() != 'RPAREN':  # 解析第一个参数
            # =====================解析命名参数==============test=====
            # add(b=1, c=2);
            if self.current_token_type() == 'ID' and self.peek_next_token_type() == 'ASSIGN':
                while self.current_token_type() == 'ID' and self.peek_next_token_type() == 'ASSIGN':
                    format_param = self.current_token_value()  # add(b = 1, c = 2); 中的b
                    self.eat_current_token_type('ID')  # add(b = 1, c = 2); 中的b
                    self.eat_current_token_type('ASSIGN')  # add(b = 1, c = 2); 中的=
                    named_arg_values[format_param] = self.expr()  # add(b = 1, c = 2); 中的1
                    # 最后一个参数的判断
                    if self.current_token_type() == 'COMMA':
                        self.eat_current_token_type('COMMA')  # ,
                print("passin_arg_values: ", named_arg_values)
            # ==================解析命名参数===============================================
            else:
                # ===================原来的解析方式=======位置参数=================================
                # 函数参数可以是任意表达式，比如1+2, add(), true and true, 1>2, "hello"等
                args.append(self.expr())
                while self.current_token_type() == 'COMMA':  # 解析多个参数
                    self.eat_current_token_type('COMMA')  # ,
                    args.append(self.expr())
                # ===================原来的解析方式========================================
        # 原来这两行代码是和else一个dent的，现在是测试
        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('END')  # ;
        return FunctionCallNode(name, args, named_arg_values)

    # 引入模块机制
    def import_module_statement(self):
        self.eat_current_token_type("KEYWORD")  # import

        # import的第二类型  import { pi,x } from Math
        import_elements = []
        if self.current_token_type() == "LBRACE":
            self.eat_current_token_type("LBRACE")
            while self.current_token_type() == "ID":
                # 导入的常量、方法等
                import_elements.append(self.current_token_value())
                self.eat_current_token_type("ID")
                if self.current_token_type() == "COMMA":
                    self.eat_current_token_type("COMMA")
            self.eat_current_token_type("RBRACE")
            self.eat_current_token_type("KEYWORD")  # from
            module_name = self.current_token_value()  # 模块名称
            self.eat_current_token_type("ID")
            return ImportModuleNode(module_name, import_elements, import_whole_module=False)

        # 第一类型  import Math
        else:
            module_name = self.current_token_value()
            self.eat_current_token_type('ID')  # 模块名
            if self.current_token_type() == "KEYWORD":  # as
                self.eat_current_token_type("KEYWORD")  # as
                alias_name = self.current_token_value()  # 别名
                self.eat_current_token_type("ID")
                # import Math as m  第一类型的第一种情况
                return ImportModuleNode(module_name, import_whole_module=True, alias=alias_name)
            else:
                # import Math   第一类型的第二种情况
                return ImportModuleNode(module_name, import_whole_module=True)

    def package_statement(self):
        self.eat_current_token_type('KEYWORD')  # package
        package_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 包名
        self.eat_current_token_type("LBRACE")  # {
        statements = []
        while self.current_token_type() != "RBRACE":
            statements.append(self.statement())
        self.eat_current_token_type("RBRACE")  # }
        # 不需要 ;
        return PackageDeclarationNode(package_name, statements)

    def const_statement(self):
        self.eat_current_token_type('KEYWORD')  # const
        const_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 变量名
        self.eat_current_token_type('ASSIGN')  # =
        const_value = self.expr()
        self.eat_current_token_type('END')  # ;
        return AssignmentNode(const_name, const_value, True)

    def factor(self):
        """
            factor 是最小的组成部分，可以是:
                 (1)一个数字 2 1.2
                 (2)一个变量 x
                 (3) 一个括号括起来的表达式 (1+2)
                 (4) 布尔值 true False
                 (5) 字符串 "hello world"
                 (6) 数组 [1,2,3]
                 (7) 对象 {name: "value"}
                 (3)一个括号括起来的表达式 (1+2)
                 (8) 函数调用 add(1,2)
                 (9) not 表达式:  not true
        """
        token = self.current_token_type()
        if token == 'NUMBER':
            # 解析数字: 字符串形式
            node = NumberNode(self.current_token_value())
            self.eat_current_token_type('NUMBER')
            print("node: ", node)
            return node
            # 解析函数调用表达式
        elif token == 'ID':

            # 判断是否为函数调用
            if self.peek_next_token_type() == 'LPAREN':
                return self.function_call_expr()  # 调用函数解析
            # 解析列表索引表达式
            elif self.peek_next_token_type() == 'LBRACKET':
                return self.index_expr()

            # 解析对象索引表达式  obj{expr}
            elif self.peek_next_token_type() == 'LBRACE':

                # 尝试解析结构体赋值
                if self.tokens[self.pos + 3][0] == "COLON":
                    return self.struct_assign_expr()

                # 尝试解析对象索引表达式  obj{expr}
                return self.object_index_expr()




            # 一个大坑: 对于模块调用方法,第一个token是Id, 那么对其的处理
            # 必须是在 elif token = "ID"分支下
            # 模块调用方法 比如 let z = module.add(1,2);
            elif self.peek_next_token_type() == "DOT":
                if self.tokens[self.pos + 2][0] == "ID":  # ID
                    if self.tokens[self.pos + 3][0] == "LPAREN":  # LPAREN
                        return self.module_method_call_expr()
                    else:
                        # 调用模块里面的变量或者常量  比如 @log(Util.pi);
                        return self.module_expr()  # 进入module_expr的时候还是ID,也就是模块名称

            # 解析获取对象属性的表达式  let z = p->Age;  @log(p->Age);这样的操作
            elif self.peek_next_token_type() == 'MINUS' and self.tokens[self.pos + 2][0] == 'GT':
                # if self.tokens[self.pos + 3][0] != 'LPAREN':  # 说明是获取对象的属性
                # return self.get_member_expr()  老名字
                return self.get_member_expr_or_method_call_expr()

            # 解析结构体对象访问属性的   p::x
            elif self.peek_next_token_type() == 'COLON' and self.tokens[self.pos + 2][0] == 'COLON':
                return self.struct_access_expr()

            # 解析变量表达式
            node = VariableNode(self.current_token_value())
            self.eat_current_token_type('ID')
            return node
        # 最小表达式：(1+2)这样的表达式, 递归解析嵌套括号
        elif token == 'LPAREN':
            self.eat_current_token_type('LPAREN')
            node = self.expr()
            self.eat_current_token_type('RPAREN')
            return node
        elif token == 'BOOL':
            node = BooleanNode(self.current_token_value())
            self.eat_current_token_type('BOOL')
            return node
        elif token == 'STRING':
            node = StringNode(self.current_token_value())
            self.eat_current_token_type('STRING')
            return node
        # 数组解析
        elif token == 'LBRACKET':  # [1,2,3]
            return self.parse_array()
        elif token == 'LBRACE':  # {name: "value"}
            return self.parse_object()

        # set集合
        elif self.current_token_value() == 'set' and self.peek_next_token_type() == "LT":
            print("执行了set")
            return self.parse_set()

            # 解析逻辑表达式
        elif token == 'NOT':
            return self.logical_expr()

        # 一下形式的lambda表达式:  let z = def(x,y){ x+y }
        elif self.current_token_value() == 'def':
            if self.peek_next_token_type() == 'LPAREN':
                # 返回FunctionDeclarationNode 即可
                return self.anonymous_function_declaration()

        # 真的lambda表达式：  let z = lambda x,y:x+y;
        elif self.current_token_value() == 'lambda':
            if self.peek_next_token_type() == 'ID':
                # 返回FunctionDeclarationNode 即可
                return self.real_lambda_function_declaration()

        # 箭头函数
        # let z = <<x,y>> =>{};
        elif self.current_token_type() == 'LT' and self.peek_next_token_type() == "LT":  # <
            return self.arrow_function_declaration()


        # 实例化对象  let z = new 类名();  右侧的: new 类名() 算作表达式
        elif self.current_token_value() == "new":
            return self.evaluate_new_expr()

        elif self.current_token_value() == 'this':
            print("进入parse_this")  # body里面的: ReturnNode(value=ThisNode())
            return self.parse_this()

        # if () x : y 这样的表达式
        elif self.current_token_value() == 'if':
            return self.if_expr()

        # match表达式
        elif self.current_token_value() == 'match':
            return self.match_expr()

        # let x= enum::Color::RED;
        elif self.current_token_value() == "enum" and self.peek_next_token_type() == "COLON":
            print("entered")
            return self.enum_access_expr()

        else:
            raise SyntaxError(
                f"Unexpected token: {token}, value = {self.current_token_value()}, next_token = {self.peek_next_token_type()}")

    def struct_access_expr(self):
        # 进来的时候是ID
        # 解析结构体对象访问属性的   p::x
        struct_instance_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 实例名
        self.eat_current_token_type('COLON')  # :
        self.eat_current_token_type('COLON')  # :
        struct_field_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 字段名
        return StructAccessNode(struct_instance_name, struct_field_name)

    def struct_assign_expr(self):  # 看作表达式
        # 例子:  Point { x: 1， y: 2}
        # 解析结构体赋值表达式
        struct_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 结构体名
        self.eat_current_token_type('LBRACE')  # {
        struct_fields_values = {}
        while self.current_token_type() != 'RBRACE':
            field_name = self.current_token_value()
            self.eat_current_token_type('ID')  # 字段名
            self.eat_current_token_type('COLON')  # :
            field_value = self.expr()  # 字段值
            struct_fields_values[field_name] = field_value
            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')  # ,
        self.eat_current_token_type('RBRACE')  # }
        return StructAssignNode(struct_name, struct_fields_values)

    def combine_expr(self):
        # 函数组合表达式
        # let z = f & g & i:
        # 特点：除了第一个id, 剩下的都是  一个 & 一个 id,
        funcs = []
        funcs.append(self.current_token_value())  # 第一个函数名
        self.eat_current_token_type('ID')
        while self.current_token_type() == "COMBINE":
            self.eat_current_token_type("COMBINE")
            funcs.append(self.current_token_value())
            self.eat_current_token_type("ID")
        return CombineNode(funcs)

    def parse_set(self):
        # let z = set<1,2>;
        self.eat_current_token_type('KEYWORD')  # set
        self.eat_current_token_type('LT')  # <
        set_values = []
        while self.current_token_type() != 'GT':
            set_values.append(self.expr())
            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')
        print("token: ", self.current_token_value())
        self.eat_current_token_type('GT')  # >
        return SetNode(set_values)

    def match_expr(self):
        """
           let z = match(x){
                1 => "one",
                2 => "two",
            }
        """
        self.eat_current_token_type('KEYWORD')  # match
        self.eat_current_token_type('LPAREN')  # (
        expr = self.expr()  # 变量
        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('LBRACE')  # {

        case_value_dict = {}  # 解析case的value

        while self.current_token_type() != 'RBRACE':
            case = self.expr()
            self.eat_current_token_type('ASSIGN')  # =
            self.eat_current_token_type('GT')  # >
            expr_if_match = self.expr()
            # 赋值
            case_value_dict[case] = expr_if_match
            # 还有进步空间，比如一些语句也可以在这执行
            self.eat_current_token_type('COMMA')  # ,
        self.eat_current_token_type('RBRACE')  # }
        return MatchExprNode(expr, case_value_dict)

    def if_expr(self):
        # if(condi) x : y
        self.eat_current_token_type('KEYWORD')  # if
        self.eat_current_token_type('LPAREN')  # (
        condition = self.expr()
        self.eat_current_token_type('RPAREN')  # )
        expr_if_true = self.expr()
        self.eat_current_token_type('COLON')  # :
        expr_if_false = self.expr()
        return IfExprNode(condition, expr_if_true, expr_if_false)

    def parse_this(self):
        self.eat_current_token_type('KEYWORD')  # 'this'
        return ThisNode()

    def parse_comment(self):
        self.eat_current_token_type("COMMENT")  # #
        comment_content = ""
        while self.tokens[self.pos][0] != "COMMENT":
            comment_content += self.current_token_value()
            self.pos += 1
        self.eat_current_token_type("COMMENT")
        return CommentNode(comment_content)

    def get_member_expr_or_method_call_expr(self):

        # ===============version 1=============================
        # 获取成员属性的表达式 @log(p->Age);
        # instance_name = self.current_token_value()
        # self.eat_current_token_type('ID')  # instance_name: p
        # self.eat_current_token_type('MINUS')  # -
        # self.eat_current_token_type('GT')  # >
        # member_name = self.current_token_value()
        # self.eat_current_token_type('ID')  # member_name: Age
        # return GetMemberNode(instance_name, member_name)
        # ===============version 1=============================

        # ====================合并属性访问和方法调用表达式=======================
        # instance_name = self.current_token_value()
        # self.eat_current_token_type('ID')
        # self.eat_current_token_type('MINUS')
        # self.eat_current_token_type('GT')
        # member_or_method_name = self.current_token_value()
        # self.eat_current_token_type('ID')
        #
        # if self.current_token_type() == 'LPAREN':
        #     # 这是一个方法调用
        #     self.eat_current_token_type('LPAREN')
        #     args = []
        #     while self.current_token_type() != 'RPAREN':
        #         args.append(self.expr())
        #         if self.current_token_type() == 'COMMA':
        #             self.eat_current_token_type('COMMA')
        #     self.eat_current_token_type('RPAREN')
        #     return MethodCallNode(instance_name, member_or_method_name, args)
        # else:
        #     # 这是一个属性访问
        #     return GetMemberNode(instance_name, member_or_method_name)

        # ==============version 2=====================================================
        instance_or_class_name = self.current_token_value()
        self.eat_current_token_type('ID')
        self.eat_current_token_type('MINUS')
        self.eat_current_token_type('GT')
        member_or_method_name = self.current_token_value()
        self.eat_current_token_type('ID')

        if self.current_token_type() == 'LPAREN':
            # 这是一个方法调用
            self.eat_current_token_type('LPAREN')
            args = []
            while self.current_token_type() != 'RPAREN':
                args.append(self.expr())
                if self.current_token_type() == 'COMMA':
                    self.eat_current_token_type('COMMA')
            self.eat_current_token_type('RPAREN')
            return MethodCallNode(instance_or_class_name, member_or_method_name, args)
        else:
            # 这是一个属性访问，可能是实例属性或静态属性
            return GetMemberNode(instance_or_class_name, member_or_method_name)
        # ========================version 2 ===end===========================================================================

    def evaluate_new_expr(self):
        # let z = new 类名();
        object_name = self.tokens[self.pos - 2][1]
        self.eat_current_token_type('KEYWORD')  # new
        class_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 类名
        self.eat_current_token_type('LPAREN')  # (
        args = []
        if self.current_token_type() != 'RPAREN':  # 解析第一个参数
            # 函数参数可以是任意表达式，比如1+2, add(), true and true, 1>2, "hello"等
            args.append(self.expr())
            while self.current_token_type() == 'COMMA':  # 解析多个参数
                self.eat_current_token_type('COMMA')  # ,
                args.append(self.expr())
        self.eat_current_token_type('RPAREN')  # )
        return NewObjectNode(object_name, class_name, args)

    def module_expr(self):
        # 该返回什么节点呢  Variable吧
        # module.变量名 或者 module.常量名
        module_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 模块名
        self.eat_current_token_type('DOT')  # .
        var_name = self.current_token_value()
        self.eat_current_token_type('ID')  # 变量名
        return VariableNode(module_name + "." + var_name)

    def module_method_call_expr(self):
        # print("called module_method_call_expr")
        # let z = 模块.add(1,2);
        name = self.current_token_value()  # 模块名称
        self.eat_current_token_type('ID')
        name += self.current_token_value()
        self.eat_current_token_type('DOT')  # .
        name += self.current_token_value()
        self.eat_current_token_type('ID')  # 方法名

        self.eat_current_token_type('LPAREN')  # (

        # 解析函数参数
        args = []
        if self.current_token_type() != 'RPAREN':  # 解析第一个参数
            # 函数参数可以是任意表达式，比如1+2, add(), true and true, 1>2, "hello"等
            args.append(self.expr())
            while self.current_token_type() == 'COMMA':  # 解析多个参数
                self.eat_current_token_type('COMMA')  # ,
                args.append(self.expr())
        self.eat_current_token_type('RPAREN')  # )
        print("module_method_call_expr的args： ", args)
        return FunctionCallNode(name, args)

    def arrow_function_declaration(self):
        # let z = <<x = 1,y = 2>> =>{    //code   };
        arrow_func_name = self.tokens[self.pos - 2][1]  # 箭头函数名称
        self.eat_current_token_type('LT')  # <
        self.eat_current_token_type('LT')  # <

        default_values = {}

        params = []
        while self.current_token_type() != 'GT':
            # 解析参数
            params.append(self.current_token_value())  # 参数名称
            self.eat_current_token_type('ID')

            # ===============解析默认值=========test=====
            # # 检查是否有默认值
            if self.current_token_type() == 'ASSIGN':
                self.eat_current_token_type('ASSIGN')  # '='
                default_values[params[-1]] = self.expr()  # 解析默认值
                # print("解析到的默认值： ", default_values[params[-1]])
            # ===============解析默认值=========test=====

            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')

        self.eat_current_token_type('GT')  # >
        self.eat_current_token_type('GT')  # >
        self.eat_current_token_type('ASSIGN')  # =
        self.eat_current_token_type('GT')  # >
        self.eat_current_token_type('LBRACE')  # {

        body = []
        while self.current_token_type() != 'RBRACE':  # }
            body.append(self.statement())
        self.eat_current_token_type('RBRACE')  # }
        # ; 不需要处理
        return FunctionDeclarationNode(arrow_func_name, params, body, default_values)

    def real_lambda_function_declaration(self):
        # let z = lambda x,y: x+y; 这种形式里面的z就是函数名
        lambda_name = self.tokens[self.pos - 2][1]  # lambda函数名称
        self.eat_current_token_type('KEYWORD')  # lambda关键字
        # 解析参数
        params = []
        while self.current_token_type() != 'COLON':  # :
            # 解析参数
            params.append(self.current_token_value())  # 参数名
            self.eat_current_token_type('ID')  # 参数名
            if self.current_token_type() == 'COMMA':  # ,
                self.eat_current_token_type('COMMA')

        self.eat_current_token_type('COLON')  # :
        # 解析函数体
        body = []
        expr = self.expr()
        body.append(expr)
        # 处理末尾的分号???  不需要，因为assignment语句处理了
        # if self.current_token_type() == 'END':
        #     self.eat_current_token_type('END')
        return FunctionDeclarationNode(lambda_name, params, body)

    # let x = def(x,y){ x+y }类型的表达式
    def anonymous_function_declaration(self, passin_name=None):
        # let add = def(x = 1,y = 10){ return x+y; }
        lambda_name = self.tokens[self.pos - 2][1]

        # if passin_name is not None:
        #     lambda_name = passin_name
        # # 解析函数名: 名称有问题，应该设置为一个不会重复的str(数字)
        # # print(" self.tokens[self.pos - 2][1]: ", self.tokens[self.pos - 2][1])
        # # lambda_name = str(uuid.uuid4())  # 随机生成一个uuid作为函数名
        # print("lambda_name: ", lambda_name)

        self.eat_current_token_type('KEYWORD')  # def
        self.eat_current_token_type("LPAREN")  # (

        # =============解析默认参数和命名参数====================================
        # 默认值
        default_values = {}

        # 解析参数
        params = []
        while self.current_token_type() != 'RPAREN':
            # 解析参数
            params.append(self.current_token_value())  # 参数名称
            self.eat_current_token_type('ID')
            # print("params[-1]: ", params[-1])

            # ===============解析默认值=========test=====
            if self.current_token_type() == 'ASSIGN':  # 有默认值 x = 1,
                self.eat_current_token_type('ASSIGN')
                default_values[params[-1]] = self.expr()

            # ===============解析默认值=========test=====
            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')

        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('LBRACE')  # {
        body = []
        while self.current_token_type() != 'RBRACE':
            body.append(self.statement())
        self.eat_current_token_type('RBRACE')  # }
        # self.eat_current_token_type('END')  # ;
        return FunctionDeclarationNode(lambda_name, params, body, default_values, func_type="anonymous")

    def class_method_declaration(self):
        """
            解析类方法声明语句

            class Person{
               methods{
                    static def xxx(){}
               }

            }
        """
        is_static = False
        if self.current_token_value() == "static":
            is_static = True
            self.eat_current_token_type("KEYWORD")  # static
        self.eat_current_token_type('KEYWORD')  # 'function'  'def'
        name = self.current_token_value()  # 函数名
        self.eat_current_token_type('ID')  # 函数名
        self.eat_current_token_type('LPAREN')  # (

        # 默认值
        default_values = {}

        params = []
        while self.current_token_type() != 'RPAREN':
            # 解析参数
            params.append(self.current_token_value())
            self.eat_current_token_type('ID')

            # ===============解析默认值=========test=====
            if self.current_token_type() == 'ASSIGN':
                self.eat_current_token_type('ASSIGN')
                default_values[params[-1]] = self.expr()
            # ===============解析默认值=========test=====

            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')
        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('LBRACE')  # {
        body = []
        while self.current_token_type() != 'RBRACE':
            body.append(self.statement())
        self.eat_current_token_type('RBRACE')
        return FunctionDeclarationNode(name, params, body, default_values, is_static, tag="class_method")

    def function_declaration(self):
        """
            参数解析：目前支持传入数字、字符串、布尔值、数组、对象、函数，但是不支持传入函数
        """

        self.eat_current_token_type('KEYWORD')  # 'function'  'def'
        name = self.current_token_value()  # 函数名
        self.eat_current_token_type('ID')  # 函数名
        self.eat_current_token_type('LPAREN')  # (

        # 默认值
        default_values = {}

        params = []
        while self.current_token_type() != 'RPAREN':
            # 解析参数
            params.append(self.current_token_value())
            self.eat_current_token_type('ID')

            # ===============解析默认值=========test=====
            if self.current_token_type() == 'ASSIGN':
                self.eat_current_token_type('ASSIGN')
                default_values[params[-1]] = self.expr()
            # ===============解析默认值=========test=====

            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')
        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('LBRACE')  # {
        body = []
        while self.current_token_type() != 'RBRACE':
            body.append(self.statement())
        self.eat_current_token_type('RBRACE')

        return FunctionDeclarationNode(name, params, body, default_values)

    def for_in_statement(self):
        """
            1, for in解析
                for(ele in []){}
            2, for(idx in 1..10){}
        """
        self.eat_current_token_type('KEYWORD')  # for
        self.eat_current_token_type("LPAREN")

        var_name = self.current_token_value()  # 变量名
        self.eat_current_token_type('ID')  # 变量名

        # 第二类 for : 语法
        # for (idx : 55 to getNumber()){
        #
        # }
        if self.current_token_type() == 'COLON':
            self.eat_current_token_type('COLON')  # :
            start_value = self.expr()
            self.eat_current_token_type('KEYWORD')  # to
            end_value = self.expr()
            self.eat_current_token_type("RPAREN")  # )
            self.eat_current_token_type("LBRACE")  # {
            # block statements
            block_statements = []  # 存放if语句块中的语句
            while self.current_token_type() != 'RBRACE':
                block_statements.append(self.statement())
            self.eat_current_token_type("RBRACE")  # }
            return ForRangeNumberNode(var_name, start_value, end_value, block_statements)

        # for in语法
        if self.current_token_value() == 'in':
            self.eat_current_token_type('KEYWORD')  # in
            iterable_obj = self.expr()
            self.eat_current_token_type("RPAREN")  # )
            self.eat_current_token_type('LBRACE')  # {
            # block statements
            block_statements = []  # 存放if语句块中的语句
            while self.current_token_type() != 'RBRACE':
                block_statements.append(self.statement())
            self.eat_current_token_type("RBRACE")  # }
            return ForInNode(var_name, iterable_obj, block_statements)

    def elif_statement(self):
        """
            解析得到的结构：
                [{condition: expr, elif_statements: [stmt,stmt},{}]

        :return:
        """
        elif_statements = []
        if self.current_token_value() == 'elif':
            # 解析elif语句, 可以有多个elif语句
            while self.current_token_value() == 'elif':
                self.eat_current_token_type('KEYWORD')  # elif
                self.eat_current_token_type("LPAREN")  # (
                # 条件
                elif_condition = self.expr()
                self.eat_current_token_type("RPAREN")  # )
                self.eat_current_token_type("LBRACE")  # {
                # block statements
                elif_block_statements = []  # 存放elif语句块中的语句
                while self.current_token_type() != 'RBRACE':
                    elif_block_statements.append(self.statement())
                self.eat_current_token_type("RBRACE")  # }

                # [{condition: expr, elif_statements: [stmt,stmt},{}]
                part = {'condition': elif_condition, 'elif_statements': elif_block_statements}
                elif_statements.append(part)
        return elif_statements

    def else_statement(self):
        # 解析else语句
        else_statements = []
        if self.current_token_type() == 'KEYWORD' and self.current_token_value() == 'else':
            self.eat_current_token_type('KEYWORD')  # else
            self.eat_current_token_type("LBRACE")  # {
            while self.current_token_type() != 'RBRACE':
                else_statements.append(self.statement())
            self.eat_current_token_type("RBRACE")  # }
        return else_statements

    """
               if(){

               }elif(){

               }else(){

               }
           """

    def if_statement(self):

        elif_statements = []
        else_statements = []

        self.eat_current_token_type('KEYWORD')  # if
        self.eat_current_token_type("LPAREN")  # (
        # 条件
        condition = self.expr()
        self.eat_current_token_type("RPAREN")  # )
        self.eat_current_token_type("LBRACE")  # {

        # block statements
        block_statements = []  # 存放if语句块中的语句
        while self.current_token_type() != 'RBRACE':
            stmt = self.statement()
            print("stmt: ", stmt)
            block_statements.append(stmt)

        self.eat_current_token_type("RBRACE")  # }
        print("self.current_token_value(): ", self.current_token_value())

        # 解析elif和else语句
        if self.current_token_value() == 'elif':
            # print("进入elif语句")
            # 解析elif语句, 可以有多个elif语句
            elif_statements = self.elif_statement()

        if self.current_token_value() == 'else':
            # 解析else语句
            else_statements = self.else_statement()
        return IfStatementNode(condition, block_statements, elif_statements, else_statements)

    def break_statement(self):
        self.eat_current_token_type('KEYWORD')  # break
        self.eat_current_token_type("END")  # ;
        return BreakNode()

    def return_statement(self):
        self.eat_current_token_type('KEYWORD')  # return
        return_value = self.expr()
        self.eat_current_token_type("END")  # ;
        return ReturnNode(return_value)

    def loop_statement(self):
        self.eat_current_token_type('KEYWORD')  # loop
        self.eat_current_token_type("LPAREN")  # (
        # 条件
        condition = self.expr()
        self.eat_current_token_type("RPAREN")  # )
        self.eat_current_token_type("LBRACE")  # {
        # block statements
        block_statements = []  # 存放if语句块中的语句
        while self.current_token_type() != 'RBRACE':
            block_statements.append(self.statement())
        self.eat_current_token_type("RBRACE")  # }
        return LoopNode(condition, block_statements)

    def let_statement(self):
        """
                let 语句得到的节点就是： name = value;
        """
        # pos会自动移动到下一个token  let是keyword类型
        self.eat_current_token_type('KEYWORD')  # let
        name = self.current_token_value()  # 变量名
        self.eat_current_token_type('ID')
        self.eat_current_token_type('ASSIGN')
        value = self.expr()
        print("进入")

        # =====================================
        if isinstance(value, FunctionDeclarationNode):
            value.tag = "assignment_value"  # 表示是作为赋值语句的值而已

        # 如果value是作为参数解析传递，应该做一个标记
        # print("val: ", value)
        # =====================================

        # print("val: ",value)
        if self.current_token_type() == 'END':
            self.eat_current_token_type('END')
        return AssignmentNode(name, value)

    """
        解析赋值语句
    """

    def assignment(self):
        name = self.current_token_value()
        self.eat_current_token_type('ID')
        self.eat_current_token_type('ASSIGN')
        value = self.expr()
        if self.current_token_type() == 'END':
            self.eat_current_token_type('END')
        return AssignmentNode(name, value)

    """
        解析函数调用语句
    """

    def function_call_statement(self):
        # print("function_call_statement")
        self.eat_current_token_type('FUNCTION_CALL_PREFIX')  # @
        # 完成
        name = self.current_token_value()  # 函数名,ID
        self.eat_current_token_type('ID')  # 函数名

        # 尝试解析 @util.add();这样的调用
        if self.current_token_type() == 'DOT':
            name += '.'
            self.eat_current_token_type('DOT')
            name += self.current_token_value()
            self.eat_current_token_type('ID')

        self.eat_current_token_type('LPAREN')  # (

        named_arg_values = {}
        # 解析函数参数
        args = []
        if self.current_token_type() != 'RPAREN':  # 解析第一个参数
            # =====================解析命名参数==============test=====
            # add(b=1, c=2);
            if self.current_token_type() == 'ID' and self.peek_next_token_type() == 'ASSIGN':
                while self.current_token_type() == 'ID' and self.peek_next_token_type() == 'ASSIGN':
                    format_param = self.current_token_value()  # add(b = 1, c = 2); 中的b
                    self.eat_current_token_type('ID')  # add(b = 1, c = 2); 中的b
                    self.eat_current_token_type('ASSIGN')  # add(b = 1, c = 2); 中的=
                    named_arg_values[format_param] = self.expr()  # add(b = 1, c = 2); 中的1
                    # 最后一个参数的判断
                    if self.current_token_type() == 'COMMA':
                        self.eat_current_token_type('COMMA')  # ,
                print("passin_arg_values: ", named_arg_values)
            # ==================解析命名参数===============================================
            else:
                # ===================原来的解析方式=======位置参数=================================
                # 函数参数可以是任意表达式，比如1+2, add(), true and true, 1>2, "hello"等
                args.append(self.expr())
                while self.current_token_type() == 'COMMA':  # 解析多个参数
                    self.eat_current_token_type('COMMA')  # ,
                    args.append(self.expr())
                # ===================原来的解析方式========================================
        # 原来这两行代码是和else一个dent的，现在是测试
        self.eat_current_token_type('RPAREN')  # )
        self.eat_current_token_type('END')  # ;
        return FunctionCallNode(name, args, named_arg_values)

    # def function_call_expr(self):
    #     # 完成  let z = getCb()(1);
    #     name = self.current_token_value()  # 函数名,ID
    #     self.eat_current_token_type('ID')  # 函数名
    #     self.eat_current_token_type('LPAREN')  # (
    #
    #     # 解析函数参数
    #     args = []
    #     if self.current_token_type() != 'RPAREN':  # 解析第一个参数
    #         # 函数参数可以是任意表达式，比如1+2, add(), true and true, 1>2, "hello"等
    #         args.append(self.expr())
    #         while self.current_token_type() == 'COMMA':  # 解析多个参数
    #             self.eat_current_token_type('COMMA')  # ,
    #             args.append(self.expr())
    #     self.eat_current_token_type('RPAREN')  # )
    #
    #     return FunctionCallNode(name, args)
    #
    #
    #
    #
    #     # ========================version2==================================
    #     # name = self.current_token_value()
    #     # self.eat_current_token_type('ID')
    #     # self.eat_current_token_type('LPAREN')
    #     #
    #     # args = []
    #     # while self.current_token_type() != 'RPAREN':
    #     #     # 检查是否是函数定义
    #     #     if self.current_token_type() == 'KEYWORD' and self.current_token_value() in ['def', 'lambda']:
    #     #         args.append(self.function_as_argument())
    #     #     elif self.current_token_type() == 'LT' and self.peek_next_token_type() == 'LT':
    #     #         args.append(self.arrow_function_declaration())
    #     #     else:
    #     #         args.append(self.expr())
    #     #
    #     #     if self.current_token_type() == 'COMMA':
    #     #         self.eat_current_token_type('COMMA')
    #     #
    #     # self.eat_current_token_type('RPAREN')
    #     # return FunctionCallNode(name, args)
    #
    def function_call_expr(self):
        expr = self.parse_single_function_call()

        # 解析连续的函数调用
        while self.current_token_type() == 'LPAREN':
            expr = self.parse_single_function_call(expr)

        return expr

    def parse_single_function_call(self, func_expr=None):
        if func_expr is None:
            name = self.current_token_value()  # 函数名,ID
            self.eat_current_token_type('ID')  # 函数名
        else:
            name = func_expr

        self.eat_current_token_type('LPAREN')  # (

        # 解析函数参数
        args = []
        if self.current_token_type() != 'RPAREN':  # 解析第一个参数
            # 函数参数可以是任意表达式，比如1+2, add(), true and true, 1>2, "hello"等
            args.append(self.expr())
            while self.current_token_type() == 'COMMA':  # 解析多个参数
                self.eat_current_token_type('COMMA')  # ,
                args.append(self.expr())
        self.eat_current_token_type('RPAREN')  # )

        return FunctionCallNode(name, args)

    def comparison_expr(self):
        """解析比较表达式，如 >, <, == 等"""
        node = self.term()  # 解析乘法和除法
        comparison_operators = ("GT", "LT", "GE", "LE", "EQ", "NEQ")
        while self.current_token_type() in comparison_operators:
            op = self.current_token_type()
            self.eat_current_token_type(op)
            right_node = self.term()
            node = BinaryOpNode(node, op, right_node)  # 创建比较运算的节点
        return node

    # term就是解析乘法和除法的表达式，比factor优先级高
    # 先调用

    # 返回node 原名叫做expr
    def expr(self):
        # expr要么返回BinaryOpNode, 要么是term()

        node = self.term()
        # 优先级比term低
        operators = ("PLUS", "MINUS", "OR")
        while self.current_token_type() in operators:
            op = self.current_token_type()  # 获取操作符的类型
            self.eat_current_token_type(op)
            node: Node = BinaryOpNode(node, op, self.term())
        return node

    """
        解析乘除法
        term优先级比expr高，所以先解析term, 再解析expr
    """

    def term(self):
        """
            在BNF（巴科斯范式）中，term 是表达式解析中的一个中间层级，
            位于 factor 和 expr 之间。term 通常用于表示乘法和除法运算的表达式部分。
            比如：3 * 4  ,而3和4是factor，*是operator
        """
        node = self.factor()  # 先解析factor
        # 放在这里的比expr中的优先级高，所以先解析term
        operators = ("MUL", "DIV", "FLOOR_DIV", "POW", "MOD",  # 乘法和除法运算符
                     "AND", "EQ", "NEQ",  # 逻辑运算符
                     "LT", "GT", "GE", "LE", "NEQ", "EQ"  # 比较运算符
                     )
        while self.current_token_type() in operators:
            op = self.current_token_type()  # 获取操作符的类型
            self.eat_current_token_type(op)
            node: Node = BinaryOpNode(node, op, self.factor())
        return node

    def logical_expr(self):
        """解析逻辑表达式，处理and和or"""
        node = self.not_expr()  # 先解析 not 表达式
        while self.current_token_type() in ('AND', 'OR'):
            op = self.current_token_type()  # 获取操作符的类型
            self.eat_current_token_type(op)
            right_node = self.not_expr()  # 右侧为 not 表达式
            node = BinaryOpNode(node, op, right_node)  # 形成新的节点
        return node

    def not_expr(self):
        """解析not表达式"""
        if self.current_token_type() == 'NOT':
            self.eat_current_token_type('NOT')
            operand = self.not_expr()  # 递归解析
            return UnaryOpNode('not', operand)  # 创建 UnaryOpNode
        return self.expr()  # 否则解析一般表达式

    def current_token_type(self):
        return self.tokens[self.pos][0]

    def current_token_value(self):
        # 获取下一个token的value
        if self.pos <= len(self.tokens) - 1:
            return self.tokens[self.pos][1]
        else:
            return None

    def peek_next_token_type(self):
        # tokens的格式是【(token_type, token_value),(token_type, token_value),...】
        # token_type是字符串, token_value是字符串
        return self.tokens[self.pos + 1][0]

    # 判断是不是指定的token_type, 如果是, 则移动pos指针, 如果不是, 则报错
    def eat_current_token_type(self, token_type):
        # tokens的格式是【(token_type, token_value),(token_type, token_value),...】
        if self.tokens[self.pos][0] == token_type:
            self.pos += 1
        else:
            raise SyntaxError(f"Expected {token_type} but got {self.tokens[self.pos][0]}")

    def parse_array(self):
        self.eat_current_token_type('LBRACKET')
        # 解析数组元素
        elements = []
        while self.current_token_type() != 'RBRACKET':
            # elements.append(self.factor())  这个是原来的，factor()只能解析单个元素
            # 数组元素可以是任意表达式，比如1+2, add(), true and true, 1>2, "hello"等
            elements.append(self.expr())

            if self.current_token_type() == 'COMMA':
                self.eat_current_token_type('COMMA')
        self.eat_current_token_type('RBRACKET')
        return ListNode(elements)

    def parse_object(self):
        self.eat_current_token_type('LBRACE')
        # 解析对象属性
        properties_values = {}
        while self.current_token_type() != 'RBRACE':
            # 解析属性名
            property_name = self.current_token_value()
            # ==================这里限制了key可以的类型=========================
            # self.eat_current_token_type('ID')  # 比如"name"
            self.pos += 1  # 跳过ID,从而支持任意类型的key, 建议是ID类型、数字类型、字符串类型
            self.eat_current_token_type('COLON')  # :
            # ==================这里限制了value可以的类型==================
            # 解析属性值
            # property_value = self.factor()  # 这个是原来的，factor()只能解析单个元素
            property_value = self.expr()
            properties_values[property_name] = property_value
            if self.current_token_type() == 'COMMA':  # ,
                self.eat_current_token_type('COMMA')
        self.eat_current_token_type('RBRACE')

        return ObjectNode(properties_values)

    def index_expr(self):
        node = self.current_token_value()  # 解析列表名
        self.eat_current_token_type('ID')  # 解析列表名

        while True:
            # 解析列表索引: id[expr] 或者 id[expr1][expr2] 或者切片 id[expr1:expr2]
            if self.current_token_type() == 'LBRACKET':
                indexes = []
                while self.current_token_type() == 'LBRACKET':
                    self.eat_current_token_type('LBRACKET')  # [
                    start_index = self.expr()  # 解析start_index
                    end_index = None
                    if self.current_token_type() == 'COLON':  # 解析end_index
                        self.eat_current_token_type('COLON')
                        end_index = self.expr()
                    self.eat_current_token_type('RBRACKET')  # ]
                    indexes.append((start_index, end_index))

                if len(indexes) == 1:
                    node = ListIndexNode(node, indexes[0][0], indexes[0][1])
                else:
                    node = MultiListIndexNode(node, indexes)

            # 解析属性访问
            elif self.current_token_type() == 'LBRACE':
                self.eat_current_token_type('LBRACE')  # {
                property_name = self.expr()
                self.eat_current_token_type('RBRACE')  # }
                node = ObjectIndexNode(node, property_name)

            else:
                break

        return node

    def object_index_expr(self):
        return self.index_expr()  # 直接调用index_expr来处理所有情况

    def prev_token_type(self):
        # 获取前一个token的类型
        return self.tokens[self.pos - 1][0]


if __name__ == '__main__':

    # 语法冲突: 对象名称{}  访问对象属性的
    code = """
         
         @annotation(returnType = "int", paramsNum = 2)
         def add(a, b=10){
             return a + b;
         }
         let dc = GetFnAnnotations(add);
         
    """

    # 引入类的机制和引入包的方法一致
    # environment中存放类的全部属性和方法，对于调用静态的方法，直接在environment中查找
    # 对于static类型的： 加入到environment中，形式是：类名.xxx
    # 对于非static类型的： 加入到environment中,形式是：实例.xxx
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    for i in tokens:
        print(i)
    # 每个语句构成一个Node, 语句之间用分号分隔,多个Node构成一个列表
    # [AssignmentNode(name=y, value=NumberNode(value=3)),
    #  AssignmentNode(name=x, value=BinaryOpNode(left=NumberNode(value=3),
    #       op=PLUS, right=NumberNode(value=2)))]
    parser = Parser(tokens)
    ast = parser.parse()  # 生成AST, 多个xxNode组成的列表
    for node in ast:
        print(node)
