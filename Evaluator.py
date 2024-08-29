import re
import uuid
from typing import List

from colorama import Fore, Back

from interpreter.ClassNodes import ClassDeclarationNode, NewObjectNode, MethodCallNode, GetMemberNode, \
    CallClassInnerMethod, ThisNode, InterfaceNode, GetMemberNodeByThis
from interpreter.utils.FileDir import FileSystemUtils
from interpreter.utils.Random import RandomUtils
from interpreter.utils.Time import TimeUtils
from interpreter.utils.common import CommonUtils
from interpreter.utils.datastructure.DictUtils import DictUtils
from interpreter.utils.datastructure.ListUtils import ListUtils
from interpreter.Nodes import AssignmentNode, NumberNode, BinaryOpNode, VariableNode, FunctionCallNode, StringNode, \
    ListNode, ObjectNode, FunctionDeclarationNode, IfStatementNode, BooleanNode, LoopNode, BreakNode, ReturnNode, \
    ListIndexNode, ObjectIndexNode, ForInNode, PackageDeclarationNode, ImportModuleNode, CommentNode, IfExprNode, \
    MatchExprNode, SwitchNode, DecontructAssignNode, ListDeconstructAssignNode, ForRangeNumberNode, TryCatchFinallyNode, \
    IncrementNode, DecrementNode, SetNode, CombineNode, MultiListIndexNode, StructDeclarationNode, StructAssignNode, \
    StructAccessNode, EnumDeclarationNode, EnumAccessNode, ChainNode, DoWhileNode, ListGeneratorNode, AbsNode, \
    SerialCall, PlusAssignNode, MinusAssignNode, MultiplyAssignNode, DivideAssignNode
from interpreter.Parser import Parser
from interpreter.utils.datastructure.StringUtils import StringUtils
from interpreter.Tokenizer import Tokenizer
from interpreter.utils.math.MathUtils import MathUtils


class BreakException(Exception):
    """自定义异常，用于处理循环中的 break 语句"""
    pass


