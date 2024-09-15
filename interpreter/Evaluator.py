import os
import re
import uuid
from typing import List

from colorama import Fore, Back

from interpreter.ClassNodes import ClassDeclarationNode, NewObjectNode, MethodCallNode, GetMemberNode, \
    CallClassInnerMethod, ThisNode, InterfaceNode, GetMemberNodeByThis, SerialMethodCallNode, SuperNode, \
    ImportThirdPartyClassNode, ImportBuiltinClassNode, UseModuleNode, ClassPropertyAssignNode
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
    SerialCall, PlusAssignNode, MinusAssignNode, MultiplyAssignNode, DivideAssignNode, ObjectAssignNode, ListAssignNode, \
    ImportThirdPartyModuleNode, UnaryOpNode, LogicNotNode, ReAssignmentNode
from interpreter.Parser import Parser
from interpreter.utils.datastructure.StringUtils import StringUtils
from interpreter.Tokenizer import Tokenizer
from interpreter.utils.math.MathUtils import MathUtils


class BreakException(Exception):
    """自定义异常，用于处理循环中的 break 语句"""
    pass


class ReturnException:
    def __init__(self, value):
        self.value = value


class Evaluator:
    def __init__(self):
        # 环境变量
        self.environment = {
            "arg_to_instance": {
                # "painterVan": "x",
            },  # 建立传入参数和实例的映射，用于多态的实现  {形参: 实参, 形参: 实参}
            "instances": {},  # 记录创建的类的实例
            "constants": [],  # 记录声明的常量
            "objects": {},  # 导入的类exports和创建的对象
            "interfaces": {},  # 记录接口
            "structs": {},  # 记录结构体
            "enums": {},  # 记录枚举类型
            "types": {}  # 记录类型 {变量名称: 类型 }
        }
        self.current_object = None  # 当前this指向的对象
        self.packages = {}  # 导入的模块
        self.modules = {}  # 导入的第三方模块
        self.exports = {}  # 记录被导出的内容，用于辅助  {模块名称:[被导出的内容]}
        self.used_elements = {}  # {模块名称:[]} 记录被use的内容

    def evaluate(self, node, env=None):
        """
            解析器的入口函数，根据不同的节点类型，调用相应的解析函数
            用于解析AST，得到具体的结果
            比如，对于NumberNode，调用evaluate_number()函数，返回数字的值

        """
        if env is not None:
            self.environment = env

        # 数据类型解析
        if isinstance(node, (int, float, bool, str, list, dict, tuple)):
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
            # result = self.evaluate_if_statement(node)
            # if isinstance(result, dict) and result.get("fight_tag"):
            #     return result  # 传递特殊的返回值


        # 表达式解析
        elif isinstance(node, BinaryOpNode):
            return self.evaluate_binary_op(node)

        # UnaryOpNode
        elif isinstance(node, UnaryOpNode):
            return self.evaluate_unary_op(node)


        elif isinstance(node, AssignmentNode):
            return self.evaluate_assignment(node)

        # 循环解析
        elif isinstance(node, BreakNode):
            # 遇到break语句，抛出BreakException异常，
            # 然后在循环体外捕获这个异常，跳出循环
            raise BreakException()
        elif isinstance(node, LoopNode):
            return self.evaluate_loop(node)
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
            return self.evaluate_function_call(node)

        elif isinstance(node, ReturnNode):
            # return self.evaluate(node.value) # 原来的代码
            return self.evaluate(node.value)  # 返回结果
            # raise ReturnException(self.evaluate(node.value))

        # 列表索引解析
        elif isinstance(node, ListIndexNode):
            return self.evaluate_list_index(node)

        # 多维索引节点
        elif isinstance(node, MultiListIndexNode):
            return self.evaluate_multi_list_index(node)

        elif isinstance(node, ObjectIndexNode):
            return self.evaluate_object_index(node)


        # UseModuleNode
        elif isinstance(node, UseModuleNode):
            return self.use_module(node)


        # 类声明解析
        elif isinstance(node, ClassDeclarationNode):
            return self.evaluate_class_declaration(node)

        elif isinstance(node, NewObjectNode):
            return self.evaluate_new_object_expr(node)

        # 方法调用解析  p->show();
        elif isinstance(node, MethodCallNode):
            # 能不能再MethodNode里面加个属性, 记录instance的类型，
            # 比如dict, list, str, 这样在调用方法的时候，就可以根据类型进行调用
            # try:
            #     val = self.environment[node.instance_name]
            #     if isinstance(val, (dict, list, str, set)):
            #         # 如果发生了NameError,可能就是基本数据类型进行方法的调用
            #         print("进入")
            #         return self.execute_by_instance_type(node)
            #     else:
            #         # 看看是不是实例进行方法调用
            #         return self.evaluate_method_call(node)
            # except NameError as e:
            #     print(e)
            try:
                return self.evaluate_method_call(node)
            except NameError as e:
                return self.execute_by_instance_type(node)

        # 连续调用
        elif isinstance(node, SerialMethodCallNode):
            return self.evaluate_serial_method_call(node)

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
            return self.evaluate_deconstruct_assign(node)

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
        elif isinstance(node, MultiplyAssignNode):
            return self.evaluate_multiply_assign(node)

        # /=
        elif isinstance(node, DivideAssignNode):
            return self.evaluate_divide_assign(node)



        # d{"key"} = val
        elif isinstance(node, ObjectAssignNode):
            return self.evaluate_object_assign(node)

        # d[index] = val
        elif isinstance(node, ListAssignNode):
            return self.evaluate_list_assign(node)

        # LogicNotNode  !True
        elif isinstance(node, LogicNotNode):
            val = self.evaluate(node.expr)
            if not isinstance(val, bool):
                raise TypeError("! operator only works on boolean values")
            return not val

        elif isinstance(node, ReAssignmentNode):
            return self.evaluate_reassignment(node)


        # ClassPropertyAssignNode
        elif isinstance(node, ClassPropertyAssignNode):
            return self.evaluate_class_property_assign(node)

        else:
            raise TypeError(f"Unexpected node type: {type(node)}")

    def evaluate_class_property_assign(self, node: ClassPropertyAssignNode):
        """
            类属性赋值  A->b = 1;
        """
        pass
        print("\n======ClassPropertyAssignNode========")
        print(node.class_name)
        print(node.property_name)
        print(node.value)
        print("=======ClassPropertyAssignNode========\n")

        print("self.environment['objects']: ", self.environment["objects"])

        if node.class_name not in self.environment["objects"]:
            raise Exception(f"Class {node.class_name} not found")
        if node.property_name not in self.environment["objects"][node.class_name]["static_fields"]:
            raise Exception(f"Static property {node.property_name} not found in class {node.class_name}")

        self.environment["objects"][node.class_name]["static_fields"][node.property_name] = self.evaluate(node.value)
        return None

    def check_is_from_module(self, access_name):
        """
            access_name一般是各种阶段的name属性，或者xx_name属性

            查看要访问的函数、变量是不是来自某个模块，
            主要是通过全局的self.exports进行检查
                self.exports的格式是：
                {
                    "module_name": [
                        "export_name1",
                        "export_name2",
                       ...
                    ]
                }
           这里的module_name是模块的名称，export_name是要导出的函数、变量的名称
        """
        print("self.exports: ", self.exports)

        for module_name in self.exports:
            # print("module_name: ", module_name, )
            if access_name in self.exports[module_name]:
                return module_name  # 返回模块名称，字符串类型
        return False

    def use_module(self, node: UseModuleNode):
        """
        1. 读出代码
        2. 全部加载到环境中
        3. 根据exports来判断是否导出，如果没有导出而尝试导出，报错
        """
        # 记录被use的内容
        self.used_elements[node.module_path] = node.use_elements

        final_path = ""
        if node.is_builtin:
            # 内置模块
            builtin_path = os.path.join(os.path.dirname(__file__), "builtin")
            final_path = os.path.join(builtin_path, node.module_path + ".fight")
        else:
            final_path = node.module_path

        # 读取代码
        with open(final_path, "r", encoding="utf-8") as f:
            code1 = f.read()

        # 解析代码
        pkg_tokenizer = Tokenizer(code1)
        pkg_parser = Parser(pkg_tokenizer.tokenize())
        pkg_ast = pkg_parser.parse(final_path)  # 处理第三方代码的结果
        # print("\nast: ", pkg_ast, "\n")

        exports_node = pkg_ast[-1]  # 最后一个节点是ExportsNode

        # 创建新的模块环境
        module_env = {
            "arg_to_instance": {},
            "instances": {},
            "constants": [],
            "objects": {},
            "interfaces": {},
            "structs": {},
            "enums": {}
        }

        # 记录旧环境
        old_env = self.environment

        # 设置当前环境为模块环境
        self.environment = module_env

        # 首先处理模块内部所有声明，包括导出和未导出的
        for declaration_node in pkg_ast[:-1]:
            self.evaluate(declaration_node)

        # 检查并处理导出
        for use_element in node.use_elements:
            if use_element not in exports_node.exports_list:
                raise Exception(f"Module {final_path} does not export {use_element}")

        # 将模块环境中的导出内容复制到主环境
        for use_element in node.use_elements:
            if use_element in module_env['objects']:
                old_env['objects'][use_element] = module_env['objects'][use_element]
            elif use_element in module_env['interfaces']:
                old_env['interfaces'][use_element] = module_env['interfaces'][use_element]
            elif use_element in module_env['structs']:
                old_env['structs'][use_element] = module_env['structs'][use_element]
            elif use_element in module_env['enums']:
                old_env['enums'][use_element] = module_env['enums'][use_element]
            elif use_element in module_env:
                old_env[use_element] = module_env[use_element]
            else:
                raise Exception(f"Element {use_element} not found in module {node.module_path}")

        # =======================================================
        # 为导出的函数创建闭包，使其能够访问模块环境
        for use_element in node.use_elements:
            # print("创建闭包: ", use_element)

            if isinstance(old_env.get(use_element), dict) and 'body' in old_env[use_element]:  # 说明是函数的dict
                old_env[use_element] = self.create_closure(old_env[use_element], module_env, use_element)
        # ===================================================

        # 恢复主环境
        self.environment = old_env

        # 记录模块环境
        self.modules[node.module_path] = module_env

        # 记录导出列表
        self.exports[node.module_path] = exports_node.exports_list

    def create_closure(self, func_dict, module_env, func_name):
        def closure(*args, **kwargs):
            # 保存当前环境
            old_env = self.environment
            # 创建一个新的环境，包含模块环境和当前环境的某些关键部分
            new_env = module_env.copy()
            new_env.update({
                'arg_to_instance': old_env.get('arg_to_instance', {}),
                'instances': old_env.get('instances', {})
            })
            self.environment = new_env

            # 创建一个模拟的 FunctionCallNode
            mock_node = type('MockFunctionCallNode', (), {
                'name': func_name,  # 使用传入的函数名
                'args': args,
                'named_arg_values': kwargs
            })()

            # 使用现有的 evaluate_function_call 方法
            result = self.evaluate_function_call(mock_node)

            # 恢复环境
            self.environment = old_env
            return result

        # 创建新的函数字典，包含闭包
        new_func_dict = func_dict.copy()
        new_func_dict['closure'] = closure
        return new_func_dict

    def eval_builtin_functions(self, node: FunctionCallNode):
        color_map = {
            'println': (Fore.RESET, None),
            'printlnRed': (Fore.RED, None),
            'printlnYellow': (Fore.YELLOW, None),
            'printlnBlue': (Fore.BLUE, None),
            'printlnCyan': (Fore.CYAN, None),
            'printlnLightGreen': (Fore.LIGHTGREEN_EX, None),
            'printlnMagenta': (Fore.MAGENTA, None)  # 粉红
        }

        # ========Is系列函数================================
        # 判断是不是数字
        if node.name == "IsNumber":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, (int, float)):
                return True
            else:
                return False
        # 判断是不是字符串
        if node.name == "IsString":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, str):
                return True
            else:
                return False

        # 判断是不是布尔值
        if node.name == "IsBool":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, bool):
                return True
            else:
                return False
        # IsInt
        if node.name == "IsInt":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, int):
                return True
            else:
                return False
        # IsFloat
        if node.name == "IsFloat":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, float):
                return True
            else:
                return False
        # IsList
        if node.name == "IsList":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, list):
                return True
            else:
                return False
        # IsDict  Object就是字典
        if node.name == "IsObject":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, dict):
                return True
            else:
                return False
        # IsSet
        if node.name == "IsSet":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, set):
                return True
            else:
                return False
        # IsFunction
        if node.name == "IsFunction":
            arg = self.evaluate(node.args[0])
            if isinstance(arg, dict) and 'body' in arg:
                return True
            else:
                return False
        # ========Is系列函数================================

        # 检查一个实例对象是不是另一个类的实例
        if node.name == "IsInstance":
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

        # ImplInterface(类名：string, 接口名:string)
        if node.name == "HasImplInterface":
            args = [self.evaluate(arg) for arg in node.args]

            classname = args[0]
            interface_name = args[1]
            print("classname: ", classname)
            print("interface_name: ", interface_name)
            print("\nobjects: ", self.environment["objects"])

            # 找到类
            class_find = self.environment["objects"][classname]
            print("class_find: ", class_find)

            # 找到接口
            interface_methods = self.environment["interfaces"][interface_name]
            print("interface_methods: ", interface_methods)

            # 遍历接口的方法，判断类中是否有实现
            for method_name in interface_methods:
                if method_name not in class_find["methods"]:
                    return False
            return True

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

        # Char2Asc
        if node.name == "Char2Asc":
            return ord(self.evaluate(node.args[0]))

        # Asc2Char
        if node.name == "Asc2Char":
            return chr(self.evaluate(node.args[0]))

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
        raise NameError(f"Function '{node.name}' not defined")

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

        # ============模块系统的代码===========================================
        if node.name in self.environment:
            func_dict = self.environment[node.name]

            # 检查是否存在闭包
            if 'closure' in func_dict:
                # 如果存在闭包，直接调用闭包函数
                args = [self.evaluate(arg) for arg in node.args]
                kwargs = {k: self.evaluate(v) for k, v in node.named_arg_values.items()}
                return func_dict['closure'](*args, **kwargs)
        # ============模块系统的代码===========================================

        """
            将外界传入的参数放入environment中，然后执行函数体，
            这样做，内部函数可以访问外界传入的变量
        """
        # ====================处理传入的参数为匿名函数或者箭头函数====================================
        # 仅仅函数作为参数时，仅仅支持位置参数

        # ===================处理嵌套函数调用=========================================
        # 得到的是函数调用节点
        if isinstance(node.name, FunctionCallNode):
            # node.name是一个FunctionCallNode，也就是fcn嵌套fcn
            func_dict = self.evaluate(node.name)
            # 参数是传递给func_dict描述的方法的！！！
            r = self.eval_by_func_dict(func_dict, node.args)
            return r
        # ===================处理嵌套函数调用=========================================
        # 使用Node解求值
        if node.name in self.environment:
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
            local_scope = {
                "instances": {}
            }
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
            for arg_name, arg_value in zip(func_args, node.args):
                # local_scope[arg_name] = self.evaluate(arg_value)  # 原来代码，只能处理传入简单参数，而不能处理对象
                # =========================传入的如果是对象======================================
                val_or_instance = self.evaluate(arg_value)

                # ==================传入类型和声明类型的检查：是否一致================================
                params_types = func_dict['params_types']
                # 利用求值后的val_or_instance的类型来进行判断
                if params_types[arg_name] != self.get_value_type(val_or_instance):
                    raise TypeError(
                        f"Function '{node.name}' expects parameter '{arg_name}' to be of type '{params_types[arg_name]}' but got '{self.get_value_type(val_or_instance)}'.")
                # ==================传入类型和声明类型的检查：是否一致================================

                # 传入的如果是对象
                if isinstance(val_or_instance, dict) and "fields" in val_or_instance:
                    # 传入的如果是对象
                    local_scope["instances"][arg_name] = val_or_instance
                else:
                    local_scope[arg_name] = val_or_instance
            # ===============================================================

            # 将命名参数放到环境中
            # 命名参数，比如 add(a=1, b=2)
            # print("node: ", node.named_arg_values.items())
            for named_arg, named_arg_value in node.named_arg_values.items():
                local_scope[named_arg] = self.evaluate(named_arg_value)

            # ===============检查参数=============在默认参数和传入参数合并后判断参数是否齐全============
            # print("需要的参数: ",self.environment[node.name]['args'])
            # for format_param in self.environment[node.name]['args']:
            #     if format_param not in local_scope:
            #         raise ValueError(f"Function '{node.name}' expects parameter '{format_param}' but got nothing.")

            # =======================环境================================
            # 保存当前的环境，以便函数执行完后恢复
            previous_environment = self.environment.copy()
            # 更新环境为局部作用域, 并执行函数体, 这样做，内部函数可以访问外界的变量
            self.environment.update(local_scope)

            # ==================执行方法体=============================
            try:
                return_value = None  # 默认的返回值
                for statement in body_statements:
                    # 1, 拦截 在if elif else外的 return 语句
                    if isinstance(statement, ReturnNode):
                        # return return_value.value  # 直接返回返回值
                        return_value = self.evaluate(statement)
                        # ===================== 返回值类型检查=================
                        if self.get_value_type(return_value) != func_dict['return_type']:
                            raise TypeError(
                                f"Function '{node.name}' expects return value to be of type '{func_dict['return_type']}' but got '{self.get_value_type(return_value)}'.")
                        # ============== 返回值类型检查=======================
                        return return_value

                    # 2, 拦截 if elif else 里面的 return 语句
                    # ==================if elif else里面的return =====================
                    # 是否返回了值，如果返回了，说明就不用再往下执行了
                    return_value = self.evaluate(statement)  # 遇到for in

                    # ============在if loop 等语句中遇到返回语句====================
                    if isinstance(return_value, dict) and "fight_tag" in return_value:
                        # print("dict 类型")

                        # ===================== 返回值类型检查=================
                        got_type = self.get_value_type(return_value['value'])
                        if got_type != func_dict['return_type']:
                            raise TypeError(
                                f"Function '{node.name}' expects return value to be of type '{func_dict['return_type']}' but got '{got_type}'.")
                        # ============== 类型检查=======================

                        return return_value['value']  # 直接返回返回值
                    # ==================if elif else里面的return=====================
            finally:
                # ========================恢复环境===================
                # print("previous_environment: ", previous_environment)

                # 注意：之前在执行函数的时候可能就返回值了，从而环境的恢复没有得到执行
                # 恢复之前的环境
                self.environment = previous_environment
                # print("恢复之后的环境: ", self.environment)
                # =======================返回值===================================
                # 上面的for in 循环,如果for in 遇到return,会直接返回,这里就不会执行

                if return_value is None:
                    print("func_dict: ", func_dict)
                    if func_dict['return_type'] != "void":
                        raise TypeError(
                            f"Function '{node.name}' expects return value to be of type '{func_dict['return_type']}' but got 'void'.")

            return return_value  # 确保返回函数的返回值
            # ================================================================

        else:
            # raise NameError(f"Function '{node.name}' not defined")
            return self.eval_builtin_functions(node)

    def evaluate_serial_method_call(self, node: SerialMethodCallNode):
        """
            实现连续调用
            p->show()->say()这样的调用
        """
        val = None
        for single_call in node.methods_list:
            # 调用方法
            val = self.evaluate_method_call(single_call)
        if val is not None:
            return val
        else:
            return False

    def evaluate_list_assign(self, node: ListAssignNode):
        """
            实现列表赋值
            d[index] = val;
        """
        try:
            self.environment[self.evaluate(node.list_name)][self.evaluate(node.index_expr)] = self.evaluate(
                node.value_expr)
            return True
        except:
            return False

    def evaluate_object_assign(self, node: ObjectAssignNode):
        """
            实现对象赋值
            d{"key"} = val;
        """
        obj_name = node.object_name
        obj = self.environment[obj_name]
        obj[self.evaluate(node.key_expr)] = self.evaluate(node.value_expr)

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
        # ======================字面量调用方法 ===========================
        # ""->lower()->split()这样 字面量调用方法
        if node.caller == "anonymous":
            self.environment[node.caller] = self.evaluate(node.extra)
            # =================================================
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

    def execute_by_instance_type(self, node: MethodCallNode):
        """
            根据实例的类型，调用相应的方法
        """
        # print("进入execute_by_instance_type")
        is_anonymous_call = False
        # ""->lower()->split()这样 字面量调用方法
        if node.instance_name == "anonymous":
            is_anonymous_call = True
            # ["anonymous"] = 初始值
            self.environment[node.instance_name] = self.evaluate(node.extra)

        var_value = self.environment[node.instance_name]
        # print("当前数据类型是: ", type(var_value))

        # 根据数据类型进行对应方法的调用，也就是说，这样存在一个对类型的隐士判断
        if isinstance(var_value, str):
            # print("str 实例")
            val = self.evaluate_string_type_method_call(node)
            if is_anonymous_call:
                del self.environment[node.instance_name]
            return val

        if isinstance(var_value, list):
            # print("进入list类型方法调用")
            val = self.evaluate_list_type_method_call(node)
            if is_anonymous_call:
                del self.environment[node.instance_name]
            return val

        if isinstance(var_value, dict):
            val = self.evaluate_dict_type_method_call(node)
            if is_anonymous_call:
                del self.environment[node.instance_name]
            return val

        if isinstance(var_value, set):
            val = self.evaluate_set_type_method_call(node)
            if is_anonymous_call:
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
        if method_name == "length":
            return len(self.environment[var_name])

        elif method_name == "upper":
            self.environment[var_name] = self.environment[var_name].upper()
            return self.environment[var_name]

        elif method_name == "lower":
            self.environment[var_name] = self.environment[var_name].lower()
            return self.environment[var_name]

        elif method_name == "startsWith":
            return self.environment[var_name].startswith(arguments[0])
        elif method_name == "endsWith":
            return self.environment[var_name].endswith(arguments[0])
        elif method_name == "capitalize":
            self.environment[var_name] = self.environment[var_name].capitalize()
            return self.environment[var_name]
        elif method_name == "swapcase":
            self.environment[var_name] = self.environment[var_name].swapcase()
            return self.environment[var_name]
        # 分割与连接
        elif method_name == "split":
            separator = arguments[0]
            return self.environment[var_name].split(separator)
        elif method_name == "strip":
            self.environment[var_name] = self.environment[var_name].strip()
            return self.environment[var_name]
        # 类型检查
        elif method_name == "isAlpha":
            return self.environment[var_name].isalpha()
        elif method_name == "isDigit":
            return self.environment[var_name].isdigit()
        elif method_name == "isAlphaNum":
            return self.environment[var_name].isalnum()
        elif method_name == "isSpace":
            return self.environment[var_name].isspace()
        elif method_name == "isLower":
            return self.environment[var_name].islower()
        elif method_name == "isUpper":
            return self.environment[var_name].isupper()
        elif method_name == "concat":  # 连接字符串
            self.environment[var_name] = self.environment[var_name] + arguments[0]
            return self.environment[var_name]
        elif method_name == "charAt":
            return self.environment[var_name][arguments[0]]

        elif method_name == "indexOf":
            return self.environment[var_name].find(arguments[0])

        elif method_name == "contains":
            return arguments[0] in self.environment[var_name]
        else:
            raise NameError(f"Method '{method_name}' not defined for string")

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

    # def evaluate_enum_access(self, node: EnumAccessNode):
    #     is_from_module = self.check_is_from_module(node.name)
    #     print("\n\nis_from_module(枚举): ", is_from_module, "\n")
    #
    #     # 保存旧环境
    #     old_env = self.environment.copy()
    #
    #     # 说明是来自模块的函数
    #     if isinstance(is_from_module, str):
    #         # 找到模块环境
    #         module_env = self.modules[is_from_module]
    #         print("module_env: ",module_env)  # enums里面是empty
    #
    #         # 合并模块内部的和外部的环境（核心）
    #         self.environment.update(module_env)
    #         # 使用合并后的环境进行函数调用
    #         value = self.evaluate_enum_access2(node)
    #         # 还原环境
    #         self.environment = old_env
    #         return value
    #
    #
    #     # 说明是来自 main 环境的函数
    #     elif isinstance(is_from_module, bool):
    #         # 调用函数
    #         value = self.evaluate_enum_access2(node)
    #         return value

    def evaluate_enum_access(self, node: EnumAccessNode):
        """
            let x = enum::Color.Red;
            EnumAccessNode(name=Color, value=Red)
            task:
                检查访问的属性是否存在于枚举类中，
                1，存在；返回值
                2，不存在；raise NameError
        """
        # 检擦枚举类是否存在

        if node.enum_name not in self.environment["enums"]:
            raise NameError(f"Enum {node.enum_name} not found!")
        if node.enum_property not in self.environment["enums"][node.enum_name]:
            raise NameError(f"Enum property '{node.enum_property}' not found in {node.enum_name}!")
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

        struct_dict = self.environment[node.struct_instance_name]
        # struct_dict 比如: {'type': 'struct', 'name': 'Point', 'value': {'x': 1, 'y': 2}}
        print("struct_dict: ", struct_dict)

        # 访问不存在的属性
        # if node.field_name not in struct_dict["value"]:
        #     return False
        # return struct_dict["value"][node.field_name]
        print("node.fields_names: ", node.fields_names)

        # 访问单一一个属性 p::x
        if node.field_name is not None:
            if node.field_name not in struct_dict:
                raise NameError(f"struct {node.struct_instance_name} has no field '{node.field_name}'!")
            return struct_dict[node.field_name]

        # 连续访问多个属性： p::x::y
        if len(node.fields_names) > 1:
            # 连续访问多个属性
            # for field_name in node.fields_names:
            for idx in range(len(node.fields_names)):
                field_name = node.fields_names[idx]
                if field_name not in struct_dict:
                    raise NameError(f"struct {node.struct_instance_name} has no field '{field_name}'!")
                struct_dict = struct_dict[field_name]
                # 最后一个属性
                if idx == len(node.fields_names) -1:
                    return struct_dict







    def evaluate_struct_assign(self, node: StructAssignNode):

        # 检查结构体是否存在
        if node.struct_name not in self.environment["structs"]:
            raise NameError(f"struct  {node.struct_name} not found!")

        # 检查结构体是否有这个属性: 不能瞎赋值
        for field_name in node.struct_fields_values:
            if field_name not in self.environment["structs"][node.struct_name]:
                raise NameError(f"struct {node.struct_name} has no field '{field_name}'!")

        result = {
            "type": "struct",
            "name": f"{node.struct_name}",
            "value": {}
        }
        for field_name in node.struct_fields_values:
            field_value = self.evaluate(node.struct_fields_values[field_name])
            result["value"][field_name] = field_value
        return result["value"]

    def evaluate_struct_declaration(self, node: StructDeclarationNode):
        """
            将结构体的名称放到env中，以便后续使用
        :param node:
        :return:
        """
        # ========类型检查============================

        # 第一次声明：
        # 将结构体的类型声明放到self.types中
        self.environment["types"][node.name] = node.fields_types
        # ========类型检查============================

        if node.struct_name in self.environment["structs"]:
            raise NameError(f"Struct '{node.struct_name}' already exists!")
        self.environment["structs"][node.struct_name] = node.fields

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
        # previous_environment = self.environment.copy()

        # 设置初始变量
        self.environment[node.var_name] = -100
        print("for in语句的var: ", self.environment[node.var_name], " var 是 ", node.var_name)

        # return {"fight_tag": True, "value": self.evaluate(statement.value)}  # 直接返回返回值
        #

        # for(idx: 1..10){} 递增类型
        if start_value < end_value:
            # 遍历每个元素
            for i in range(start_value, end_value + 1):
                # print("i = ",i)
                self.environment[node.var_name] = i
                try:
                    for statement in node.body:
                        val = self.evaluate(statement)
                        # 返回值的形式：{'fight_tag': True, 'value': 5}
                        if isinstance(val, dict) and "fight_tag" in val:
                            return val["value"]
                except BreakException:
                    break

        # for(idx: 10..1){} 倒退类型
        # 原来的代码
        # for statement in node.body:
        #     self.evaluate(statement)

        # 修改的代码
        if start_value > end_value:
            # 遍历每个元素
            for i in range(start_value, end_value - 1, -1):
                # print("i = ",i)
                self.environment[node.var_name] = i
                try:
                    for statement in node.body:
                        val = self.evaluate(statement)
                        # 返回值的形式：{'fight_tag': True, 'value': 5}
                        if isinstance(val, dict) and "fight_tag" in val:
                            return val["value"]
                except BreakException:
                    break
        print("for in结束后")
        # 还原环境变量
        # self.environment = previous_environment.copy()

    def evaluate_interface_declaration(self, node: InterfaceNode):
        # 处理接口定义: 将接口加入到environment中, 类实现的时候要用到
        # {"接口名称":[方法名称1,方法名称2,...]}
        # self.environment["interfaces"][node.interface_name] = node.methods

        interface_lst = []
        for method_name in node.methods:
            interface_lst.append(
                {
                    method_name: {
                        "return_type": node.return_type,
                        "params_types": node.params_types
                    }
                }
            )

        self.environment["interfaces"][node.interface_name] = interface_lst

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

    def evaluate_deconstruct_assign(self, node: DecontructAssignNode):
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

    def evaluate_call_class_inner_method(self, node: CallClassInnerMethod, outer_instance_name=None):
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

        # 如果有外层的实例，则使用外层的实例
        if outer_instance_name is not None:
            instance_name = outer_instance_name

        # print("current_object: ", self.current_object)
        # 方法名称
        method_name = node.method_name
        # 调用方法的参数
        args_pass_in = [self.evaluate(arg) for arg in node.arguments]

        # ========处理命名参数=================
        named_args_pass_in = {}
        for arg in node.named_args:
            named_args_pass_in[arg] = self.evaluate(node.named_args[arg])
        print("named_args_pass_in(this->xx()): ", named_args_pass_in)
        # ========处理命名参数=================

        # 找到instance_name的实例
        instance_dict = self.environment["instances"][instance_name]
        # print(f"instance_dict: {instance_name}的定义  ", instance_dict)

        # ========= 参数类型检查================
        # 找到方法的定义
        method_prototype = self.environment["objects"][instance_dict["parent_name"]]["methods"][method_name]
        params_types = method_prototype['params_types']

        index = 0
        for param_name in params_types:
            # print("param_name: ",param_name)
            if index < len(args_pass_in):
                if self.get_value_type(args_pass_in[index]) != params_types[param_name]:
                    raise TypeError(
                        f"Method {instance_name}->{method_name}() parameter {param_name} type is {params_types[param_name]}, but got {self.get_value_type(args_pass_in[index])}")
                index += 1
        # ========= 参数类型检查================

        # 找到方法的定义
        method_dict = instance_dict["methods"][method_name]
        # print(f"method_dict: {method_name}的定义  ", method_dict)

        # 合并位置参数和命名参数
        final_args_pass_in = {**dict(zip(method_dict['args'], args_pass_in)), **named_args_pass_in}
        # 设置默认参数
        for param, default_value in method_dict['default_values'].items():
            if param not in final_args_pass_in:
                final_args_pass_in[param] = self.evaluate(default_value)


        # 保存旧环境
        old_env = self.environment

        # 创建新环境，包含实例字段和方法参数
        self.environment = {
            **old_env,  # 包含全局环境,是指可以访问类外面的变量
            **instance_dict['fields'],
            # **dict(zip(method_dict['args'], args_pass_in)),  # 原来的
            **final_args_pass_in,  # 现在的
            # "constants": []  # 记录声明的常量
        }

        # 执行方法体
        result = None
        for statement in method_dict['body']:
            print("执行语句(call_class_inner_method)=======>  ", statement, "\n")

            # ======如果是对实例属性的修改，需要进行赋值的检查=======
            if isinstance(statement, ReAssignmentNode):
                # 找到字段的类型
                if statement.name in self.environment["objects"][instance_dict["parent_name"]]["fields_types"]:
                    fields_types = self.environment["objects"][instance_dict["parent_name"]]["fields_types"]
                    # 校验赋值的类型
                    if self.get_value_type(self.evaluate(statement.value)) != fields_types[statement.name]:
                        raise TypeError(
                            f"Field {statement.name} type is {fields_types[statement.name]}, but got {self.get_value_type(self.evaluate(statement.value))}  '{self.evaluate(statement.value)}'     ")
            # ======如果是对实例属性的修改，需要进行赋值的检查=======

            result = self.evaluate(statement)
            # 更新实例字段————每每执行一条语句之后，因为可能某一条语句就直接更新了实例字段，所以需要更新实例字段
            for field_name in instance_dict['fields']:
                if field_name in self.environment:
                    instance_dict['fields'][field_name] = self.environment[field_name]

        # 恢复旧环境
        self.environment = old_env

        # ====== 检查返回值和声明的返回值=====
        if result is None:
            class_prototype_dict = self.environment["objects"][instance_dict["parent_name"]]
            method_prototype_dict = class_prototype_dict['methods'][node.method_name]
            class_method_return_type = method_prototype_dict['return_type']
            if class_method_return_type != "void":
                raise TypeError(
                    f"Method this->{method_name}() return type should be {class_method_return_type}, but got void")
        # ====== 检查返回值和声明的返回值=====

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
        # ====================version 2============================================
        print("caller: ", node.instance_name)

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
            print("method_dict: ", method_dict)

            # 位置参数
            args_pass_in = [self.evaluate(arg) for arg in node.arguments]

            # ===========命名参数===================
            # 命名参数: 默认参数放在了method_dict['default_values']中
            named_args_pass_in = {}
            for arg in node.named_args:
                named_args_pass_in[arg] = self.evaluate(node.named_args[arg])
            print("named_args_pass_in: ", named_args_pass_in)

            # 合并位置参数和命名参数
            final_args_pass_in = {**dict(zip(method_dict['args'], args_pass_in)), **named_args_pass_in}

            # 设置默认参数
            for param, default_value in method_dict['default_values'].items():
                if param not in final_args_pass_in:
                    final_args_pass_in[param] = self.evaluate(default_value)
            # ===========命名参数===================

            # ======================传入参数检查=================
            # static方法的返回值
            class_method_return_type = method_dict['return_type']

            # index = 0
            # for param_name in method_dict['params_types']:
            #     print("param_name: ",param_name)
            # if self.get_value_type(args_pass_in[index]) != method_dict['params_types'][param_name]:
            #     raise TypeError(
            #         f"Method {class_name}->{method_name}() parameter {param_name} type is {method_dict['params_types'][param_name]}, but got {self.get_value_type(args_pass_in[index])}")
            # index += 1
            # ======================传入参数检查=================

            # 保存旧环境
            old_env = self.environment
            # 创建新环境，包含方法参数
            self.environment = {
                **old_env,  # 包含全局环境,是指可以访问类外面的变量
                # **dict(zip(method_dict['args'], args_pass_in)),  # 原来的
                **final_args_pass_in,  # 现在的
                # "constants": []  # 记录声明的常量
            }
            # 执行方法体
            result = None
            for statement in method_dict['body']:
                result = self.evaluate(statement)
            # 恢复旧环境
            self.environment = old_env

            # =========返回值检查====================
            # if elif else里面的返回值
            if isinstance(result, dict) and "fight_tag" in result:
                # print("result: ", result)
                if self.get_value_type(result["value"]) != class_method_return_type:
                    raise TypeError(
                        f"Method {caller}->{method_name}() return type is {class_method_return_type}, but got {self.get_value_type(result['value'])}")
            else:
                # 非if else语句里面的返回值
                # 校验返回值类型
                type_val = self.get_value_type(result)
                if self.get_value_type(result) == "NoneType":
                    type_val = "void"
                if type_val != class_method_return_type:
                    raise TypeError(
                        f"Method {caller}->{method_name}() return type should be {class_method_return_type}, but got {self.get_value_type(result)}")

            # =========返回值检查====================

            if isinstance(result, dict) and "fight_tag" in result:
                return result["value"]
            else:
                return result
        # ====================类调用方法结束============================================




        # ====== ====================== 实例方法调用===============================
        method_name = node.method_name

        # 位置参数
        args_pass_in = [self.evaluate(arg) for arg in node.arguments]

        # ===========命名参数===================
        # 命名参数
        named_args_pass_in = {}
        for arg in node.named_args:
            named_args_pass_in[arg] = self.evaluate(node.named_args[arg])

        # ===========命名参数===================

        print("named_args_pass_in: ", named_args_pass_in)
        print("args_pass_in: ", args_pass_in)

        # 判断是不是private方法，如果是，拒绝访问
        if method_name[0].islower():
            raise NameError(f"Method {caller}->{method_name}() is not public. Access denied.")

        return_type = None  # 方法的返回类型

        try:
            # 尝试找到该对象
            # 实例对象的所有东西
            instance_dict = self.environment["instances"][caller]
            # 对象的所有方法
            method_dict = instance_dict["methods"][method_name]

            # 合并位置参数和命名参数
            final_args_pass_in = {**dict(zip(method_dict['args'], args_pass_in)), **named_args_pass_in}
            # 设置默认参数
            for param, default_value in method_dict['default_values'].items():
                if param not in final_args_pass_in:
                    final_args_pass_in[param] = self.evaluate(default_value)


            # ==============传入参数检查=======================
            class_prototype_dict = self.environment["objects"][instance_dict["parent_name"]]
            method_prototype_dict = class_prototype_dict['methods'][method_name]

            return_type = method_prototype_dict['return_type']
            params_types = method_prototype_dict['params_types']

            index = 0
            for param_name in params_types:
                # print("param_name: ",param_name)
                # print("self.get_value_type(args_pass_in[index]): ",self.get_value_type(args_pass_in[index]))
                # print("params_types[param_name]: ",params_types[param_name],"\n\n")

                # 需要处理默认参数的情况，也就是index out of range的情况
                if index < len(args_pass_in) and self.get_value_type(args_pass_in[index]) != params_types[param_name]:
                    raise TypeError(
                        f"Method {caller}->{method_name}() parameter {param_name} type is {params_types[param_name]}, but got {self.get_value_type(args_pass_in[index])}")
                index += 1
            # ================传入参数检查=====================

        except KeyError:
            # 找不到该对象
            raise NameError(f"Object {caller} not found.")

        # 保存旧环境
        old_env = self.environment

        # ================原来的代码=====================================
        # 创建新环境，包含实例字段和方法参数
        # self.environment = {
        #     **old_env,  # 包含全局环境,是指可以访问类外面的变量
        #     **instance_dict['fields'],
        #     **dict(zip(method_dict['args'], args_pass_in)),
        #     # "constants": []  # 记录声明的常量
        # }

        # =============================test==============================
        new_env = {
            **old_env,  # 包含全局环境
            **instance_dict['fields'],
            # **dict(zip(method_dict['args'], args_pass_in)),  原来的
            **final_args_pass_in,  # 现在的
        }

        # 新增：将参数也添加到 instances 字典中
        if 'instances' not in new_env:
            new_env['instances'] = {}
        for arg_name, arg_value in zip(method_dict['args'], args_pass_in):
            # 判断是不是实例对象
            if isinstance(arg_value, dict) and "fields" in arg_value:
                new_env['instances'][arg_name] = arg_value

        self.environment = new_env
        # ===============================test============================

        # 执行方法体
        result = None
        for statement in method_dict['body']:
            # ====== 检查语句是否是对字段进行重新赋值语句： 检查赋值的类型=======
            if isinstance(statement, ReAssignmentNode):
                # 找到字段的类型
                if statement.name in self.environment["objects"][instance_dict["parent_name"]]["fields_types"]:
                    fields_types = self.environment["objects"][instance_dict["parent_name"]]["fields_types"]
                    # 校验赋值的类型
                    if self.get_value_type(self.evaluate(statement.value)) != fields_types[statement.name]:
                        raise TypeError(
                            f" {caller}->{statement.name}'s type is {fields_types[statement.name]}, but got {self.get_value_type(self.evaluate(statement.value))}  '{self.evaluate(statement.value)}' ")
                # ====== 检查语句是否是对字段进行重新赋值语句： 检查赋值的类型=======
            result = self.evaluate(statement)
            # if isinstance(statement,ReturnNode):
            #     break
            # 更新实例字段————每每执行一条语句之后，因为可能某一条语句就直接更新了实例字段，所以需要更新实例字段
            for field_name in instance_dict['fields']:
                if field_name in self.environment:
                    instance_dict['fields'][field_name] = self.environment[field_name]
        # 恢复旧环境
        self.environment = old_env

        # if elif else里面的返回值
        if isinstance(result, dict) and "fight_tag" in result:
            if self.get_value_type(result["value"]) != return_type:
                raise TypeError(
                    f"Method {caller}->{method_name}() return type is {return_type}, but got {self.get_value_type(result['value'])}")
        else:
            # 非if else语句里面的返回值
            # 校验返回值类型
            if return_type == "void":
                pass
            elif self.get_value_type(result) != return_type:
                raise TypeError(
                    f"Method {caller}->{method_name}() return type is {return_type}, but  nothing is returned at all ! ")

        # 返回值
        if isinstance(result, dict) and "fight_tag" in result:
            return result["value"]
        else:
            return result

    def evaluate_new_object_expr2(self, node: NewObjectNode):
        """
            从environment中获取类定义，就是复制属性、方法、及其init
        """
        # print("node: ", node)

        # 用于存储实例化后的对象
        global delay_caller
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

            # 处理init  (多个init函数)
            # original_class_definition['init']: [
            #   {'args': ['name', 'age'], 'body': [
            #               AssignmentNode(name=Name, value=VariableNode(value=name), is_constant=False),
            #               AssignmentNode(name=Age, value=VariableNode(value=age), is_constant=False)], 'default_values': {}},
            #   {'args': ['age'], 'body': [
            #                                         AssignmentNode(name=Age, value=VariableNode(value=age),
            #                                                        is_constant=False)], 'default_values': {}}]
            # #

            # # ======================= 找到匹配的init函数 ========
            # arg_len = len(node.arguments)  # 传进来的参数个数
            # print("arg_len: ", arg_len)
            # # 如果包含多个Init（保存到list里面）
            # if isinstance(original_class_definition['init'], list):
            #     for init in original_class_definition['init']:
            #         print("init[args]: ",init["args"])
            #         if len(init['args']) == arg_len:
            #             original_class_definition['init'] = init
            #
            # # ======================= 找到匹配的init函数 ========
            # print("original_class_definition['init']: ", original_class_definition['init'])
            #
            # # print("original_class_definition['init']: ", original_class_definition['init'])
            # if original_class_definition['init']:
            #     init_args = original_class_definition['init']['args']
            #     init_body = original_class_definition['init']['body']
            #     init_default_values = original_class_definition['init']['default_values']
            #     return_instance["init"] = {
            #         "args": init_args,
            #         "body": init_body,
            #         "default_values": init_default_values
            #     }
            arg_len = len(node.arguments)
            # print("arg_len: ", arg_len)

            # 选择匹配的构造函数
            matching_init = None
            if isinstance(original_class_definition['init'], list):
                for init in original_class_definition['init']:
                    if len(init['args']) == arg_len:
                        matching_init = init
                        break
            else:
                matching_init = original_class_definition['init']

            if matching_init is None:
                raise ValueError(f"No matching constructor found for {arg_len} arguments")

            # 使用匹配的构造函数
            init_args = matching_init['args']
            init_body = matching_init['body']
            init_default_values = matching_init.get('default_values', {})

            print("node xxx: ")

            return_instance["init"] = {
                "args": init_args,
                "body": init_body,
                "default_values": init_default_values
            }

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

            # init里面的this->xxx()类方法
            delay_calls = []
            delay_caller = None

            # 2, 处理非赋值语句
            for statement in init_body:
                # 再遇到赋值语句额时候发生错误，因为已经赋值过了，所以这里不再处理对字段的赋值语句
                if isinstance(statement, AssignmentNode) and statement.name in return_instance["fields"]:
                    return_instance["fields"][statement.name] = self.evaluate(statement.value)



                else:
                    # 思路：如果遇到SuperNode, 就往init_body里面追加赋值语句！
                    if isinstance(statement, SuperNode):
                        # 设置super指向的当前实例（调用super实际上是对当前实例的父类属性进行赋值）
                        # statement.cur_instance_name = node.object_name
                        for field in statement.key_value_pairs:
                            init_body.append(
                                AssignmentNode(name=field, value=statement.key_value_pairs[field])
                            )
                        continue

                    # this->xxx() 解析
                    if isinstance(statement, CallClassInnerMethod):
                        delay_calls.append(statement)
                        delay_caller = node.object_name
                        continue

                    # 和SuperNode平级
                    self.evaluate(statement)  # 处理语句，比如函数调用、赋值语句等
            # 回复旧环境
            self.environment = old_env
        # =======================处理对象调用方法===============================
        # 将 实例对象放到 environment 中
        self.environment["instances"][node.object_name] = return_instance
        # print("environment: ", self.environment)
        # ======================================================
        # print("env: ",self.environment)
        # print("\ndelay_call: ",delay_calls,"\n")

        # 处理延迟调用： 在这里实例化的对象才在env中，所以才能处理this->xxx()类方法
        for this_call_in_init in delay_calls:
            self.evaluate_call_class_inner_method(this_call_in_init, delay_caller)

        return return_instance

    # 该方法是claude3.5给出的版本，修改了evaluate_new_object_expr2方法没法在init里面访问字段的bug
    def evaluate_new_object_expr(self, node: NewObjectNode):
        """
        目标： let p: Person = new Person("Alice", 20);


        从environment中获取类定义，就是复制属性、方法、及其init
        """
        print("newobjectnode: ", node, "\n\n")
        global delay_caller
        return_instance = {
            "fields": {},
            "methods": {},
            "init": {},
            "parent_name": node.class_name,
            "fields_annotations": {},
        }
        class_name = node.class_name

        # 先获取类定义, 也就是类的原型
        if class_name not in self.environment["objects"]:
            raise NameError(f"Class '{class_name}' not found.")
        original_class_definition = self.environment["objects"][class_name]

        # 处理fields
        for field_name in original_class_definition['fields']:
            field_value = original_class_definition['fields'][field_name]
            return_instance["fields"][field_name] = field_value

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
                "annotations": original_class_definition['methods'][method_name]["annotations"],
                "args": method_args,
                "body": method_body,
                "default_values": method_default_values,
            }

        # 选择匹配的构造函数
        arg_len = len(node.arguments)
        matching_init = None
        if isinstance(original_class_definition['init'], list):
            for init in original_class_definition['init']:
                if len(init['args']) == arg_len:
                    matching_init = init
                    break
        else:
            matching_init = original_class_definition['init']

        if matching_init is None:
            raise ValueError(f"No matching constructor found for {arg_len} arguments")

        # =========== 使用匹配的构造函数==============

        # ======构造函数传入参数类型检查===========
        init_arg_names = matching_init['args']
        # print("init_args: ", init_arg_names)
        # print("node.arguments: ", node.arguments)
        # print("params_types: ", matching_init['params_types'])
        # real_args是实参
        real_args = [self.evaluate(arg) for arg in node.arguments]
        for real_arg in real_args:
            # 比较实参和形参的类型
            if self.get_value_type(real_arg) != matching_init['params_types'][
                init_arg_names[real_args.index(real_arg)]]:
                raise TypeError(
                    f"In the init method of {class_name}, the parameter '{init_arg_names[real_args.index(real_arg)]}' type is {matching_init['params_types'][init_arg_names[real_args.index(real_arg)]]}, but got '{self.get_value_type(real_arg)}'  ")
        # ======参数类型检查===========

        init_args = matching_init['args']
        init_body = matching_init['body']
        init_default_values = matching_init.get('default_values', {})
        return_instance["init"] = {
            # "params_types": {},
            "args": init_args,
            "body": init_body,
            "default_values": init_default_values
        }

        # 创建新环境，包含类的字段
        new_env = {
            "constants": [],
            "objects": {},
        }

        # 将类的字段添加到新环境中
        for field_name, field_value in return_instance["fields"].items():
            new_env[field_name] = field_value

        # 记录旧环境
        old_env = self.environment
        self.environment = new_env

        # 将传进来的参数放到新环境里面
        for i in range(len(node.arguments)):
            arg_name = init_args[i]
            arg_value = self.evaluate(node.arguments[i])
            self.environment[arg_name] = arg_value

        # init里面的this->xxx()类方法
        delay_calls = []
        delay_caller = None

        # 处理init函数体
        for statement in init_body:
            if isinstance(statement, AssignmentNode) and statement.name in return_instance["fields"]:
                # 更新字段值
                value = self.evaluate(statement.value)
                self.environment[statement.name] = value
                return_instance["fields"][statement.name] = value
            elif isinstance(statement, SuperNode):
                # 处理SuperNode
                for field in statement.key_value_pairs:
                    init_body.append(
                        AssignmentNode(name=field, value=statement.key_value_pairs[field])
                    )
            elif isinstance(statement, CallClassInnerMethod):
                # 处理this->xxx()调用
                delay_calls.append(statement)
                delay_caller = node.object_name
            else:
                self.evaluate(statement)

        # 将更新后的字段值复制回return_instance
        for field_name in return_instance["fields"]:
            if field_name in self.environment:
                return_instance["fields"][field_name] = self.environment[field_name]

        # 恢复旧环境
        self.environment = old_env

        # 将实例对象放到environment中
        self.environment["instances"][node.object_name] = return_instance

        # 处理延迟调用
        for this_call_in_init in delay_calls:
            self.evaluate_call_class_inner_method(this_call_in_init, delay_caller)

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
            "fields_annotations": {},
            "fields_types": {}  # 字段的类型 {字段名称:类型}
        }

        # print(" \n node---------------------> ", node,"\n")

        # ====================static 类型属性============================================
        for field_name in node.static_fields:
            # field_name = field.name
            field_value = self.evaluate(node.static_fields[field_name])

            # ========= 类型检查==========
            # print("\nfields_types(static): ",node.fields_types,"\n")
            if self.get_value_type(field_value) != node.fields_types[field_name]:
                raise TypeError(
                    f"The type of static field '{field_name}' should be '{node.fields_types[field_name]}', but '{self.get_value_type(field_value)}' found.")

            # ========= 类型检查==========

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
                    "return_type": method_dict.return_type,
                    "params_types": method_dict.params_types,
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

            # 将字段类型加入到class_dict中
            class_dict['fields_types'][field_name] = node.fields_types[field_name]
            if self.get_value_type(field_value) != node.fields_types[field_name]:
                raise ValueError(
                    f"The type of field '{field_name}' should be '{node.fields_types[field_name]}', but '{self.get_value_type(field_value)}' found.")

        # fields的形式:  {'name': 'Alice', 'Age': 25}
        # print("fields: ", class_dict['fields'])

        # ==============处理方法===================
        for method_name in node.methods:
            # print("node.methods[method_name].annotations= =================> ", node.methods[method_name].annotations,
            #       "\n")
            class_dict['methods'][method_name] = {
                # 注解注解
                "return_type": node.methods[method_name].return_type,
                "params_types": node.methods[method_name].params_types,
                "annotations": node.methods[method_name].annotations,
                'args': node.methods[method_name].args,
                'body': node.methods[method_name].body,
                "default_values": node.methods[method_name].default_values,
            }
        # print("class_dict(methods): ", class_dict['methods'])

        # ================ 处理初始化函数=================================
        # print("node.init: ", node.init)
        if isinstance(node.init, list):
            inits = []
            for init in node.init:
                inits.append({
                    "params_types": init.params_types,
                    'args': init.args,
                    'body': init.body,
                    "default_values": init.default_values,

                })
            class_dict['init'] = inits

        else:
            # 只有一个初始化函数
            # if node.init:
            class_dict['init'] = {
                # 构造函数的参数
                "params_types": node.init.params_types,

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
            # print(type(node.parent_name))
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
        for interface_name in node.interfaces:
            # 先获取接口定义
            if interface_name not in self.environment["interfaces"]:
                raise ValueError(f"Interface '{interface_name}' is not defined.")
            # interface_list: 类要实现的接口的列表
            interface_list = self.environment["interfaces"][interface_name]

            # 遍历接口定义中的方法，判断类中是否有实现
            for method_dict_from_interface in interface_list:
                method_name_from_interface = list(method_dict_from_interface.keys())[0]
                # print("method_name: ", method_name_from_interface)
                if method_name not in class_dict['methods']:
                    raise NotImplementedError(
                        f"Class '{class_name}' have not implemented method '{method_name_from_interface}' declared in interface '{interface_name}'")
                # ===== 处理返回值、参数的类型问题： 是否和接口一致========

                for method_name in node.methods:
                    if method_name == method_name_from_interface:

                        method_dict1 = node.methods[method_name]
                        # 返回类型的检查
                        method_return_type = method_dict1.return_type
                        # 返回类型检查: 方法返回值 ！= 接口定义的返回值
                        interface_return_type = method_dict_from_interface[method_name_from_interface]["return_type"]
                        if method_return_type != interface_return_type:
                            raise TypeError(
                                f"The return type of method '{method_name_from_interface}' in class '{class_name}' should be '{method_dict_from_interface[method_name_from_interface]['return_type']}', but '{method_return_type}' found.")

                        method_params_types = method_dict1.params_types
                        interface_params_types = method_dict_from_interface[method_name_from_interface]["params_types"]

                        method_params_types_list = list(method_params_types.values())
                        # 个数匹配
                        if len(method_params_types_list) != len(interface_params_types):
                            raise TypeError(
                                f"The number of parameters of method '{method_name_from_interface}' in class '{class_name}' should be '{len(method_dict_from_interface[method_name_from_interface]['params_types'])}', but '{len(method_params_types_list)}' found.")

                        # 按位置：逐个类型匹配
                        index = 0
                        for param_type in method_params_types_list:
                            if param_type != interface_params_types[index]:
                                raise TypeError(
                                    f"The parameter  type of method '{method_name_from_interface}' in class '{class_name}' should be '{method_dict_from_interface[method_name_from_interface]['params_types'][index]}', but '{param_type}' found.")
                            index += 1
                # ===== 处理返回值、参数的类型问题： 是否和接口一致========

        # ========================处理接口实现问题===============================

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

        # 保存之前的环境变量func
        previous_environment = self.environment.copy()

        # 设置初始变量
        self.environment[node.variable] = "xxxx"
        iter_obj = self.evaluate(node.iteration_obj)

        """
                        try:
                            self.evaluate(statement)
                        except BreakException:
                            break
        """

        # # 遍历每个元素
        # for item in iter_obj:
        #     self.environment[node.variable] = item
        #     try:
        #         for statement in node.body:
        #             self.evaluate(statement)
        #     except BreakException:
        #         break
        # 还原环境变量
        # self.environment = previous_environment.copy()

        # ============================================================

        # 外层的except是在收到break后跳出元素遍历

        for item in iter_obj:
            try:
                # 遍历每个元素
                self.environment[node.variable] = item
                for statement in node.body:
                    try:
                        result = self.evaluate(statement)

                        # # 遇到返回语句
                        if isinstance(result, dict) and "fight_tag" in result:
                            return result  # 直接返回值，结束循环
                    except BreakException:
                        raise BreakException("break")  # 重新抛出异常，结束循环
            except BreakException:
                break
            finally:
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

        # 为了解决在main env声明的函数没有被放到main env的问题，
        # 注释掉了下面的代码，下面的代码好像是来处理传入箭头函数、匿名函数函数的？？

        # =========================================
        # 处理函数里面传入匿名、箭头函数的？？？

        # # 先看看是不是在环境中已经存在了
        # if node.name in self.environment:
        #     print("node.name??: ", node.name)
        #     # raise NameError(f"Function '{node.name}' already defined")
        #     # ==================================================
        #     if node.tag is None:  # 函数表示作为参数进行传递
        #         print("tag为none - 遇到的节点: ",node.name,"\n\n")
        #         # print("收到tag是none的节点: ",node)
        #         return {
        #             "annotations": annot,
        #             "args": node.args,
        #             "body": node.body,
        #             "defaults": node.default_values,  # 假设在 AST 中传递默认值
        #         }
        #     raise NameError(f"Function '{node.name}' already defined")
        # ============================================================

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
        # ======= 检查默认值和类似声明是否一致==========
        # 暂时不做

        # ======= 检查默认值和类似声明是否一致==========

        # ================修改后=====================
        result = {
            # "name": node.name,
            "return_type": node.return_type,  # 假设在 AST 中传递返回值类型
            "params_types": node.params_types,  # 假设在 AST 中传递参数类型
            "annotations": annot,
            "args": node.args,
            "body": node.body,
            #
            "defaults": node.default_values,  # 假设在 AST 中传递默认值
        }

        # ==============类型检查===============================
        # 判断是否已经赋过值
        if node.name in self.environment["types"]:  # 已经赋过值，需要检查最新的赋值的值的类型是否一致
            print("\ntypes: ", self.environment["types"])

            if self.environment["types"][node.name] == "any":
                pass
            else:  # 已有的类型  !=  新的类型
                if self.environment["types"][node.name] != self.get_value_type():
                    raise TypeError(
                        f"Cannot reassign variable '{node.name}' with a different type: {self.get_value_type(node=node)}")

        # =============================================

        if node.name in self.environment:
            raise NameError(f"Function '{node.name}' already defined")
        # 保存函数到环境中
        self.environment[node.name] = result
        return result

    def evaluate_if_statement(self, node):
        condition_value: bool = self.evaluate(node.condition)

        if condition_value:
            for statement in node.if_body:
                if isinstance(statement, ReturnNode):
                    return {"fight_tag": True, "value": self.evaluate(statement.value)}
                else:
                    val = self.evaluate(statement)
                    if isinstance(val, dict) and val.get("fight_tag"):
                        return val["value"]
            return  # 添加这行，if 块执行完就返回

        for elseif_dict in node.elif_:
            condition_value: bool = self.evaluate(elseif_dict['condition'])
            if condition_value:
                elif_statements = elseif_dict['elif_statements']
                for statement in elif_statements:
                    if isinstance(statement, ReturnNode):
                        return {"fight_tag": True, "value": self.evaluate(statement.value)}
                    val = self.evaluate(statement)
                    if isinstance(val, dict) and val.get("fight_tag"):
                        return val["value"]
                return  # 添加这行，elif 块执行完就返回

        # 只有当所有 if 和 elif 条件都为假时，才执行 else 块
        else_statements = node.else_
        for statement in else_statements:
            if isinstance(statement, ReturnNode):
                return {"fight_tag": True, "value": self.evaluate(statement.value)}
            else:
                val = self.evaluate(statement)
                if isinstance(val, dict) and val.get("fight_tag"):
                    return val["value"]

    def evaluate_object(self, node):
        print("遇到的节点: ", node)
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

    def evaluate_variable(self, node: VariableNode):
        """
            变量存放在list里面
        """
        if node.value in self.environment:
            return self.environment[node.value]
        else:
            raise NameError(f"Variable '{node.value}' not defined")

        # 尝试在temp_env中查找
        # if node.name in self.temp_env:
        #     return self.temp_env[node.name]

    def evaluate_unary_op(self, node: UnaryOpNode):
        # 操作数 operand
        # 运算符 operator
        operand = self.evaluate(node.operand)
        # print("operand: ", operand)
        if node.operator == "not":
            return not operand

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

    def evaluate_reassignment(self, node: ReAssignmentNode):

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
            # 第2次赋值：
            # 类型检查
            self.environment["types"] = {}
            if node.name in self.environment["types"]:  # 已经赋过值，需要检查最新的赋值的值的类型是否一致
                # 已有的类型  !=  新的类型
                if self.environment["types"][node.name] != "any":
                    # 声明的类型 ！=  赋值的类型
                    if self.environment["types"][node.name] != self.get_value_type(node.value):
                        raise TypeError(
                            f"Cannot reassign variable '{node.name}' with a different type: {self.get_value_type(node.value, node.data_type)}")


        else:
            # =======================常量检查===============================
            if node.name in self.environment['constants']:
                raise ValueError(f"Constant '{node.name}' cannot be reassigned")
                # 如果当前节点是常量，加入到constants列表中, 用于检查是否重复赋值

            # 否则，直接求值
            value = self.evaluate(node.value)
            # ===================== 增加类型系统===========================
            # 判断是否已经赋过值
            # print("node.name: ", node.name)
            # print("env: ", self.environment)

            if "types" in self.environment and node.name in self.environment["types"]:  # 已经赋过值，需要检查最新的赋值的值的类型是否一致
                if self.environment["types"][node.name] == "any":
                    pass
                else:  # 已有的类型  !=  新的类型
                    if self.environment["types"][node.name] != self.get_value_type(value):
                        raise TypeError(
                            f"Cannot reassign variable '{node.name}' with a new type: {self.get_value_type(value)}")

            # 判断声明的类型、赋值的类型是否一致
            # if isinstance(node, AssignmentNode) and node.data_type is not None:
            #     print("node.data_type: ", node.data_type)
            #     print("got type: ", self.get_value_type(value, node.data_type))
            #     got_type = self.get_value_type(value, node.data_type)
            #
            #     # print("传进去的value: ", value)
            #     if node.data_type != got_type:  # 需要得到Color类型
            #         raise TypeError(f"the given value of variable '{node.name}' is not '{node.data_type}' ")
            #
            # self.environment["types"][node.name] = self.get_value_type(value, node.data_type)
            # ===================== 增加类型系统============================
            # 赋值
            self.environment[node.name] = value
            return value

    def is_this_struct(self, struct_name, potential_struct_dict):
        """
            判断一个dict的字段是否和某个结构体一致，
            True / False
        """
        if struct_name not in self.environment["types"]:
            raise NameError(f"Struct '{struct_name}' not defined")

        struct_prototype = self.environment["types"][struct_name]
        for key in potential_struct_dict:
            if key not in struct_prototype:
                return False
            if self.get_value_type(potential_struct_dict[key]) != struct_prototype[key]:
                return False

        for key in struct_prototype:
            if key not in potential_struct_dict:
                return False
        return True

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
        print("node???: ", node)

        if isinstance(node.value, ObjectNode):
            data_type = node.data_type

            # 结构体的定义
            # data_type_prototype:  {'x': 'int', 'y': 'int', 'd3': 'D3'}
            data_type_prototype = self.environment["types"][data_type]
            print("data_type_prototype: ", data_type_prototype)

            print("data_type: ", data_type)
            node1: ObjectNode = node.value
            print("node1: ", node1, "\n")

            # 结构体的赋值
            properties = {k: self.evaluate(v) for k, v in node1.k_v.items()}
            for key in properties:
                # 判断属性是否存在
                if key not in data_type_prototype:
                    raise TypeError(f"the field '{key}' is not defined in the class '{data_type}' ")
                print("properties[key]: ", properties[key])

                # 判断是不是某个结构体
                if isinstance(properties[key], dict):
                    struct_name = data_type_prototype[key]
                    print("enter")
                    if not self.is_this_struct(struct_name, properties[key]):
                        raise TypeError(
                            f"the field '{key}' is not a '{struct_name}', please check if the object is a '{struct_name}' ")
                if not isinstance(properties[key], dict) and self.get_value_type(properties[key]) != \
                        data_type_prototype[key]:
                    raise TypeError(
                        f"the field '{key}' is declared as {data_type_prototype[key]}, but the given value is {self.get_value_type(properties[key])}")

            print("properties: ", properties)
            print("\n\n")

        # 自定义类类型
        if isinstance(node.value, NewObjectNode):
            # node.value是NewObjectNode类型，说明是自定义类
            if node.data_type != node.value.class_name:
                raise TypeError(f"the given value of variable '{node.name}' is not '{node.data_type}' ")

        # 进行赋值类型和声明类型的判断（是否匹配）
        if isinstance(node.value, StructAssignNode):
            # 对赋的值进行类型检查
            prototype = self.environment["types"][node.value.struct_name]
            struct = self.evaluate(node.value)

            if "value" in struct:
                struct = struct["value"]
            # for field in struct:
            #     if self.get_value_type(struct[field]) != prototype[field]:
            #         raise TypeError(
            #             f"the field is declared as {prototype[field]}, but the given value is {self.get_value_type(struct[field])}")

        # let x = def(){}; 这种
        if isinstance(node.value, FunctionDeclarationNode):
            # 将函数的参数和体存入环境  node.value是FunctionDeclarationNode类型， 需要里面的参数和body_statements
            if node.name in self.environment:
                raise NameError(f"Function '{node.name}' already defined")
            # 保存函数到环境中
            self.environment[node.name] = {

                # =========== 类型系统====================
                "return_type": node.value.return_type,  # 假设在 AST 中传递返回值类型
                "params_types": node.value.params_types,  # 假设在 AST 中传递参数类型
                # =========== 类型系统====================

                "args": node.value.args,
                "body": node.value.body,
                # 对于let z = def(){}这种形式，需要将默认参数放到environment中, 否则在
                # 函数调用的时候找不到参数,而对let z = def(){}类和箭头函数的默认参数，需要在
                # evaluate_assignment中进行处理，对于 def main(){}这类函数，参数需要在
                # evaluate_function_declaration中处理,这就是差异！！！
                "defaults": node.value.default_values,  # 假设在 AST 中传递默认值
            }

            # 第2次赋值：
            # 类型检查
            if node.name in self.environment["types"]:  # 已经赋过值，需要检查最新的赋值的值的类型是否一致
                # 已有的类型  !=  新的类型
                if self.environment["types"][node.name] != "any":
                    # 声明的类型 ！=  赋值的类型
                    if self.environment["types"][node.name] != self.get_value_type(node.value):
                        raise TypeError(
                            f"Cannot reassign variable '{node.name}' with a new type: {self.get_value_type(node.value, node.data_type)}")

            # 类型记录
            # 第一次赋值：
            #       判断声明的类型、赋值的类型是否一致
            got_type = self.get_value_type(node.value)
            # 变量如果声明的是any, 则不进行类型检查; 否则，需要进行类型检查
            if node.data_type != "any":
                if node.data_type != got_type:
                    raise TypeError(f"the given value of variable '{node.name}' is not '{node.data_type}' ")
            # node.data_type 是变量声明时候的类型   let x: int = 1;
            self.environment["types"][node.name] = node.data_type

        else:
            # =======================常量检查===============================
            if node.name in self.environment['constants']:
                raise ValueError(f"Constant '{node.name}' cannot be reassigned")
                # 如果当前节点是常量，加入到constants列表中, 用于检查是否重复赋值
            if node.is_constant:
                self.environment['constants'].append(node.name)
            # =======================常量检查===============================

            # 否则，直接求值
            value = self.evaluate(node.value)

            # ===================== 增加类型系统===========================
            # 第二次赋值：
            #           判断是否已经赋过值
            if node.name in self.environment["types"]:  # 已经赋过值，需要检查最新的赋值的值的类型是否一致
                # 已有的类型  !=  新的类型
                if self.environment["types"][node.name] != "any":
                    # 声明的类型 ！=  赋值的类型
                    if self.environment["types"][node.name] != self.get_value_type(value, node.data_type):
                        raise TypeError(
                            f"Cannot reassign variable '{node.name}' with a different type: {self.get_value_type(value, node.data_type)}")

            # 第一次赋值：

            # 对象单独判断
            if isinstance(value, dict):
                # 说明是实例
                if "parent_name" in value:
                    if node.data_type != value["parent_name"]:
                        raise TypeError(f"the given value of variable '{node.name}' is not '{node.data_type}' ")
            #  判断声明的类型、赋值的类型是否一致
            elif isinstance(node, AssignmentNode):
                # print("value: ",value)
                # print("value之parent_name: ",value["parent_name"])

                got_type = self.get_value_type(value, node.data_type)
                # print("got type: ", type(got_type))

                # 函数没有返回任何东西，返回类型是void
                if got_type == "NoneType":
                    raise TypeError(f"the function expected to return a value of type '{node.data_type}',got 'void' ")

                if node.data_type != got_type:
                    raise TypeError(f"the given value of variable '{node.name}' is not '{node.data_type}' ")

            # 记录变量的类型
            self.environment["types"][node.name] = self.get_value_type(value, node.data_type)
            # ===================== 增加类型系统============================

            # 赋值
            self.environment[node.name] = value
            return value

    def get_value_type(self, val, data_type=None):

        """
        :param val:
        :param data_type:
            node里面记录的类型
        :return:
        :node: 节点
        """
        if isinstance(val, FunctionDeclarationNode):
            return "function"

        # 枚举值传进来的是字符串
        if isinstance(val, str):
            for enum_name in self.environment["enums"]:
                if val in self.environment["enums"][enum_name]:
                    return enum_name
        # 结构体类型
        if isinstance(val, dict) and "type" in val:
            return val["name"]

        if data_type == "any":
            return "any"

        # 其他普通类型
        type_name = type(val).__name__

        if type_name == "dict":
            return "object"
        elif type_name == "str":
            return "string"
        # return type_name
        else:
            return type_name

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
                # print("statement: ",statement)

                if isinstance(statement, BreakNode):
                    break_flag = True
                # if break_flag == False:
                try:
                    # 有可能遇到return 语句, 直接返回值
                    val = self.evaluate(statement)
                    # 遇到return语句的返回值，形式是：{'fight_tag': True, 'value': val}
                    if isinstance(val, dict) and "fight_tag" in val:
                        return val["value"]  # 直接返回值，结束循环

                    # 2，重新计算条件表达式
                    condition_value = self.evaluate(node.condition)
                except BreakException:
                    break_flag = True
                    break
            if break_flag:
                break

    def evaluate_do_while(self, node: DoWhileNode):
        """
            实现 do while 循环
        """
        #
        # for statement in node.body:
        #     self.evaluate(statement)
        # cond = self.evaluate(node.condition)
        # while cond:
        #     try:
        #         for statement in node.body:
        #             self.evaluate(statement)
        #         cond = self.evaluate(node.condition)
        #     except BreakException:
        #         break

        # ==================new version======================

        for statement in node.body:
            self.evaluate(statement)
        cond = self.evaluate(node.condition)
        while cond:
            # 处理break 语句
            try:
                for statement in node.body:
                    # 获取每个语句的返回值，如果是return语句，会得到一个dict，里面有"fight_tag"和"value"
                    val = self.evaluate(statement)
                    print("val(do_while) = ", val)
                    # 处理返回值问题
                    if isinstance(val, dict) and "fight_tag" in val:
                        return val["value"]  # 直接返回值，结束循环

                # 重新计算条件表达式
                cond = self.evaluate(node.condition)

            except BreakException:
                break


# 测试Evaluator
if __name__ == '__main__':
    # ================================================================
    #  3，多态的支持??!!

    code = """
       class A{
            fields{
                X:int = 10;
            }
            methods{
                    def Inc(incNum:float = 1.1) void{
                            X  += incNum;
                    }
                    def MyPrintln() void{
                            printlnCyan(X);
                    }
            }
            init(){}
       }
       let a: A = new A();
       a->Inc(incNum=10.534123)->MyPrintln();
       
       
    """
    code = """
        enum Color{
            RED, GREEN
        }
        
        let color: Color = enum::Color::RED;
        printlnCyan(color); 
    
    """
    # StructAccessNode
    code = """
        struct Info{
            id: int,
            age: int
        } 
         struct Person{
            name: string,
            id: Info
         }
        
         let info: Info = Info{
                id: 100,
                age: 20
        };
        
         let p: Person = Person{
            name: "Tom",
            id:  Info{
                id: 100,
                age: 20
            }
        };
        
        let v: any = p::id::age; 
        printlnCyan(v); 
    """

    # ==================================================================
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
        print("node:  ", node)
        r = evaluator.evaluate(node)
        # print(r)

    print("environment（最终版）: \n\t", evaluator.environment)
    print("environment（instances）: \n\t", evaluator.environment["instances"])
    # print("module_env: \n\t", evaluator.modules)