class Evaluator:
    def __init__(self):
        # 环境变量
        self.environment = {
            "arg_to_instance": {
                # "painterVan": "x",
            },  # 建立传入参数和实例的映射，用于多态的实现  {形参: 实参, 形参: 实参}
            "instances": {},  # 记录创建的类的实例
            "constants": [],  # 记录声明的常量
            "objects": {},  # 导入的类和创建的对象
            "interfaces": {},  # 记录接口
            "structs": {},  # 记录结构体
            "enums": {}  # 记录枚举类型

        }
        self.current_object = None  # 当前this指向的对象
        self.packages = {}  # 导入的模块

    def evaluate(self, node):
        """
            解析器的入口函数，根据不同的节点类型，调用相应的解析函数
            用于解析AST，得到具体的结果
            比如，对于NumberNode，调用evaluate_number()函数，返回数字的值

        """

        # 数据类型解析
        if isinstance(node, (int, float, bool, str,list,dict,tuple)):
            return node

        if isinstance(node, NumberNode):
            return self.evaluate_number(node)
        elif isinstance(node, StringNode):  # ""
            return self.evaluate_string(node)
        elif isinstance(node, ListNode):  # []
            return [self.evaluate(n) for n in node.elements]
        elif isinstance(node, ObjectNode):  # {}
            return self.evaluate_object(node)
        elif isinstance(node, VariableNode):
            return self.evaluate_variable(node)
        elif isinstance(node, BooleanNode):
            if node.value == "True":
                return True
            elif node.value == "False":
                return False
        # 语句解析
        elif isinstance(node, IfStatementNode):
            """
                  self.condition = condition
                  self.if_body = if_body
                  self.elif_ = elif_
                 self.else_ = else_
            """
            return self.evaluate_if_statement(node)

        # 表达式解析
        elif isinstance(node, BinaryOpNode):
            return self.evaluate_binary_op(node)
        elif isinstance(node, AssignmentNode):
            return self.evaluate_assignment(node)

        # 循环解析
        elif isinstance(node, BreakNode):
            # 遇到break语句，抛出BreakException异常，
            # 然后在循环体外捕获这个异常，跳出循环
            raise BreakException()
        elif isinstance(node, LoopNode):
            self.evaluate_loop(node)
        # for in 循环解析
        elif isinstance(node, ForInNode):
            return self.evaluate_for_in(node)

        # for(idx: 1..10){}
        elif isinstance(node, ForRangeNumberNode):
            return self.evaluate_for_range_number(node)

            # 函数方面
        elif isinstance(node, FunctionDeclarationNode):
            # 函数声明，不做任何事情
            return self.evaluate_function_declaration(node)

        elif isinstance(node, FunctionCallNode):
            # print("env: ", self.environment)
            return self.evaluate_function_call(node)

        elif isinstance(node, ReturnNode):
            # return self.evaluate(node.value) # 原来的代码
            return self.evaluate(node.value)  # 返回结果

        # 列表索引解析
        elif isinstance(node, ListIndexNode):
            return self.evaluate_list_index(node)

        # 多维索引节点
        elif isinstance(node, MultiListIndexNode):
            return self.evaluate_multi_list_index(node)

        elif isinstance(node, ObjectIndexNode):
            return self.evaluate_object_index(node)

        # 引入包
        elif isinstance(node, ImportModuleNode):
            # 将包里面的都行都加载到环境变量中
            return self.import_module(node)
        # 包的声明
        elif isinstance(node, PackageDeclarationNode):
            return self.evaluate_package_declaration(node)


        # 类声明解析
        elif isinstance(node, ClassDeclarationNode):
            return self.evaluate_class_declaration(node)

        elif isinstance(node, NewObjectNode):
            return self.evaluate_new_object_expr(node)

        # 方法调用解析  p->show();
        elif isinstance(node, MethodCallNode):
            # 能不能再MethodNode里面加个属性, 记录instance的类型，
            # 比如dict, list, str, 这样在调用方法的时候，就可以根据类型进行调用
            try:
                # 看看是不是实例进行方法调用
                return self.evaluate_method_call(node)
            except NameError as e:
                # 如果发生了NameError,可能就是基本数据类型进行方法的调用
                return self.execute_by_instance_type(node)

        # 类内部方法调用解析 this.xxx();
        if isinstance(node, CallClassInnerMethod):
            return self.evaluate_call_class_inner_method(node)





        elif isinstance(node, GetMemberNode):
            return self.evaluate_get_instance_member(node)

        # 注释
        elif isinstance(node, CommentNode):
            # 注释不做任何事情
            pass

        # 解析  this.xxx();
        elif isinstance(node, CallClassInnerMethod):
            return self.evaluate_call_class_inner_method(node)

        # let z = if(true) x : y; 这样的表达式（注意不是语句）
        elif isinstance(node, IfExprNode):
            return self.evaluate_if_expr(node)


        # match表达式解析
        # let z = match(x) {
        #     case 1: 'One',
        #     case 2: 'Two',
        #     case 3: 'Three'
        # };
        elif isinstance(node, MatchExprNode):
            return self.evaluate_match_expr(node)

        # switch语句
        elif isinstance(node, SwitchNode):
            self.evaluate_switch_statement(node)

        # 解构赋值节点
        elif isinstance(node, DecontructAssignNode):
            return self.evaluate_decontruct_assign(node)

        # 列表解构赋值 解构列表赋值, 比如 let [a, _,b] = [1, 2,3];
        elif isinstance(node, ListDeconstructAssignNode):
            return self.evaluate_list_deconstruct_assign(node)

        # 接口定义
        elif isinstance(node, InterfaceNode):
            self.evaluate_interface_declaration(node)

        # try catch finally
        elif isinstance(node, TryCatchFinallyNode):
            return self.evaluate_try_catch_finally(node)

        # inc  id++;
        elif isinstance(node, IncrementNode):
            return self.evaluate_increment(node)

        # dec id--;
        elif isinstance(node, DecrementNode):
            return self.evaluate_decrement(node)
        # setNode
        elif isinstance(node, SetNode):
            return self.evaluate_set_node(node)

        # StructDeclarationNode
        elif isinstance(node, StructDeclarationNode):
            return self.evaluate_struct_declaration(node)

        # let z= Point{x:1,y:2};
        elif isinstance(node, StructAssignNode):
            return self.evaluate_struct_assign(node)

        # StructAccessNode 访问结构体的属性  比如: p::x
        elif isinstance(node, StructAccessNode):
            return self.evaluate_struct_access(node)
        # EnumDeclarationNode
        elif isinstance(node, EnumDeclarationNode):
            return self.evaluate_enum_declaration(node)

        # EnumAccessNode
        elif isinstance(node, EnumAccessNode):
            return self.evaluate_enum_access(node)

        # do while
        elif isinstance(node, DoWhileNode):
            return self.evaluate_do_while(node)

        # ListGeneratorNode
        elif isinstance(node, ListGeneratorNode):
            return self.evaluate_list_generator(node)

        # abs
        elif isinstance(node, AbsNode):
            val = self.evaluate(node.expr)
            return abs(val)

        # SerialCall
        elif isinstance(node, SerialCall):
            return self.evaluate_serial_call(node)


        # += -=系列
        elif isinstance(node, PlusAssignNode):
            return self.evaluate_plus_assign(node)
        # -=
        elif isinstance(node, MinusAssignNode):
             return self.evaluate_minus_assign(node)

        # *=
        elif isinstance(node,MultiplyAssignNode):
            return self.evaluate_multiply_assign(node)

        # /=
        elif isinstance(node,DivideAssignNode):
            return self.evaluate_divide_assign(node)


        else:
            raise TypeError(f"Unexpected node type: {type(node)}")


    def evaluate_divide_assign(self, node: DivideAssignNode):
        """
            实现 /= 系列
        """
        var_name = node.var_name
        div_val = self.evaluate(node.div_val)
        self.environment[var_name] /= div_val
        return None

    def evaluate_multiply_assign(self, node: MultiplyAssignNode):
        """
            实现 *= 系列
        """
        var_name = node.var_name
        mul_val = self.evaluate(node.mul_val)
        self.environment[var_name] *= mul_val
        return None

    def evaluate_minus_assign(self, node: MinusAssignNode):
        """
            实现 -= 系列
        """
        var_name = node.var_name
        dec_val = self.evaluate(node.dec_val)
        self.environment[var_name] -= dec_val
        return None


    def evaluate_plus_assign(self, node: PlusAssignNode):
        """
            实现 += 系列
        """
        var_name = node.var_name
        inc_val = self.evaluate(node.inc_val)
        self.environment[var_name] += inc_val
        return None


    def evaluate_serial_call(self, node: SerialCall):
        """
            实现串行调用
        """
        # 使用字面量进行连续调用
        #======================字面量调用方法 ===========================
        # ""->lower()->split()这样 字面量调用方法
        if node.caller == "anonymous":
            self.environment[node.caller] = self.evaluate(node.extra)
            #=================================================
            caller_value_copy = self.environment[node.caller]

            # 遍历方法列表，执行方法，并将结果保存到caller变量中
            for method in node.methods_list:
                # 下一个方法获得上一个方法的结果作为参数
                method.extra = self.environment[node.caller]
                self.environment[node.caller] = self.execute_by_instance_type(method)
            # 最终的结果
            cal_result = self.environment[node.caller]

            # 恢复原值
            self.environment[node.caller] = caller_value_copy

            # ======================字面量调用方法 ===========================
            # 删除anonymous
            if node.caller == "anonymous":
                del self.environment[node.caller]
            # ======================字面量调用方法 ===========================

            return cal_result

        # 使用变量进行连续调用
        else:
            # 先将caller的值保存起来
            caller_value_copy = self.environment[node.caller]

            # 遍历方法列表，执行方法，并将结果保存到caller变量中
            for method in node.methods_list:
                # print("method = ", method)
                self.environment[node.caller] = self.execute_by_instance_type(method)
                # print("本轮调用结果: ", self.environment[node.caller])

            # 最终的结果
            cal_result = self.environment[node.caller]

            # 恢复原值
            self.environment[node.caller] = caller_value_copy
            return cal_result

    def evaluate_list_generator(self, node: ListGeneratorNode):
        """
            实现列表生成器
        """
        pre_env = self.environment.copy()

        start = self.evaluate(node.start)
        end = self.evaluate(node.end)
        step = self.evaluate(node.step)

        # 返回的列表
        gen_list = []

        self.environment[f"{node.iter_name}"] = start

        # 左closed, right closed
        for i in range(start, end + 1, step):
            # print("i = ", i)
            gen_list.append(self.evaluate(node.gen_expr))
            if end > start:
                self.environment[f"{node.iter_name}"] = i + step
            else:
                self.environment[f"{node.iter_name}"] = i - step

        # print("gen_list = ", gen_list)
        self.environment = pre_env.copy()
        return gen_list

    def evaluate_do_while(self, node: DoWhileNode):
        """
            实现 do while 循环
        """

        for statement in node.body:
            self.evaluate(statement)
        cond = self.evaluate(node.condition)
        while cond:
            for statement in node.body:
                self.evaluate(statement)
            cond = self.evaluate(node.condition)

    def execute_by_instance_type(self, node: MethodCallNode):
        """
            根据实例的类型，调用相应的方法
        """
        print(node.extra)

        if node.instance_name == "anonymous":
            self.environment[node.instance_name] = self.evaluate(node.extra)

        var_value = self.environment[node.instance_name]
        # print("当前数据类型是: ", type(var_value))

        # 根据数据类型进行对应方法的调用，也就是说，这样存在一个对类型的隐士判断
        if isinstance(var_value, str):
            # print("str 实例")
            val  =  self.evaluate_string_type_method_call(node)
            del self.environment[node.instance_name]
            return val

        if isinstance(var_value, list):
            val =  self.evaluate_list_type_method_call(node)
            del self.environment[node.instance_name]
            return val

        if isinstance(var_value, dict):
            val =  self.evaluate_dict_type_method_call(node)
            del self.environment[node.instance_name]
            return val

        if isinstance(var_value, set):
            val =  self.evaluate_set_type_method_call(node)
            del self.environment[node.instance_name]
            return val

    def evaluate_set_type_method_call(self, node: MethodCallNode):
        """
            调用set的方法
        """
        var_name = node.instance_name
        method_name = node.method_name
        arguments = [self.evaluate(arg) for arg in node.arguments]

        # 获取参数的值
        if method_name == "add":
            try:
                for arg in arguments:
                    self.environment[var_name].add(arg)
                return True
            except:
                return False
        if method_name == "remove":
            try:
                self.environment[var_name].remove(arguments[0])
                return True
            except:
                return False
        if method_name == "clear":
            self.environment[var_name].clear()
            return True
        if method_name == "size":
            return len(self.environment[var_name])
        if method_name == "contains":
            return arguments[0] in self.environment[var_name]

        # =======集合上的方法=============
        # s->isSubset( z2): bool
        # isSuperset(): bool
        # union(): Set
        # intersection(): Set
        # difference(): Set
        if method_name == "isSubset":
            return set(self.environment[var_name]).issubset(arguments[0])
        if method_name == "isSuperset":
            return set(self.environment[var_name]).issuperset(arguments[0])
        if method_name == "union":
            return set(self.environment[var_name]).union(arguments[0])
        if method_name == "intersection":
            return set(self.environment[var_name]).intersection(arguments[0])
        if method_name == "difference":
            return set(self.environment[var_name]).difference(arguments[0])

    def evaluate_dict_type_method_call(self, node: MethodCallNode):
        """
            调用字典的方法
        """
        var_name = node.instance_name
        method_name = node.method_name
        # 获取参数的值
        arguments = [self.evaluate(arg) for arg in node.arguments]
        # print("======================================")
        # print("变量名称: ", var_name)
        # print("方法每次: ", method_name)
        # print("参数: ", arguments)
        # print("==========")
        if method_name == "getKeys":
            return list(self.environment[var_name].keys())
        if method_name == "getValues":
            return list(self.environment[var_name].values())

        if method_name == "getValue":
            return self.environment[var_name].get(arguments[0])

        # 通过key 删除元素
        if method_name == "deleteItem":
            return self.environment[var_name].pop(arguments[0])

        if method_name == "update":
            self.environment[var_name].update(arguments[0])
            return None

        if method_name == "clear":
            self.environment[var_name].clear()
            return None

        # 返回嵌套的list 比如： [['name', 'Alice'], ['age', 20]]
        if method_name == "getItems":
            return list([list(item) for item in self.environment[var_name].items()])

        if method_name == "hasKey":
            return arguments[0] in self.environment[var_name]

    def evaluate_string_type_method_call(self, node: MethodCallNode):
        """
            调用字符串的方法
        """
        var_name = node.instance_name
        method_name = node.method_name
        # 获取参数的值
        arguments = [self.evaluate(arg) for arg in node.arguments]
        # print("======================================")
        # print("变量名称: ", var_name)
        # print("方法每次: ", method_name)
        # print("参数: ", arguments)
        # print("======================================")

        # 常见方法
        if method_name == "upper":
            self.environment[var_name] = self.environment[var_name].upper()
            return self.environment[var_name]
        if method_name == "lower":
            self.environment[var_name] = self.environment[var_name].lower()
            return self.environment[var_name]
        if method_name == "startsWith":
            return self.environment[var_name].startswith(arguments[0])
        if method_name == "endsWith":
            return self.environment[var_name].endswith(arguments[0])
        if method_name == "capitalize":
            self.environment[var_name] = self.environment[var_name].capitalize()
            return self.environment[var_name]
        if method_name == "swapcase":
            self.environment[var_name] = self.environment[var_name].swapcase()
            return self.environment[var_name]
        # 分割与连接
        if method_name == "split":
            separator = arguments[0]
            return self.environment[var_name].split(separator)
        if method_name == "strip":
            self.environment[var_name] = self.environment[var_name].strip()
            return self.environment[var_name]
        # 类型检查
        if method_name == "isAlpha":
            return self.environment[var_name].isalpha()
        if method_name == "isDigit":
            return self.environment[var_name].isdigit()
        if method_name == "isAlphaNum":
            return self.environment[var_name].isalnum()
        if method_name == "isSpace":
            return self.environment[var_name].isspace()
        if method_name == "isLower":
            return self.environment[var_name].islower()
        if method_name == "isUpper":
            return self.environment[var_name].isupper()
        if method_name == "concat":  # 连接字符串
            self.environment[var_name] = self.environment[var_name] + arguments[0]
            return self.environment[var_name]
        if method_name == "charAt":
            return self.environment[var_name][arguments[0]]

        if method_name == "indexOf":
            return self.environment[var_name].find(arguments[0])

        if method_name == "contains":
            return arguments[0] in self.environment[var_name]

    def evaluate_list_type_method_call(self, node: MethodCallNode):

        """
            改进：
                记录每个数据的初始类型（类型推断），然后在调用方法的时候
                根据类型进行调用

            调用基本数据类型的方法，比如字符串的split()方法
        """
        pass
        # print("得到的节点信息: ", node)
        var_name = node.instance_name
        # print("var_name==================> ", var_name)

        method_name = node.method_name
        # print("arguments==================> ", node.arguments)

        arguments = [self.evaluate(arg) for arg in node.arguments]
        # print("======================================")
        # print("var_name: ", var_name)
        # print("method_name: ", method_name)
        # print("arguments: ", arguments)
        # print("======================================")

        # 列表的append方法
        if method_name == "append":
            # 列表的append方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only append to list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的追加
            for arg in arguments:
                value.append(arg)
            return value

        # insert方法
        if method_name == "insert":
            # 列表的insert方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only insert to list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的插入
            index = arguments[0]
            for arg in arguments[1:]:
                value.insert(index, arg)
                index += 1
            return value

        # 删除成功，返回True，否则返回False
        # remove(元素),
        if method_name == "remove":
            # 列表的remove方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only remove from list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的删除
            for arg in arguments:
                value.remove(arg)
            return value

        # 删除指定位置的元素
        # removeAt(索引)
        if method_name == "removeAt":
            # 列表的pop方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only removeAt from list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的删除
            index = arguments[0]
            value.pop(index)
            return value
        # 查找元素的索引
        if method_name == "indexOf":
            # 列表的index方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only index list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的索引
            arg = arguments[0]

            # 列表中不存在该元素，返回-1
            if arg not in value:
                return -1
            return value.index(arg)

        # 计数: count(元素)
        if method_name == "count":
            # 列表的count方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only count list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的计数
            arg = arguments[0]
            return value.count(arg)

        # reverse()方法
        if method_name == "reverse":
            # 列表的reverse方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only reverse list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的反转
            value.reverse()
            return value

        # clear()方法
        if method_name == "clear":
            # 列表的clear方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only clear list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的清空
            value.clear()
            return value

        # 判断列表是否包含某个元素
        if method_name == "has":
            # list的for in
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only has list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的判断是否包含
            arg = arguments[0]
            return arg in value

        # set 设置列表某个索引的值
        if method_name == "setAt":
            # 列表的set方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            xlist = self.environment[var_name]

            if type(xlist) != list:
                raise TypeError(f"can only set list, but got {type(xlist)}")
            # 支持任意数量和任意类型类型的数据的设置
            index = arguments[0]
            xlist[index] = arguments[1]

            return xlist
        # isEmpty()方法
        if method_name == "isEmpty":
            # 列表的isEmpty方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            if type(value) != list:
                raise TypeError(f"can only isEmpty list, but got {type(value)}")
            # 支持任意数量和任意类型类型的数据的判断是否为空
            return len(value) == 0
        # length()方法
        if method_name == "length":
            # 列表的length方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            value = self.environment[var_name]
            # 支持任意数量和任意类型类型的数据的长度
            # print("len = ", len(value))
            return len(value)

        # combine, 类似join方法
        if method_name == "combine":
            # 列表的combine方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            xlist = self.environment[var_name]
            if type(xlist) != list:
                raise TypeError(f"can only combine list, but got {type(xlist)}")
            # 支持任意数量和任意类型类型的数据的合并
            separator = arguments[0]

            # 将每个元素转化为字符串
            xlist = [str(x) for x in xlist]

            return separator.join(xlist)

        # FunctionDeclarationNode
        # filter()方法
        if method_name == "filter":
            # 列表的filter方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            xlist = self.environment[var_name]
            if type(xlist) != list:
                raise TypeError(f"can only filter list, but got {type(xlist)}")
            # 支持任意数量和任意类型类型的数据的过滤
            filter_func_dict = arguments[0]
            return self.filter_server(filter_func_dict, xlist)

        # map()方法
        if method_name == "map":
            # 列表的map方法
            if var_name not in self.environment:
                raise NameError(f"name '{var_name}' is not defined")
            xlist = self.environment[var_name]
            if type(xlist) != list:
                raise TypeError(f"can only map list, but got {type(xlist)}")
            # 支持任意数量和任意类型类型的数据的映射
            map_func_dict = arguments[0]
            return self.map_server(map_func_dict, xlist)
        # ===============set类型的方法=======================

    def map_server(self, map_func, xlist):
        """
            服务map函数的, 可以服务map等函数
            map_func_dict: 匿名函数，用来map的条件
            xlist: 待映射的列表
        """
        func_dict = map_func  # 值居然是None
        # print("predicate_param_name: ", func_dict)  # None

        predicate_param_name = func_dict['args'][0]  # 形参名称,比如['x']

        body_statements = func_dict['body']  # 函数体

        local_scope = {}

        previous_environment = self.environment.copy()

        # filtered的结果
        result = []
        for element in xlist:
            # 没迭代一个元素就更新一次环境
            local_scope[predicate_param_name] = element
            # 保存当前的环境，以便函数执行完后恢复
            # 更新环境为局部作用域, 并执行函数体, 这样做，内部函数可以访问外界的变量
            self.environment.update(local_scope)
            # ==================执行方法体=============================
            for statement in body_statements:
                mapped_value = self.evaluate(statement)
                if isinstance(statement, ReturnNode):
                    # 如果符合predicate条件，则添加到结果列表中
                    result.append(mapped_value)
        # ========================恢复环境===================
        # 恢复之前的环境
        self.environment = previous_environment
        # print("result: ", result)
        return result

    def filter_server(self, filter_predicate, xlist):
        """
            服务filter函数的, 可以服务map等函数
            filter_predicate: 匿名函数，用来filter的条件
            xlist: 待过滤的列表
        """
        # func_dict的样子: {
        #   args': ['x'],
        #   'body': [ReturnNode(value=BinaryOpNode(left=VariableNode(value=x), op=GT, right=NumberNode(value=1)))]

        func_dict = filter_predicate  # 值居然是None
        predicate_param_name = func_dict['args'][0]  # 形参名称,比如['x']
        body_statements = func_dict['body']  # 函数体

        local_scope = {}

        previous_environment = self.environment.copy()

        # filtered的结果
        result = []
        for element in xlist:
            # 没迭代一个元素就更新一次环境
            local_scope[predicate_param_name] = element
            # 保存当前的环境，以便函数执行完后恢复
            # 更新环境为局部作用域, 并执行函数体, 这样做，内部函数可以访问外界的变量
            self.environment.update(local_scope)
            # ==================执行方法体=============================
            for statement in body_statements:
                return_value = self.evaluate(statement)
                if isinstance(statement, ReturnNode):
                    # 如果符合predicate条件，则添加到结果列表中
                    if return_value:
                        result.append(element)
        # ========================恢复环境===================
        # 恢复之前的环境
        self.environment = previous_environment
        # print("result: ", result)
        return result

    def evaluate_enum_access(self, node: EnumAccessNode):
        """
            let x = enum::Color.Red;
            EnumAccessNode(name=Color, value=Red)
            task:
                检查访问的属性是否存在于枚举类中，
                1，存在；返回值
                2，不存在；raise NameError
        """
        # print("node: ", node)
        # print("env: ", self.environment["enums"])
        # 检擦枚举类是否存在
        if node.enum_name not in self.environment["enums"]:
            raise NameError(f"Enum {node.enum_name} not found!")
        if node.enum_property not in self.environment["enums"][node.enum_name]:
            raise NameError(f"Enum property {node.enum_property} not found in {node.enum_name}!")
        return node.enum_property

    def evaluate_enum_declaration(self, node: EnumDeclarationNode):
        """
            枚举类型定义
        """
        # 枚举类型定义
        # print("node: ", node)
        enum_values = []
        for enum_name in node.enum_values:
            enum_values.append(enum_name)
        self.environment["enums"][node.enum_name] = enum_values
        # print(f"Enum {node.enum_name} declared.")
        # print("env: ", self.environment)
        return None

    def evaluate_struct_access(self, node: StructAccessNode):
        """
             访问结构体的属性
             比如:
                p::x
        """
        if node.struct_instance_name not in self.environment:
            raise NameError(f"struct instance {node.struct_instance_name} not found!")
        # print("StructAccessNode =====> ", node)
        struct_dict = self.environment[node.struct_instance_name]
        # struct_dict 比如: {'type': 'struct', 'name': 'Point', 'value': {'x': 1, 'y': 2}}

        # 访问不存在的属性
        # print("fieldname: ", node.field_name)
        if node.field_name not in struct_dict["value"]:
            return False
        return struct_dict["value"][node.field_name]

    def evaluate_struct_assign(self, node: StructAssignNode):
        result = {
            "type": "struct",
            "name": f"{node.struct_name}",
            "value": {}
        }
        for field_name in node.struct_fields_values:
            field_value = self.evaluate(node.struct_fields_values[field_name])
            result["value"][field_name] = field_value
        return result

    def evaluate_struct_declaration(self, node: StructDeclarationNode):
        """
            将结构体的名称放到env中，以便后续使用

        :param node:
        :return:
        """
        if node.struct_name in self.environment["structs"]:
            raise NameError(f"Struct {node.struct_name} already exists!")
        self.environment["structs"][node.struct_name] = node.fields
        # print(f"Struct {node.struct_name} declared.")
        # print("env: ", self.environment)
        return None

    def evaluate_set_node(self, node: SetNode):
        # 借用python的set类型创建set类型
        set_result = []
        for element in node.set_values:
            r = self.evaluate(element)
            set_result.append(r)
        return set(set_result)

    def evaluate_decrement(self, node: DecrementNode):
        # 处理自减运算符
        var_name = node.var_name
        if var_name not in self.environment:
            raise NameError(f"name '{var_name}' is not defined")
        value = self.environment[var_name]
        if type(value) != int:
            raise TypeError(f"can only decrement integer, but got {type(value)}")
        self.environment[var_name] = value - 1
        # return value - 1

    def evaluate_increment(self, node: IncrementNode):
        # 处理自增运算符
        var_name = node.var_name
        if var_name not in self.environment:
            raise NameError(f"name '{var_name}' is not defined")
        value = self.environment[var_name]
        if type(value) != int:
            raise TypeError(f"can only increment integer, but got {type(value)}")
        self.environment[var_name] = value + 1
        # return value + 1

    def evaluate_try_catch_finally(self, node: TryCatchFinallyNode):
        # 解析try catch finally语句
        """
            核心科技:
                当捕获到异常时，你需要将Python的异常转换为你的语言中对应的异常类型。


        """
        # 定义异常类型映射
        exception_mapping = {
            ZeroDivisionError: "ZeroDivisionError",
            ValueError: "ValueError",
            TypeError: "TypeError",
            NameError: "NameError",
            IndexError: "IndexError",
            KeyError: "KeyError",
            AttributeError: "AttributeError",
            FileNotFoundError: "FileNotFoundError",
            IOError: "IOError",
            ImportError: "ImportError",
            SyntaxError: "SyntaxError",
            IndentationError: "IndentationError",
            OverflowError: "OverflowError",
            AssertionError: "AssertionError",
            RuntimeError: "RuntimeError",
            MemoryError: "MemoryError",
            RecursionError: "RecursionError",
            NotImplementedError: "NotImplementedError",
            PermissionError: "PermissionError",
            TimeoutError: "TimeoutError",
        }

        # 定义打印红色字体的函数
        # def print_red(text):
        #     print("\033[91m{}\033[0m".format(text))

        try:
            for statement in node.try_block:
                self.evaluate(statement)
        except Exception as e:

            # 异常映射
            # 将Python异常转换为你的语言的异常
            caught_exception = exception_mapping.get(type(e), "Exception")
            # print_red(f"Caught Exception: {e}")
            # 捕获异常  catch_block = [{err_type: [stmt1, stmt2, stmt3] }]
            for catch_dict in node.catch_block:
                for err_type in catch_dict:
                    # 遍历catch_block字典，找到对应的异常类型
                    if err_type == caught_exception:
                        for stmt in catch_dict[err_type]:
                            self.evaluate(stmt)
        finally:
            # 没有异常，执行finally语句
            for finally_statement in node.finally_block:
                self.evaluate(finally_statement)

    def evaluate_for_range_number(self, node: ForRangeNumberNode):
        # 两种类型： 1，递增 2，递减  如果传进来的参数是小说，range方法自己会报错

        # for(idx: 1..10){}
        # 解析for循环语句
        # 先计算表达式的值
        start_value = self.evaluate(node.start_num)
        end_value = self.evaluate(node.end_num)

        # 判断是不是小数
        if type(start_value) == float:
            raise TypeError(f"only support integer, but got float {start_value}")
        if type(end_value) == float:
            raise TypeError(f"only support integer, but got float {end_value}")

        # 保存之前的环境变量
        previous_environment = self.environment.copy()

        # 设置初始变量
        self.environment[node.var_name] = -100

        # for(idx: 1..10){} 递增类型
        if start_value < end_value:
            # 遍历每个元素
            for i in range(start_value, end_value + 1):
                # print("i = ",i)
                self.environment[node.var_name] = i
                try:
                    for statement in node.body:
                        self.evaluate(statement)
                except BreakException:
                    break

        # for(idx: 10..1){} 倒退类型
        if start_value > end_value:
            # 遍历每个元素
            for i in range(start_value, end_value - 1, -1):
                # print("i = ",i)
                self.environment[node.var_name] = i
                try:
                    for statement in node.body:
                        self.evaluate(statement)
                except BreakException:
                    break

        # 还原环境变量
        self.environment = previous_environment.copy()

    def evaluate_interface_declaration(self, node: InterfaceNode):
        # 处理接口定义: 将接口加入到environment中, 类实现的时候要用到
        # {"接口名称":[方法名称1,方法名称2,...]}
        self.environment["interfaces"][node.interface_name] = node.methods

    def evaluate_list_deconstruct_assign(self, node: ListDeconstructAssignNode):
        # 解构列表赋值, 比如 let [a, _,b] = [1, 2,3];

        # node.vars_list 是一个dict，里面是变量名
        for var_name in node.vars_list:
            # 判断变量是否已经存在于环境中
            if var_name in self.environment:
                raise NameError(f"Variable '{var_name}' already exists!")
            # node.vars_list的样子： {”a“:index1, “b”:index2}
            index = node.vars_list[var_name]  # 获取变量名称对应的索引
            if index >= len(self.evaluate(node.list_obj)):
                raise IndexError(f"Index {index} out of range for list of length {len(self.evaluate(node.list_obj))}")
            value = self.evaluate(node.list_obj)[index]
            # 将值放到环境中
            self.environment[var_name] = value

    def evaluate_decontruct_assign(self, node: DecontructAssignNode):
        # 解构赋值  let {a, b} = {"a": 1, "b": 2}; 或者 let {c,d} = dictObj;
        # 否则，直接求值

        # 判断变量是否已经存在于环境中
        for var in node.vars_list:
            if var in self.environment:
                raise NameError(f"Variable '{var}' already exists!")

        for var_name in node.vars_list:
            key_exist = False
            # print(var_name)
            for key in self.evaluate(node.dict_obj):
                if key == var_name:
                    key_exist = True
                    self.environment[var_name] = self.evaluate(node.dict_obj)[key]
                    break
            if not key_exist:
                raise NameError(f"Key '{var_name}' not found in the right object.")

    def evaluate_switch_statement(self, node: SwitchNode):
        """
            解析switch语句
            switch(x){
                case(x){

                }
                case(y){

                }
                default{

                }
            }
        """
        # node.cases是一个字典，key是case的表达式，value是list装的一系列的语句

        # 先计算表达式的值
        condition_value = self.evaluate(node.expr)
        # print("condition_value: ", condition_value)
        for case in node.cases:  # case是xxNode()，需要解析
            # print("case: ", self.evaluate(case))
            if self.evaluate(case) == condition_value:
                for statement in node.cases[case]:
                    self.evaluate(statement)
                break
            elif self.evaluate(case) == "default":
                for statement in node.cases[case]:
                    self.evaluate(statement)
                break

    def evaluate_match_expr(self, node: MatchExprNode):
        # 解析match表达式
        # 比如:  {1: 'One', 2: 'Two', 3: 'Three'}
        case_val_dict = {}
        condition_value = self.evaluate(node.expr)
        # print("condition_value: ", condition_value)
        for case in node.case_value_dict:
            case_val_dict[self.evaluate(case)] = self.evaluate(node.case_value_dict[case])

        # 在处理后的dict中查找匹配的case
        for case in case_val_dict:
            if case == condition_value:
                return case_val_dict[case]

        # 没有匹配的case，返回else
        return self.evaluate(node.else_expr)

    def evaluate_if_expr(self, node: IfExprNode):
        """
            解析if表达式
            先计算条件表达式，然后根据条件表达式的结果，决定执行哪个分支
            注意：if表达式的返回值是表达式的值，而不是语句的值
        """
        # 计算条件表达式
        condition_value = self.evaluate(node.condition)
        # print("condition_value: ", condition_value)
        if type(condition_value) != bool:
            raise TypeError(f"Condition expression must be a boolean, but got {type(condition_value)}")

        # 根据条件表达式的结果，决定执行哪个分支
        if condition_value:
            return self.evaluate(node.expr_if_true)
        else:
            return self.evaluate(node.expr_if_false)

    def evaluate_call_class_inner_method(self, node: CallClassInnerMethod):
        """
                解析类内部方法调用
            在调用实例的方法时，记录caller, 也就是调用方法的实例，在方法内部如果遇到this，
            就知道了调用者是谁，从而找到调用者的实例，然后从实例中获取方法的定义，并调用方法

            特别地，在执行方法的，时候，每执行一条语句，就需要更新实例字段，
            因为可能某一条语句就直接更新了实例字段，所以需要更新实例字段，如此，方法内部的方法想要访问才能
            得到最新的值
        """
        # 记录当前的对象，用于this的解析，也就是确定this指向的对象
        instance_name = self.current_object
        # print("current_object: ", self.current_object)
        # 方法名称
        method_name = node.method_name
        # 调用方法的参数
        args_pass_in = [self.evaluate(arg) for arg in node.arguments]

        # 找到instance_name的实例
        instance_dict = self.environment["instances"][instance_name]
        # print(f"instance_dict: {instance_name}的定义  ", instance_dict)

        # 找到方法的定义
        method_dict = instance_dict["methods"][method_name]
        # print(f"method_dict: {method_name}的定义  ", method_dict)

        # 保存旧环境
        old_env = self.environment

        # 创建新环境，包含实例字段和方法参数
        self.environment = {
            **old_env,  # 包含全局环境,是指可以访问类外面的变量
            **instance_dict['fields'],
            **dict(zip(method_dict['args'], args_pass_in)),
            # "constants": []  # 记录声明的常量
        }

        # 执行方法体
        result = None
        for statement in method_dict['body']:
            result = self.evaluate(statement)
            # 更新实例字段————每每执行一条语句之后，因为可能某一条语句就直接更新了实例字段，所以需要更新实例字段
            for field_name in instance_dict['fields']:
                if field_name in self.environment:
                    instance_dict['fields'][field_name] = self.environment[field_name]

        # 恢复旧环境
        self.environment = old_env

        return result

    def evaluate_get_instance_member(self, node: GetMemberNode):
        """
        GetMemberNode
             self.instance_name = instance_name
             self.member_name = member_name
        """

        # ==============静态属性========================================
        # 判断是不是在访问类的static属性
        if node.instance_or_class_name in self.environment["objects"]:
            # print("md 一个类啊")
            return self.environment["objects"][node.instance_or_class_name]["static_fields"][node.member_name]
        # ==============静态属性========================================

        # 将instance的字段对应的值返回
        # instance_name = node.instance_name
        instance_name = node.instance_or_class_name
        field_name = node.member_name
        instance_dict = self.environment["instances"][instance_name]
        # 判断是否存在这个字段
        if field_name not in instance_dict["fields"]:
            raise NameError(f"Field {field_name} not found in instance {instance_name}")

        # 判断属性是否是public
        if field_name[0].islower():
            raise NameError(f"Field {field_name} is not public (no such field)")

        return instance_dict["fields"][field_name]

    def evaluate_method_call(self, node: MethodCallNode):
        """
            解析方法调用
            先找到方法的定义，然后调用方法

            来源：
                修改的不是instances里面的变量

            version 1:
                对实例属性的修改不会同步到实例字段中
            version 2:
                对实例属性的修改会同步到实例字段中
            node.arguments
                    实参
        """
        # print("env test: ", self.environment)
        # print("node info: ", node)

        # ====================version 2============================================

        caller = node.instance_name  # 记录调用者的名字
        self.current_object = caller  # 记录当前的对象，用于this的解析

        # ====================类调用方法开始============================================
        # 在环境中找到类的定义
        if caller in self.environment["objects"]:
            # print("哦吼，调用的是一个类")
            class_name = caller
            # 找到类的定义
            class_definition = self.environment["objects"][class_name]
            # 找到方法的定义
            method_name = node.method_name
            method_dict = class_definition["methods"][method_name]
            # 调用方法
            args_pass_in = [self.evaluate(arg) for arg in node.arguments]
            # 保存旧环境
            old_env = self.environment
            # 创建新环境，包含方法参数
            self.environment = {
                **old_env,  # 包含全局环境,是指可以访问类外面的变量
                **dict(zip(method_dict['args'], args_pass_in)),
                # "constants": []  # 记录声明的常量
            }
            # 执行方法体
            result = None
            for statement in method_dict['body']:
                result = self.evaluate(statement)
            # 恢复旧环境
            self.environment = old_env
            return result
        # ====================类调用方法结束============================================

        # print("caller: ", caller)
        method_name = node.method_name
        args_pass_in = [self.evaluate(arg) for arg in node.arguments]

        # 判断是不是private方法，如果是，拒绝访问
        if method_name[0].islower():
            raise NameError(f"Method {caller}->{method_name}() is not public. Access denied.")

        try:
            # 尝试找到该对象
            # 实例对象的所有东西
            instance_dict = self.environment["instances"][caller]
            # 对象的所有方法
            method_dict = instance_dict["methods"][method_name]
        except KeyError:
            # 找不到该对象
            raise NameError(f"Object {caller} not found.")

        # 保存旧环境
        old_env = self.environment

        # 创建新环境，包含实例字段和方法参数
        self.environment = {
            **old_env,  # 包含全局环境,是指可以访问类外面的变量
            **instance_dict['fields'],
            **dict(zip(method_dict['args'], args_pass_in)),
            # "constants": []  # 记录声明的常量
        }
        #
        # 执行方法体
        result = None
        for statement in method_dict['body']:
            result = self.evaluate(statement)
            # if isinstance(statement,ReturnNode):
            #     break
            # 更新实例字段————每每执行一条语句之后，因为可能某一条语句就直接更新了实例字段，所以需要更新实例字段
            for field_name in instance_dict['fields']:
                if field_name in self.environment:
                    instance_dict['fields'][field_name] = self.environment[field_name]

        # 原先实例更新的版本，和上面的for在同一个level
        # for field_name in instance_dict['fields']:
        #     if field_name in self.environment:
        #         instance_dict['fields'][field_name] = self.environment[field_name]

        # 恢复旧环境
        self.environment = old_env

        return result
        # ====================version 2========end====================================

    def evaluate_new_object_expr(self, node: NewObjectNode):
        """
            从environment中获取类定义，就是复制属性、方法、及其init
        """
        # print("node: ", node)

        # 用于存储实例化后的对象
        return_instance = {
            "fields": {},
            "methods": {},
            "init": {},
            "parent_name": node.class_name,
            "fields_annotations": {},
        }
        class_name = node.class_name
        # print("类名: ", class_name)

        # 先获取类定义, 也就是类的原型
        original_class_definition = self.environment["objects"][class_name]
        # print("original_class_definition: ", original_class_definition)

        # 处理fields
        for field_name in original_class_definition['fields']:
            field_value = original_class_definition['fields'][field_name]
            # 如果属性的首字母大写，则加入到新对象的属性中（看作publlic）,否则不加入 (继承public类型的属性)
            return_instance["fields"][field_name] = field_value
        # print("return_instance(处理prototype的fields后): ",return_instance)

        # 处理fields_annotations
        for field_name in original_class_definition['fields_annotations']:
            field_annotation = original_class_definition['fields_annotations'][field_name]
            return_instance["fields_annotations"][field_name] = field_annotation

        # 处理methods
        for method_name in original_class_definition['methods']:
            method_body = original_class_definition['methods'][method_name]['body']
            method_args = original_class_definition['methods'][method_name]['args']
            method_default_values = original_class_definition['methods'][method_name]['default_values']
            return_instance["methods"][method_name] = {
                # 函数注解
                "annotations": original_class_definition['methods'][method_name]["annotations"],
                "args": method_args,
                "body": method_body,
                "default_values": method_default_values,
            }
        # print("return_instance(处理prototype的methods后): ",return_instance)

        # 处理init
        if original_class_definition['init']:
            init_args = original_class_definition['init']['args']
            init_body = original_class_definition['init']['body']
            init_default_values = original_class_definition['init']['default_values']
            return_instance["init"] = {
                "args": init_args,
                "body": init_body,
                "default_values": init_default_values
            }
            # print("return_instance(处理prototype的init后): ",return_instance)
            # init内部有两类语句： 1，赋值语句(涉及的变量和fields中的名称一样，看作对属性的赋值)  2，其他语句（比如赋值、输出等）

            # 将传进来的参数赋值到 return_instance["fields"]里面去
            # print("\nreturn_instance['fields']: ",return_instance["fields"])
            # print("要初始化init_args的变量(及其顺序): ",init_args)
            # print("传进来的参数(node.arguments):",node.arguments)

            # 字段赋值  取出node.arguments的第一个参数，赋值给return_instance["fields"]中对应的字段
            # 处理 let 字段 = 值; 这样的语句
            # fields = list(return_instance["fields"].keys())
            # print("fields: ",fields)
            # for i in range(len(init_args)):
            #         field_name = fields[i]
            #         return_instance["fields"][field_name] = self.evaluate(node.arguments[i])
            # print("赋值后的return_instance['fields']: ",return_instance["fields"])

            # =============为了让init内部可以访问变量，需要设置新环境=====为了下面的for statement in init_body可以访问变量服务===============================
            # 记录旧环境
            old_env = self.environment
            self.environment = self.environment = {
                "constants": [],  # 记录声明的常量
                "objects": {},  # 导入的类和创建的对象
            }
            # 将传进来的参数放到新环境里面
            for i in range(len(node.arguments)):
                arg_name = init_args[i]  # 获取参数名称，从哪获取呢?
                arg_value = self.evaluate(node.arguments[i])  # 取出参数的值
                self.environment[arg_name] = arg_value
            # print("environment: ", self.environment)

            # =============为了让init内部可以访问变量，需要设置新环境====================================

            # 2, 处理非赋值语句
            for statement in init_body:
                # 再遇到赋值语句额时候发生错误，因为已经赋值过了，所以这里不再处理对字段的赋值语句
                if isinstance(statement, AssignmentNode) and statement.name in return_instance["fields"]:
                    return_instance["fields"][statement.name] = self.evaluate(statement.value)
                else:
                    self.evaluate(statement)  # 处理语句，比如函数调用、赋值语句等
            # 回复旧环境
            self.environment = old_env
        # print("return_instance最终: ", return_instance)

        # =======================处理对象调用方法===============================
        # 将 实例对象放到 environment 中
        self.environment["instances"][node.object_name] = return_instance
        # print("environment: ", self.environment)
        # ======================================================

        return return_instance

    def evaluate_class_declaration(self, node: ClassDeclarationNode):
        """
           解析类的声明
            引入类的机制和引入包的方法一致:
                environment中存放类的全部属性和方法，对于调用静态的方法，直接在environment中查找
                对于static类型的： 加入到environment中，形式是：类名.xxx
                对于非static类型的： 加入到environment中,形式是：实例.xxx
            类存储的形式：
            @@@self.environment:
            {
                'constants': [],
                'objects': {
                    'Person': {
                        'fields': {'name': 'Alice', 'Age': 25},
                        'methods': {
                            'hi': {'args': [], 'body': [], 'default_values': {}},
                            'SayHello': {'args': [], 'body': [FunctionCallNode(name=log, args=[NumberNode(value=1)], named_arg_values={})], 'default_values': {}}},
                        'init': {'args': [], 'body': [FunctionCallNode(name=log, args=[StringNode(value=init)], named_arg_values={})], 'default_values': {}}}}}
                    }
                }
            }

        """
        # print("当前的nodexxx: ", node)
        class_name = node.classname

        # class_dict表示当前解析的类
        class_dict = {
            'fields': {},
            'methods': {},
            'init': None,
            "static_fields": {},
            "static_methods": {},  # 静态方法
            "fields_annotations": {}
        }

        # print(" \n node---------------------> ", node,"\n")

        # ====================static 类型属性============================================
        for field_name in node.static_fields:
            # field_name = field.name
            field_value = self.evaluate(node.static_fields[field_name])
            # 这里的field_name是类名.field_name
            class_dict['static_fields'][field_name] = field_value
        # ====================static 类型属性============================================

        # ====================static 方法============================================
        for method_name in node.methods:
            # print("method_name: ", method_name)
            method_dict = node.methods[method_name]
            # 处理static方法
            if method_dict.is_static == True:
                # print("method_dict: ", method_dict)
                class_dict['static_methods'][method_name] = {
                    'args': method_dict.args,
                    'body': method_dict.body,
                    "default_values": method_dict.default_values
                }
        # ====================static 方法============================================

        # ===============处理字段的注解===========================
        for field_name in node.fields_annotations:
            annot = node.fields_annotations[
                field_name]  # 格式:  {'permission': StringNode(value=public), 'returnType': StringNode(value=string)}
            annot_return = {}  # 要返回的annotation
            for key in annot:
                annot_return[key] = self.evaluate(annot[key])
            class_dict['fields_annotations'][field_name] = annot_return
            # print("class_dict['fields_annotations'] : ", class_dict['fields_annotations'])

        # ===============处理字段的注解===========================

        # ==========================处理字段======================
        # field就是key
        for field_name in node.fields:
            # field_name = field.name
            field_value = self.evaluate(node.fields[field_name])
            class_dict['fields'][field_name] = field_value
        # fields的形式:  {'name': 'Alice', 'Age': 25}
        # print("fields: ", class_dict['fields'])

        # 处理方法
        for method_name in node.methods:
            # print("node.methods[method_name].annotations= =================> ", node.methods[method_name].annotations,
            #       "\n")

            class_dict['methods'][method_name] = {
                # 注解注解
                "annotations": node.methods[method_name].annotations,
                'args': node.methods[method_name].args,
                'body': node.methods[method_name].body,
                "default_values": node.methods[method_name].default_values,
            }
        # print("class_dict(methods): ", class_dict['methods'])
        # 处理初始化函数
        if node.init:
            class_dict['init'] = {
                'args': node.init.args,
                'body': node.init.body,
                "default_values": node.init.default_values,

            }
        # print("init: ", class_dict['init'])
        # 将类定义存储在环境中
        self.environment["objects"][class_name] = class_dict

        # print("class_dict: ", self.environment["objects"][class_name])

        # ==============extends========测试=========================================
        # 有一个问题, 初始类问题,
        # class_dict: {
        #       'fields': {'brand': 'Bulldog'},
        #       'methods': {'Bark': {'args': [], 'body': [
        #                 FunctionCallNode(name=log, args=[StringNode(value=dog is barking /)], named_arg_values={})],
        #                                                                   'default_values': {}}},
        #       'init': {'args': [], 'body': [FunctionCallNode(name=log, args=[StringNode(value=Dog init)],
        #                       named_arg_values = {})], 'default_values': {}},
        #       'static_fields': {}, 'static_methods': {}}
        def ifSubclassHasAttribute(subclass_name, attr):
            subclass_fields = self.environment["objects"][subclass_name]["fields"]
            for f in subclass_fields:
                if f == attr:
                    return True
            return False

        def ifSubclassHasMethod(subclass_name, check_method_name):
            subclass_methods_dict = self.environment["objects"][subclass_name]["methods"]
            for method in subclass_methods_dict:
                if method == check_method_name:
                    return True
            return False

        # ===========================处理继承===========================================
        if node.parent_name != "":
            # print("classname: ", class_name)  # Animal
            # print("此时的node: ", node)
            # print("父类: ", node.parent_name)
            # print("此时的环境: ", self.environment)
            print(type(node.parent_name))
            # print("父类： ", self.environment["objects"][node.parent_name])

            extended_fields = {}
            extended_methods = {}
            # 处理父类的fields
            for parent_field_name in self.environment["objects"][node.parent_name]["fields"]:
                # 继承public类型的属性（如果子类没有同名的属性）
                if parent_field_name[0].isupper() and not ifSubclassHasAttribute(node.classname, parent_field_name):
                    extended_fields[parent_field_name] = self.environment["objects"][node.parent_name]["fields"][
                        parent_field_name]
            print("extended_fields:", extended_fields)

            # 处理父类的methods
            for parent_method_name in self.environment["objects"][node.parent_name]["methods"]:
                # 继承public类型的属性
                if parent_method_name[0].isupper() and not ifSubclassHasMethod(node.classname, parent_method_name):
                    extended_methods[parent_method_name] = self.environment["objects"][node.parent_name]["methods"][
                        parent_method_name]
            print("extended_methods:", extended_methods)

            # ============关键一步==============================
            # 将方法和属性合并到class_dict中
            class_dict['fields'].update(extended_fields)
            class_dict['methods'].update(extended_methods)
            # print("class_dict(new): ", class_dict)
            # print("class_dict(fields): ", class_dict['fields'])
            # print("class_dict(methods): ", class_dict['methods'])
            # print("\n继承后的样子：\n")

            # for field_name in class_dict['fields']:
            # print("field_name: ", field_name)
            # for method_name in class_dict['methods']:
            #     print("method_name: ", method_name)
            # print("class_name: ", class_name)
            # ==============extends=================================================

            # 将类定义存储在环境中
            self.environment["objects"][class_name] = class_dict

        # ========================处理接口实现问题===============================
        # {'Drawable': ['Draw']}  => {接口名称：[方法列表]}
        # 处理方法: 判断类中有没有接口声明的方法，如果没有，报错!
        # node.interfaces表达式的是类自己要implements的接口列表
        # print("mynode: ", node.interfaces)
        # print("环境: ", self.environment)
        for interface_name in node.interfaces:
            # 先获取接口定义
            interface_list = self.environment["interfaces"][interface_name]
            # 遍历接口定义中的方法，判断类中是否有实现
            for method_name in interface_list:
                if method_name not in class_dict['methods']:
                    raise NotImplementedError(
                        f"Class '{class_name}' does not implement method '{method_name}' declared in interface '{interface_name}'")
        # ========================处理接口实现问题===============================

    def import_module(self, node: ImportModuleNode):
        """
            引入包，将包里面的变量、代码等都加载到环境变量中
            ImportModuleNode(module_name=Util, alias=None)
        """
        if node.module_name in self.packages:
            imported_env = self.packages[node.module_name]
            # 将导入的包内容添加到当前环境
            # 这里的 imported_env 是一个字典，里面包含了导入的包中的变量和函数等, 其中的key是没有包作为前缀的
            # imported_env.items() 的格式是:[('add', {args: [], body: []})]这样
            for name, value in imported_env.items():
                # print("name: ", name)
                # print("value: ", value)
                # 模块名称.方法名称
                if node.import_whole_module:
                    # 引入整个模块
                    module_name = node.module_name
                    if node.alias is not None:
                        module_name = node.alias
                    # self.environment[f"{node.module_name}.{name}"] = value
                    self.environment[f"{module_name}.{name}"] = value
                else:
                    # 引入模块的部分元素
                    self.environment[f"{name}"] = value
            # print("@@@self.environment: ", self.environment)
        else:
            raise ImportError(f"Package {node.module_name} not found")

    def evaluate_package_declaration(self, node: PackageDeclarationNode):
        """
            evaluate_package_declaration 方法的主要任务是：

            创建一个新的环境变量来存储包内部的内容。
            保存当前的环境变量，以便在包处理完后恢复。
            遍历包的内容（即包体中的每个声明），并使用 evaluate 方法对其进行处理。
            将包的环境保存到 self.packages 字典中，以便将来可能的导入。
            恢复原来的环境变量。

        """

        # 创建的新环境变量要和self.environment形式一致，才能正常工作，也就才能定义常量
        package_env = {
            "constants": []
        }
        old_env = self.environment
        self.environment = package_env

        for statement in node.package_body:
            self.evaluate(statement)

        # ================核心===================================
        # 将包的环境保存到 self.packages 字典中，以便将来可能的导入。
        self.packages[node.package_name] = package_env
        # print("@@@self.packages: ", self.packages)
        self.environment = old_env

    def evaluate_function_call(self, node: FunctionCallNode):
        """
                      {'myprint':
                             {
                                 'args': [],
                                 'body': [
                                     FunctionCallNode(
                                         name=print,
                                         args=[
                                             StringNode(value=add function被调用...)])]}}
        """
        color_map = {
            'println': (Fore.RESET, None),
            'printlnRed': (Fore.RED, None),
            'printlnYellow': (Fore.YELLOW, None),
            'printlnBlue': (Fore.BLUE, None),
            'printlnCyan': (Fore.CYAN, None),
            'printlnRedBg': (Fore.RESET, Back.RED),
            'printlnLightGreen': (Fore.LIGHTGREEN_EX, None)
        }

        # 检查一个实例对象是不是另一个类的实例
        if node.name == "isInstance":
            args = [self.evaluate(arg) for arg in node.args]
            instance = args[0]  # instance被解析为一个ditc对象，包含fiels和methods等
            print("instance: ", instance)
            classname = args[1]
            # print("classname: ",classname)
            if instance["parent_name"] == classname:
                return True
            else:
                return False
                # 简单示例，仅支持打印函数
        if node.name == 'print':
            args = [self.evaluate(arg) for arg in node.args]
            print(*args, end="")
            return None

        # 简单示例，仅支持打印函数
        if node.name == 'println':
            args = [self.evaluate(arg) for arg in node.args]
            print(*args)
            return None

        # 打印十六进制
        elif node.name == 'printlnHex':
            args = [self.evaluate(arg) for arg in node.args]
            hex_args = []
            for arg in args:
                if isinstance(arg, int):
                    hex_args.append(hex(arg))
                elif isinstance(arg, str):
                    # 如果是字符串，尝试将其转换为整数后再转换为十六进制
                    try:
                        hex_args.append(hex(int(arg)))
                    except ValueError:
                        hex_args.append(arg)  # 如果无法转换，保持原样
                else:
                    hex_args.append(str(arg))  # 其他类型保持原样
            print(*hex_args)
            return None

        elif node.name == 'printlnBin':
            args = [self.evaluate(arg) for arg in node.args]
            bin_args = []
            for arg in args:
                if isinstance(arg, int):
                    bin_args.append(bin(arg))
                elif isinstance(arg, str):
                    # 如果是字符串，尝试将其转换为整数后再转换为二进制
                    try:
                        bin_args.append(bin(int(arg)))
                    except ValueError:
                        bin_args.append(arg)  # 如果无法转换，保持原样
                else:
                    bin_args.append(str(arg))  # 其他类型保持原样
            print(*bin_args)
            return None

        # 输出八进制
        elif node.name == 'printlnOct':
            args = [self.evaluate(arg) for arg in node.args]
            oct_args = []
            for arg in args:
                if isinstance(arg, int):
                    oct_args.append(oct(arg))
                elif isinstance(arg, str):
                    # 如果是字符串，尝试将其转换为整数后再转换为八进制
                    try:
                        oct_args.append(oct(int(arg)))
                    except ValueError:
                        oct_args.append(arg)  # 如果无法转换，保持原样
                else:
                    oct_args.append(str(arg))  # 其他类型保持原样
            print(*oct_args)
            return None

        # 带颜色的打印函数
        if node.name in color_map:
            args = [self.evaluate(arg) for arg in node.args]
            foreground_color, background_color = color_map[node.name]

            if background_color:
                print(background_color, *args, Fore.RESET)
            else:
                print(foreground_color, *args, Fore.RESET)
            return None

        # ============ 对象的两个方法================
        if node.name == "ObjectKeys":
            # objectKeys(obj)
            if len(node.args) != 1:
                raise ValueError(f"Function '{node.name}' expects 1 argument but got {len(node.args)}.")
            args: dict = self.evaluate(node.args[0])
            return list(args.keys())

        if node.name == "ObjectValues":
            # objectValues(obj)
            if len(node.args) != 1:
                raise ValueError(f"Function '{node.name}' expects 1 argument but got {len(node.args)}.")
            args: dict = self.evaluate(node.args[0])
            return list(args.values())

        # =============Set类型======================
        if node.name == "SetLength":
            myset = self.evaluate(node.args[0])
            return len(myset)
        if node.name == "SetAdd":
            myset = self.evaluate(node.args[0])
            element = self.evaluate(node.args[1])
            try:
                myset.add(element)
                return True
            except:
                return False
        if node.name == "SetRemove":
            myset = self.evaluate(node.args[0])
            element = self.evaluate(node.args[1])
            try:
                myset.remove(element)
                return True
            except:
                return False

        if node.name == "SetContains":
            myset = self.evaluate(node.args[0])
            element = self.evaluate(node.args[1])
            return element in myset

        if node.name == "SetIsSubset":
            myset1 = self.evaluate(node.args[0])
            myset2 = self.evaluate(node.args[1])
            return myset1.issubset(myset2)

        if node.name == "SetIsSuperset":
            myset1 = self.evaluate(node.args[0])
            myset2 = self.evaluate(node.args[1])
            return myset1.issuperset(myset2)

        if node.name == "SetClear":
            myset = self.evaluate(node.args[0])
            myset.clear()
            return True

        if node.name == "SetUnion":
            myset1 = self.evaluate(node.args[0])
            myset2 = self.evaluate(node.args[1])
            return myset1.union(myset2)
        if node.name == "SetIntersection":
            myset1 = self.evaluate(node.args[0])
            myset2 = self.evaluate(node.args[1])
            return myset1.intersection(myset2)

        if node.name == "SetDiff":
            myset1 = self.evaluate(node.args[0])
            myset2 = self.evaluate(node.args[1])
            return myset1.difference(myset2)

        if node.name == "GetParamsByName":
            func_name = self.evaluate(node.args[0])
            return self.environment[func_name]["args"]

        # ==================================================
        # 通过方法名称获取默认参数
        if node.name == "GetDefaultValues":
            func_name = self.evaluate(node.args[0])
            defaults = self.environment[func_name]["defaults"]
            # defaults:  {'x': NumberNode(value=1)}
            # print("defaults: ", defaults)
            for key in defaults:
                defaults[key] = self.evaluate(defaults[key])
            return defaults

        # 通过方法名称调用函数
        # InvokeFunc("方法名称", {})
        if node.name == "InvokeFunc":
            name_and_params = [self.evaluate(arg) for arg in node.args]
            # print("name_and_params: ", name_and_params)
            # 比如: name_and_params:  ['cb', {'x': 5}]
            return self.invokefunc_server(self.environment[name_and_params[0]], name_and_params[1])

        # 返回类名的字段
        if node.name == "GetFieldsByClassName":
            print("GetFields的参数: ", node.args)
            if len(node.args) > 1:
                raise ValueError(f"Function '{node.name}' expects 1 argument but got {len(node.args)}.")
            # 传入的参数就是类名
            classname = self.evaluate(node.args[0])
            # 从环境中获取fields的学习
            fields = self.environment["objects"][classname]["fields"]
            return fields

        # GetInstanceFields
        if node.name == "GetInstanceFields":
            instance_name = f"{node.args[0].value}"
            # print("instance_name: ",instance_name)
            # {'fields': {'Name': 'Fight从入门到精通', 'Price': 99}, 'methods': {}...}
            instance_dict = self.environment["instances"][instance_name]
            return instance_dict['fields']

        # 获取实例的方法的相关信息
        if node.name == "GetInstanceMethods":
            print("node.args:  ", node.args)
            instance_name = f"{node.args[0].value}"
            instance_methods_dict = self.environment["instances"][instance_name]["methods"]

            result = []
            for method_name in instance_methods_dict:
                single_method_dict = instance_methods_dict[method_name]
                # single method dict: {'args': ['x', 'y'], 'body': []}
                del single_method_dict['body']
                single_method_dict['method_name'] = method_name
                result.append(single_method_dict)
                for arg in single_method_dict['default_values']:
                    single_method_dict['default_values'][arg] = self.evaluate(single_method_dict['default_values'][arg])
            return result

        # 设置实例的字段值 SetInstanceField(instance_name,{field:value,field2:value2})
        if node.name == "SetInstanceField":

            instance_name = f"{node.args[0].value}"
            field_and_value = self.evaluate(node.args[1])
            # 可以修改多个属性和值
            fields = list(field_and_value.keys())
            values = list(field_and_value.values())
            for i in range(len(fields)):
                if fields[i] in self.environment["instances"][instance_name]["fields"]:
                    self.environment["instances"][instance_name]["fields"][fields[i]] = values[i]
                else:
                    raise NameError(f"Field '{fields[i]}' not defined in instance '{instance_name}'")
            return True

        # 调用实例的方法 InvokeInstanceMethod(instance_name, "method_name", args_dict)
        # 似乎仅仅支持命名参数
        if node.name == "InvokeInstanceMethod":
            print("node.args=====>  ", node.args)
            instance_name = f"{node.args[0].value}"
            method_name = self.evaluate(node.args[1])
            args = self.evaluate(node.args[2])
            print("instance_name: ", instance_name)
            print("method_name: ", method_name)
            print("args: ", args)
            return self.invokefunc_server(self.environment["instances"][instance_name]["methods"][method_name], args)

        # partialUpdate
        # args: [VariableNode(value=p), ObjectNode(properties={'x': NumberNode(value=4)})]
        if node.name == "partialUpdate":
            # 返回 False 或者 True 表示是否成功
            instance_name = f"{node.args[0].value}"
            # 比如  {'x': 4}
            if instance_name not in self.environment:
                return False
            update_dict = self.evaluate(node.args[1])
            for modification_key_name in update_dict:
                self.environment[instance_name]["value"][modification_key_name] = update_dict[modification_key_name]
            return True

        # GetMethodAnnotations
        if node.name == "GetMethodAnnotations":
            # GetMethodAnnotations(instance_name: 实例, method_name:str)
            instance_name = f"{node.args[0].value}"
            method_name = self.evaluate(node.args[1])
            # print("GetMethodAnnotations: ", instance_name, method_name)
            try:
                annotations = self.environment["instances"][instance_name]["methods"][method_name]["annotations"]
                for key in annotations:
                    # 解析出值
                    annotations[key] = self.evaluate(annotations[key])
                return annotations
            except:
                return {}

        # GetFieldAnnotations
        if node.name == "GetFieldAnnotations":
            # GetFieldAnnotations(instance_name: 实例, field_name:str)
            instance_name = f"{node.args[0].value}"
            field_name = self.evaluate(node.args[1])
            # print("GetFieldAnnotations: ", instance_name, field_name)
            try:
                annotations = self.environment["instances"][instance_name]["fields_annotations"]
                print("annotations: ", annotations)
                return {field_name: annotations[field_name]}
            except:
                return {}

        # ===============借用python的字符串方法===================================
        # name就是method_name
        # dir(StringUtils) 得到StringUtils的所有方法，包括自定义的，dir返回列表
        if node.name in dir(StringUtils):
            # 获取方法
            method = getattr(StringUtils, node.name)
            # 评估参数
            args = [self.evaluate(arg) for arg in node.args]
            # 调用方法并返回结果
            return method(*args)
        # ============================FileSystemUtils==============================
        if node.name in dir(FileSystemUtils):
            # 获取方法
            method = getattr(FileSystemUtils, node.name)
            # 评估参数
            args = [self.evaluate(arg) for arg in node.args]
            # 调用方法并返回结果
            return method(*args)
        # =============================FileSystemUtils===============================

        # =======================RandomUtils===================================================
        if node.name in dir(RandomUtils):
            # 获取方法
            method = getattr(RandomUtils, node.name)
            # 评估参数
            args = [self.evaluate(arg) for arg in node.args]
            # 调用方法并返回结果
            return method(*args)

        # =======================RandomUtils===================================================

        # ===================借用python的列表方法======================================
        if node.name in dir(ListUtils):
            # 获取方法
            method = getattr(ListUtils, node.name)
            # 评估参数
            args = [self.evaluate(arg) for arg in node.args]
            # 调用方法并返回结果
            return method(*args)

        # ====================借用python的字典方法=============================================================
        if node.name in dir(DictUtils):
            method = getattr(DictUtils, node.name)
            args = [self.evaluate(arg) for arg in node.args]
            return method(*args)

        # ====================借用python的数学模块=============================================================
        if node.name in dir(MathUtils):
            method = getattr(MathUtils, node.name)
            args = [self.evaluate(arg) for arg in node.args]
            return method(*args)

        # =============================借用其他 common的方法。比如type=========
        if node.name in dir(CommonUtils):
            method = getattr(CommonUtils, node.name)
            args = [self.evaluate(arg) for arg in node.args]
            return method(*args)

        # =============================借用python的time模块===================================
        if node.name in dir(TimeUtils):
            method = getattr(TimeUtils, node.name)
            args = [self.evaluate(arg) for arg in node.args]
            return method(*args)
        if node.name == "GetFnAnnotations":
            # 获取方法的注释
            annotations = {}
            func_description = self.evaluate(node.args[0])
            if "annotations" in func_description:
                annotations = func_description["annotations"]
            # print("func_description: ",annotations)
            return annotations

        # ========================version1=================================
        # 这段代码之所以没有能够解析外部传来的变量，是因为没有将传入的参数放到environment

        # 自定义函数
        # if node.name in self.environment:
        #     # 函数字典
        #     func_dict = self.environment[node.name]
        #     # node.args是数组，需要将其中的元素都求值
        #     args: List = [self.evaluate(arg) for arg in func_dict['args']]
        #     body_statements = func_dict['body']
        #     # 进入函数作用域
        #     for statement in body_statements:
        #         # 递归调用，直到所有语句都求值完毕
        #         self.evaluate(statement)

        # ========================version2==========it seems to be working========================
        """
            将外界传入的参数放入environment中，然后执行函数体，
            这样做，内部函数可以访问外界传入的变量
        """
        # ====================处理传入的参数为匿名函数或者箭头函数====================================
        # 仅仅函数作为参数时，仅仅支持位置参数

        # ===================处理嵌套函数调用=========================================
        # 得到的是函数调用节点
        if isinstance(node.name, FunctionCallNode):
            # print("函数调用节点: ", node)
            # node.name是一个FunctionCallNode，也就是fcn嵌套fcn
            func_dict = self.evaluate(node.name)
            # 参数是传递给func_dict描述的方法的！！！
            r = self.eval_by_func_dict(func_dict, node.args)
            # print("args: ", args)
            # print("result: ", func_dict)
            # print("r: ", r)
            return r
        # ===================处理嵌套函数调用=========================================
        # 使用Node解求值
        if node.name in self.environment:
            # 准备函数的参数和体
            # print("===============> node.name: ", node.name)
            # print("=======x====> args:  ", node.args)
            # 结果是None
            # print("self.environment[node.name] = ", self.environment[node.name])
            func_dict = self.environment[node.name]

            # 如果 func 是一个函数（包括 Lambda 函数）
            func_args = func_dict['args']  # 形参名称,比如 ['a', 'b']
            body_statements = func_dict['body']  # 函数体
            return_value = None  # 函数返回值

            # ============默认参数的部分===========================
            # FunctionCallNode(
            #       name=add,
            #       args=[NumberNode(value=111111), StringNode(value=empty str)])
            # node.args:  是实际传入的参数  func_args：是形参,函数参数名称(list类型)
            local_scope = {}
            # print("node: ", node)
            # self.environment[node.name]["defaults"]指的是函数声明时候放到environment中的默认值
            default_values = self.environment[node.name]["defaults"]
            arg_keys = list(default_values.keys())
            for arg_key in arg_keys:
                local_scope[arg_key] = self.evaluate(default_values[arg_key])
            """
                1,node是FunctionDeclarationNode,包含了函数定义时候的具体细节,而不是FunctionCallNode
            """
            # =========================================================
            # 参数检查(个数)
            # if len(func_args) != len(node.args):  # 参数检查， 这里仅仅支持位置参数
            #     raise ValueError(
            #         f"Function '{node.name}' expects {len(func_args)} arguments but got {len(node.args)}.")

            # 将实际参数与形参对应
            # node.args: 实际传入的参数  func_args: 形参名称
            # arg_name: 形式参数名  arg_value: 实际参数值
            # ====================位置参数处理=====================================

            # print(" zip(func_args, node.args): ", list(zip(func_args, node.args)))
            # zip(func_args, node.args): [('x', FunctionDeclarationNode(is_static=False, name=cb, args=['y'], body=[
            #     FunctionCallNode(name=print, args=[VariableNode(value=y)], named_arg_values={})], default_values={}, ))]
            # node.args是实参，func_args是形参
            # print("测试func_args: ", func_args)
            for arg_name, arg_value in zip(func_args, node.args):
                local_scope[arg_name] = self.evaluate(arg_value)

            # 将命名参数放到环境中
            # 命名参数，比如 add(a=1, b=2)
            # print("node: ", node.named_arg_values.items())
            for named_arg, named_arg_value in node.named_arg_values.items():
                local_scope[named_arg] = self.evaluate(named_arg_value)

            # ===============检查参数=============在默认参数和传入参数合并后判断参数是否齐全============
            # print("需要的参数: ",self.environment[node.name]['args'])
            for format_param in self.environment[node.name]['args']:
                if format_param not in local_scope:
                    raise ValueError(f"Function '{node.name}' expects parameter '{format_param}' but got nothing.")

            # =======================环境================================
            # 保存当前的环境，以便函数执行完后恢复
            previous_environment = self.environment.copy()
            # 更新环境为局部作用域, 并执行函数体, 这样做，内部函数可以访问外界的变量
            self.environment.update(local_scope)

            # ==================执行方法体=============================
            return_value = None  # 默认的返回值
            for statement in body_statements:
                # print("statement: ", statement)
                # 1, 拦截 在if elif else外的 return 语句
                if isinstance(statement, ReturnNode):
                    # return return_value.value  # 直接返回返回值
                    return_value = self.evaluate(statement)
                    return return_value

                # 2, 拦截 if elif else 里面的 return 语句
                # ==================if elif else里面的return =====================
                # return_value判断是不是None, 如果不是None, 说明有了返回值，那么就是直接返回！！！
                # statement可能是某个ifstatement语句，而ifstatement语句可能有return语句，所以需要判断一下
                # 是否返回了值，如果返回了，说明就不用再往下执行了
                return_value = self.evaluate(statement)
                # if elif else里面的return的值使用dict继续包装，具体可以看if_statement()
                if isinstance(return_value, dict) and "fight_tag" in return_value:
                    # print("dict 类型")
                    return return_value["value"]  # 直接返回返回值
                # ==================if elif else里面的return=====================

            # ========================恢复环境===================
            # 恢复之前的环境
            self.environment = previous_environment

            # =======================返回值=========================
            # 上面的for in 循环,如果for in 遇到return,会直接返回,这里就不会执行
            return return_value  # 确保返回函数的返回值
            # ======================================================
        else:
            raise NameError(f"Function '{node.name}' not defined")

    def invokefunc_server(self, func_dictx, args):
        """
            1,该函数就是用来服务 InvokeFunc方法的
            2,func_dictx是函数字典，args是实际传入的参数
              args是命名参数，比如 {a:1, b:2}
        """
        func_dict = func_dictx  # 值居然是None
        # 如果 func 是一个函数（包括 Lambda 函数）
        func_args = func_dict['args']  # 形参名称,比如 ['a', 'b']
        body_statements = func_dict['body']  # 函数体
        return_value = None  # 函数返回值

        local_scope = {}
        # 这里使用命名参数 {a:1, b:2} 这种
        for named_arg, named_arg_value in args.items():
            local_scope[named_arg] = named_arg_value
        # =======================环境================================
        # 保存当前的环境，以便函数执行完后恢复
        previous_environment = self.environment.copy()
        # 更新环境为局部作用域, 并执行函数体, 这样做，内部函数可以访问外界的变量
        self.environment.update(local_scope)

        # ==================执行方法体=============================
        return_value = None  # 默认的返回值
        for statement in body_statements:
            return_value = self.evaluate(statement)
            if isinstance(return_value, ReturnNode):
                return return_value.value  # 直接返回返回值
        # ========================恢复环境===================
        # 恢复之前的环境
        self.environment = previous_environment

        return return_value  # 确保返回函数的返回值

    def eval_by_func_dict(self, func_dictx, args):
        """
                该方法用来辅助执行嵌套函数调用
                func_dict是在environment中找到的函数字典，args是实际传入的参数
                func_dict通过名称来获取，比如:
                self.environment[func_name]
        """

        # 准备函数的参数和体
        func_dict = func_dictx  # 值居然是None
        # 如果 func 是一个函数（包括 Lambda 函数）
        func_args = func_dict['args']  # 形参名称,比如 ['a', 'b']
        body_statements = func_dict['body']  # 函数体
        return_value = None  # 函数返回值

        # ============默认参数的部分===========================
        # FunctionCallNode(
        #       name=add,
        #       args=[NumberNode(value=111111), StringNode(value=empty str)])
        # node.args:  是实际传入的参数  func_args：是形参,函数参数名称(list类型)
        local_scope = {}
        print("args: ", args)
        # node.args是实参，func_args是形参
        for arg_name, arg_value in zip(func_args, args):
            local_scope[arg_name] = self.evaluate(arg_value)

        # =======================环境================================
        # 保存当前的环境，以便函数执行完后恢复
        previous_environment = self.environment.copy()
        # 更新环境为局部作用域, 并执行函数体, 这样做，内部函数可以访问外界的变量
        self.environment.update(local_scope)

        # ==================执行方法体=============================
        return_value = None  # 默认的返回值
        for statement in body_statements:
            return_value = self.evaluate(statement)
            if isinstance(return_value, ReturnNode):
                return return_value.value  # 直接返回返回值

        # ========================恢复环境===================
        # 恢复之前的环境
        self.environment = previous_environment

        # =======================返回值=========================
        # 上面的for in 循环,如果for in 遇到return,会直接返回,这里就不会执行
        return return_value  # 确保返回函数的返回值

    def evaluate_for_in(self, node: ForInNode):
        # print("node: ",node)
        # print("variable:", node.variable)

        # 保存之前的环境变量
        previous_environment = self.environment.copy()

        # 设置初始变量
        self.environment[node.variable] = "xxxx"
        # print("environment:", self.environment)
        iter_obj = self.evaluate(node.iteration_obj)
        # print("iter_obj:", iter_obj)

        """
                        try:
                            self.evaluate(statement)
                        except BreakException:
                            break
        """

        # 遍历每个元素
        for item in iter_obj:
            self.environment[node.variable] = item
            try:
                for statement in node.body:
                    self.evaluate(statement)
            except BreakException:
                break

        # 还原环境变量
        self.environment = previous_environment.copy()

    def evaluate_object_index(self, node: ObjectIndexNode):
        # ===============版本2============================================
        """
          解析 对象{属性} 这样的表达式，支持嵌套属性访问
          """
        # 获取对象
        if isinstance(node.object_name, (ListIndexNode, ObjectIndexNode, MultiListIndexNode)):
            obj = self.evaluate(node.object_name)
        else:
            if node.object_name not in self.environment:
                raise NameError(f"Object '{node.object_name}' not defined")
            obj = self.environment[node.object_name]

        # 获取键
        key = self.evaluate(node.key_expr)

        # 检查键是否存在
        if isinstance(obj, dict):
            if key not in obj:
                raise KeyError(f"Key '{key}' not defined in object")
            return obj[key]
        elif isinstance(obj, list):
            if not isinstance(key, int) or key < 0 or key >= len(obj):
                raise IndexError(f"Invalid index '{key}' for list")
            return obj[key]
        else:
            raise TypeError(f"Object of type '{type(obj)}' is not subscriptable")

    def evaluate_multi_list_index(self, node: MultiListIndexNode):
        # =========================版本2==============================
        # isinstance 会检查 node.list_name 是否是这个元组中任何一个类型的实例。
        if isinstance(node.list_name, (ListIndexNode, ObjectIndexNode, MultiListIndexNode)):
            current_result = self.evaluate(node.list_name)
        else:
            if node.list_name not in self.environment:
                raise NameError(f"List '{node.list_name}' not defined")
            current_result = self.environment[node.list_name]

        for dim_indexes in node.index_list:
            start_index = self.evaluate(dim_indexes[0])
            end_index = None if dim_indexes[1] is None else self.evaluate(dim_indexes[1])

            if end_index is None:
                current_result = current_result[start_index]
            else:
                current_result = current_result[start_index:end_index + 1]

        return current_result

    def evaluate_list_index(self, node: ListIndexNode):

        # ====================版本2===============================
        # 如果 node.list_name 是 ObjectIndexNode 或 ListIndexNode，先评估它
        if isinstance(node.list_name, (ObjectIndexNode, ListIndexNode, MultiListIndexNode)):
            lst = self.evaluate(node.list_name)
        else:
            if node.list_name not in self.environment:
                raise NameError(f"List '{node.list_name}' not defined")
            lst = self.environment[node.list_name]

        start_index = self.evaluate(node.start_index)

        if node.end_index is None:
            return lst[start_index]
        else:
            end_index = self.evaluate(node.end_index)
            return lst[start_index:end_index + 1]

    def evaluate_function_declaration(self, node: FunctionDeclarationNode):
        # 处理函数声明
        """
            FunctionDeclarationNode(
                    name=myprint,
                    args=[],
                    body=[
                            FunctionCallNode(name=print, args=[StringNode(value=add function被调用...)])
                         ]
            )
        一个想法：
            如果在方法前面加上指定的模块名称，是不是就实现了定义域问题了?
            比如：@module.function() 这样就可以调用模块中的函数了。
        """
        annot = {}
        for key in node.annotations:
            annot[key] = self.evaluate(node.annotations[key])
        # 先看看是不是在环境中已经存在了

        # name = map
        # print("node.name: ", node.name)

        if node.name in self.environment:
            # raise NameError(f"Function '{node.name}' already defined")
            # ==================================================
            if node.tag is None:  # 函数表示作为参数进行传递
                # print("收到tag是none的节点: ",node)
                return {
                    "annotations": annot,
                    "args": node.args,
                    "body": node.body,
                    "defaults": node.default_values,  # 假设在 AST 中传递默认值
                }
            raise NameError(f"Function '{node.name}' already defined")

            # ==================================================
        # 处理annotations
        annot = {}
        for key in node.annotations:
            annot[key] = self.evaluate(node.annotations[key])

        """
        
        没修改前: 
            self.environment[node.name] = {
                "annotations": annot,
                "args": node.args,
                "body": node.body,
                "defaults": node.default_values,  # 假设在 AST 中传递默认值
            }
        
        
        """

        # ================修改后=====================
        result = {
            "annotations": annot,
            "args": node.args,
            "body": node.body,
            #
            "defaults": node.default_values,  # 假设在 AST 中传递默认值
        }
        self.environment[node.name] = result

        return result
        # print("after declaration 后的environment: ", self.environment)

    def evaluate_if_statement(self, node):
        # 评估条件表达式
        condition_value: bool = self.evaluate(node.condition)
        print("condition_value: ", condition_value)

        # 根据条件的结果执行相应的代码块
        if condition_value:  # 如果条件为真，执行 if 代码块
            # if_body是一个列表，可能有多个语句
            for statement in node.if_body:
                # ============新增： 如果在if语句中遇到return,可以返回值到外界==========
                if isinstance(statement, ReturnNode):
                    # print("遇到return node", statement)
                    # print("self.evaluate(statement.value): ", self.evaluate(statement.value))
                    # return self.evaluate(statement.value)  # 直接返回返回值 ======> 原来的代码
                    return {"fight_tag": True, "value": self.evaluate(statement.value)}  # 直接返回返回值

                # ============测试==========
                else:
                    self.evaluate(statement)
            # return
        # print("还继续执行?")
        # elif_: [{"condition": condition, "elif_statements": [statement1, statement2, statement3]}]
        for elseif_dict in node.elif_:
            condition_value: bool = self.evaluate(elseif_dict['condition'])
            if condition_value:
                # return self.evaluate(elseif.body)
                elif_statements = elseif_dict['elif_statements']
                for statement in elif_statements:
                    # ============新增： 如果在if语句中遇到return,可以返回值到外界==========
                    if isinstance(statement, ReturnNode):
                        # return self.evaluate(statement.value)  # 直接返回返回值
                        return {"fight_tag": True, "value": self.evaluate(statement.value)}  # 直接返回返回值
                    # ============测试==========
                    self.evaluate(statement)
                return
        else:
            # 如果有 else 部分，执行 else 代码块
            else_statements = node.else_

            for statement in else_statements:
                # ============新增： 如果在if语句中遇到return,可以返回值到外界==========
                if isinstance(statement, ReturnNode):
                    return {"fight_tag": True, "value": self.evaluate(statement.value)}  # 直接返回返回值
                # ============测试==========
                else:
                    self.evaluate(statement)

    def evaluate_object(self, node):
        return {k: self.evaluate(v) for k, v in node.k_v.items()}

    def evaluate_string(self, node):

        # ================old version=====================
        # return node.value
        # ==============old version=====================

        # ===============同时考虑包含模板字符串和不包含模板字符串=================================
        # 解析里面的模板字符串，替换变量值
        template_str = node.value

        # 使用正则表达式查找 ${} 中的变量
        def replace_variable(match):
            var_name = match.group(1)  # 提取变量名
            # 返回变量的值，如果未定义则返回原变量名
            return str(self.environment.get(var_name, var_name))

        # 使用正则表达式进行替换
        result = re.sub(r'\${(.*?)}', replace_variable, template_str)

        return result
        # ===============同时考虑包含模板字符串和不包含模板字符串=================================

    def evaluate_number(self, node):
        # node是字符串类型,需要转换为数字类型
        try:
            if '.' in node.value:
                return float(node.value)
            else:
                return int(node.value)
        except ValueError:
            raise ValueError(f"Invalid number: {node.value}")

    def evaluate_variable(self, node):
        """
            变量存放在list里面
        """
        if node.value in self.environment:
            return self.environment[node.value]
        else:
            raise NameError(f"Variable '{node.value}' not defined")

    def evaluate_binary_op(self, node):
        left_val = self.evaluate(node.left)
        right_val = self.evaluate(node.right)

        if node.op == 'PLUS':
            return left_val + right_val
        elif node.op == 'MINUS':
            return left_val - right_val
        elif node.op == 'MUL':
            return left_val * right_val
        elif node.op == 'DIV':
            return left_val / right_val
        elif node.op == 'POW':
            return left_val ** right_val
        elif node.op == "MOD":
            return left_val % right_val
        elif node.op == 'FLOOR_DIV':
            return left_val // right_val
        # 逻辑比较
        elif node.op == 'GT':  # 大于
            return left_val > right_val

        elif node.op == 'LT':  # 小于
            return left_val < right_val

        elif node.op == 'LE':  # 小于等于
            return left_val <= right_val

        elif node.op == 'GE':  # 大于等于
            return left_val >= right_val

        elif node.op == 'EQ':  # 等于
            return left_val == right_val

        elif node.op == 'NEQ':  # 不等于
            return left_val != right_val

        # 逻辑运算
        elif node.op == 'AND':
            # 对于算术比较，直接得到bool类型的值了
            # 字符串转bool
            if left_val == "True":
                left_val = True
            if left_val == "False":
                left_val = False
            if right_val == "True":
                right_val = True
            if right_val == "False":
                right_val = False
            # ================ 对逻辑运算的类型进行检查======================
            if not isinstance(left_val, bool) or not isinstance(right_val, bool):
                raise TypeError("逻辑运算只适合布尔类型!")
            return left_val and right_val

        elif node.op == 'OR':
            return left_val or right_val
        else:
            raise ValueError(f"Unknown operator: {node.op}")

    def evaluate_assignment(self, node):
        """
            赋值节点：将变量的值存入环境变量

            lambda 函数的赋值：
                AssignmentNode(
                    name=x,
                    value=LambdaFunctionCallNode(
                        args=[VariableNode(value=x), VariableNode(value=y)],
                        body=[NumberNode(value=10)]))
        """
        # 应该将函数信息保存到环境中，而不是执行他
        # 如果赋值的是一个函数声明，存储完整的函数信息
        # print("node.value: ",node.value)
        """
            node.value是FunctionDeclarationNode类型, 说明是函数声明，需要将函数信息保存到环境中
            这样在函数调用的时候自己会解析并调用！！！！
        """

        if isinstance(node.value, FunctionDeclarationNode):
            # 将函数的参数和体存入环境  node.value是FunctionDeclarationNode类型， 需要里面的参数和body_statements
            self.environment[node.name] = {
                "args": node.value.args,
                "body": node.value.body,
                # 对于let z = def(){}这种形式，需要将默认参数放到environment中, 否则在
                # 函数调用的时候找不到参数,而对let z = def(){}类和箭头函数的默认参数，需要在
                # evaluate_assignment中进行处理，对于 def main(){}这类函数，参数需要在
                # evaluate_function_declaration中处理,这就是差异！！！
                "defaults": node.value.default_values,  # 假设在 AST 中传递默认值
            }
        else:
            # =======================常量检查===============================
            if node.name in self.environment['constants']:
                raise ValueError(f"Constant '{node.name}' cannot be reassigned")
                # 如果当前节点是常量，加入到constants列表中, 用于检查是否重复赋值
            if node.is_constant:
                self.environment['constants'].append(node.name)
            # 否则，直接求值
            value = self.evaluate(node.value)

            # 赋值
            self.environment[node.name] = value
            return value

    def evaluate_loop(self, node):
        """
            self.condition = condition
            self.body = body
        """
        # 用于跳出while循环
        break_flag = False
        condition_value: bool = self.evaluate(node.condition)
        # 不断判断条件
        while condition_value:
            for statement in node.body:
                # print("statement: ",statement)
                # 1，可能遇到跳出循环的情况
                if isinstance(statement, BreakNode):
                    break_flag = True
                # if break_flag == False:
                try:
                    self.evaluate(statement)
                    # 2，重新计算条件表达式
                    condition_value = self.evaluate(node.condition)
                except BreakException:
                    break_flag = True
                    break
            if break_flag:
                break


# 测试Evaluator
if __name__ == '__main__':
    # ================================================================
    code = """
        $x = 3;
        x/=2;
        printlnRed(x);
        
    """
    # ==================================================================
    print("=================tokenizer======================\n")
    # 词法分析
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    for i in tokens:
        print(i)
    print("=================parser========================\n")
    # 语法分析
    parser = Parser(tokens)
    ast = parser.parse()  # 生成AST, 多个xxNode组成的列表
    print("AST: ")
    for node in ast:
        print(node)

    # 求值器
    evaluator = Evaluator()
    print("=================evaluator=====================\n")
    for node in ast:
        r = evaluator.evaluate(node)
        # print(r)
    print("environment（最终版）: \n\t", evaluator.environment)
    print("environment（instances）: \n\t", evaluator.environment["instances"])
