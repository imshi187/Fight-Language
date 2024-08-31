from typing import List, Dict

from interpreter.Node import Node


# 函数组合表达式
# let z = f & g & inc;
class CombineNode(Node):
    def __init__(self, combined_name, funcs):
        self.combined_name = combined_name
        self.funcs = funcs

    def __repr__(self):
        return f"CombineNode(combined_name={self.combined_name},funcs={self.funcs})"


# set<1,2,3>
class SetNode(Node):
    def __init__(self, set_values):
        self.set_values = set_values

    def __repr__(self):
        return f"SetNode(set_values={self.set_values})"


# id--;
class DecrementNode(Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def __repr__(self):
        return f"DecrementNode(var_name={self.var_name})"


# id++;
class IncrementNode(Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def __repr__(self):
        return f"IncrementNode(var_name={self.var_name})"


# try 代码块
class TryCatchFinallyNode(Node):
    def __init__(self, try_block, catch_block, finally_block):
        self.try_block = try_block
        # [{ ERR_TYPE: [代码列表]  }, {}, {}]
        self.catch_block = catch_block
        self.finally_block = finally_block

    def __repr__(self):
        return f"TryCatchFinallyNode(try_block={self.try_block}, catch_block={self.catch_block}, finally_block={self.finally_block})"


# for(idx: 1..10){}
class ForRangeNumberNode(Node):
    def __init__(self, var_name, start_num, end_num, body):
        self.var_name = var_name  # 变量名
        self.start_num = start_num  # 开始数字
        self.end_num = end_num  # 结束数字
        self.body = body  # 循环体

    def __repr__(self):
        return f"ForRangeNumberNode(var_name={self.var_name}, start_num={self.start_num}, end_num={self.end_num}, body={self.body})"


# switch语句
class SwitchNode(Node):
    def __init__(self, expr, cases: dict = {}):
        self.expr = expr  # 表达式
        self.cases = cases  # 字典，key是case的表达式，value是case对应的语句

    def __repr__(self):
        return f"SwitchNode(expr={self.expr}, cases={self.cases})"


# match表达式
class MatchExprNode(Node):
    def __init__(self, expr, case_value_dict: dict = {}, else_expr=None):
        # match(x) {1 => "value"}
        self.expr = expr  # 比如x
        #  1 => "value",  这样的表达式
        self.case_value_dict = case_value_dict
        # 其他情况的表达式
        self.else_expr = else_expr

    def __repr__(self):
        return f"MatchExprNode(expr={self.expr}, cases={self.case_value_dict}), else_expr={self.else_expr})"


# 处理 if(true) 10: 200 这样的表达式
class IfExprNode(Node):
    def __init__(self, condition, expr_if_true, expr_if_false):
        self.condition = condition
        self.expr_if_true = expr_if_true
        self.expr_if_false = expr_if_false

    def __repr__(self):
        return f"IfExprNode(condition={self.condition}, expr_if_true={self.expr_if_true}, expr_if_false={self.expr_if_false})"


# 引入模块  import Math
class CommentNode(Node):
    def __init__(self, comments):
        self.comments = comments

    def __repr__(self):
        return f"CommentNode(comments={self.comments})"


# 支持导入真个模块或者模块里面的单个元素
class ImportModuleNode(Node):
    def __init__(self, module_name, import_elements: list = [], import_whole_module=True, alias=None):
        self.module_name = module_name
        self.alias = alias
        # 引入的元素，比如 import {a,b} from "module"  这里的a,b就是import_elements
        self.import_elements = import_elements
        # 是否引入整个模块，比如 import "module"  这里的module就是import_whole_module
        self.import_whole_module = import_whole_module

    def __repr__(self):
        return f"ImportModuleNode(module_name={self.module_name}, import_elements={self.import_elements}, import_whole_module={self.import_whole_module}, alias={self.alias})"


# 声明模块  比如 package module{ let x = 10;  }
class PackageDeclarationNode(Node):
    def __init__(self, package_name, package_body):
        self.package_name = package_name
        self.package_body = package_body

    def __repr__(self):
        return f"PackageDeclarationNode(package_name={self.package_name}, package_body={self.package_body})"


# for in语法节点
class ForInNode(Node):
    def __init__(self, variable, iteration_obj, body):
        self.variable = variable
        self.iteration_obj = iteration_obj
        self.body = body

    def __repr__(self):
        return f"ForInNode(variable={self.variable}, iteration_obj={self.iteration_obj}, body={self.body})"


class UnaryOpNode(Node):
    def __init__(self, operator, operand):
        self.operator = operator  # 操作符，例如 'not'
        self.operand = operand  # 操作数，通常是一个节点（如逻辑表达式）

    def __repr__(self):
        return f"UnaryOpNode(operator={self.operator}, operand={self.operand})"


class NumberNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode(value={self.value})"


class ListNode(Node):
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"ListNode(elements={self.elements})"


# 列表索引节点, 如 a[1]
class ListIndexNode(Node):
    def __init__(self, name, start_index, end_index=None):
        self.list_name = name
        self.start_index = start_index
        self.end_index = end_index

    def __repr__(self):
        return f"ListIndexNode(list_name={self.list_name}, start_index={self.start_index}, end_index={self.end_index})"


# dual list index  双列表索引，如 a[1][2]
# 多维列表索引，如 a[1][2][3]
class MultiListIndexNode(Node):
    def __init__(self, name, index_list):
        self.list_name = name
        self.index_list = index_list

    def __repr__(self):
        return f"MultiListIndexNode(list_name={self.list_name}, index_list={self.index_list})"


class VariableNode(Node):
    def __init__(self, value):
        # self.name = name
        self.value = value

    def __repr__(self):
        return f"VariableNode(value={self.value})"


class BinaryOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOpNode(left={self.left}, op={self.op}, right={self.right})"


class LoopNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"LoopNode(condition={self.condition}, body={self.body})"


class ReturnNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"ReturnNode(value={self.value})"


# 列表解构赋值
class ListDeconstructAssignNode(Node):
    def __init__(self, vars_list, list_obj):
        # 使用列表存放变量名  【"a","b"】
        self.vars_list = vars_list
        self.list_obj = list_obj

    def __repr__(self):
        return f"ListDeconstructAssignNode(vars={self.vars_list}, list_obj={self.list_obj})"


# 解构赋值 let {a,b} = {a:1,b:2}
class DecontructAssignNode(Node):
    def __init__(self, vars_list, dict_obj):
        # 使用列表存放变量名  【"a","b"】
        self.vars_list = vars_list
        self.dict_obj = dict_obj

    def __repr__(self):
        return f"DecontructAssignNode(vars={self.vars_list}, dict_obj={self.dict_obj})"


class AssignmentNode(Node):
    # name = value
    def __init__(self, name, value, is_constant=False):
        self.name = name
        self.value = value
        self.is_constant = is_constant

    def __repr__(self):
        return f"AssignmentNode(name={self.name}, value={self.value}, is_constant={self.is_constant})"


class ArrayNode(Node):
    def __init__(self, elements):
        self.elements: List[any] = elements

    def __repr__(self):
        return f"ArrayNode(elements={self.elements})"


class ObjectNode(Node):
    def __init__(self, properties):
        self.k_v: Dict[any, any] = properties

    def __repr__(self):
        return f"ObjectNode(properties={self.k_v})"


# 对象属性索引
class ObjectIndexNode(Node):
    # 比如 name{"id"}
    def __init__(self, object_name, key_expr):
        self.object_name = object_name
        self.key_expr = key_expr

    def __repr__(self):
        return f"ObjectIndexNode(object_name={self.object_name}, key_expr={self.key_expr})"


class IfStatementNode(Node):
    def __init__(self, condition, if_body, elif_, else_):
        self.condition = condition
        self.if_body = if_body
        self.elif_ = elif_
        self.else_ = else_

    def __repr__(self):
        return f"IfStatementNode(condition={self.condition}, if_body={self.if_body}, elif_={self.elif_}, else_={self.else_})"


class FunctionCallNode(Node):
    def __init__(self, name, args, named_arg_values: dict = {}, is_combined=False):
        # 函数名
        self.name = name
        self.args = args
        # 命名参数的值
        self.named_arg_values = named_arg_values
        self.is_combined = is_combined

    def __repr__(self):
        # return f"FunctionCallNode(name={self.name}, args={self.args}, named_arg_values={self.named_arg_values})"
        return f"FunctionCallNode(name={self.name}, args={self.args}, named_arg_values={self.named_arg_values}, is_combined={self.is_combined})"


class FunctionDeclarationNode:
    def __init__(self, name, args, body, default_values: dict = {}, is_static=False, func_type=None, tag=None,
                 annotations: dict = {}):
        # 函数注解
        self.annotations = annotations
        self.name = name
        self.args = args
        self.body: List = body
        self.default_values = default_values
        self.return_type = None,
        # 用于判断类的方法是否是静态方法
        self.is_static = is_static
        # 指的是匿名函数、箭头函数、普通函数(def定义的)
        self.func_type = func_type
        self.tag = tag

    def __repr__(self):
        return f"FunctionDeclarationNode(annotations = {self.annotations},tag = {self.tag},func_type={self.func_type},name={self.name}, args={self.args}, body={self.body}, default_values={self.default_values}, is_static={self.is_static},)"


class BooleanNode:
    def __init__(self, value):
        self.value: bool = value

    def __repr__(self):
        return f"BooleanNode(value={self.value})"


class StringNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"StringNode(value={self.value})"


class BreakNode:
    def __init__(self):
        self.value = "break"

    def __repr__(self):
        return f"BreakNode(value={self.value})"


# struct 名称 {x,y,z}
# 考虑给每个属性一个初始值,-1
class StructDeclarationNode(Node):
    def __init__(self, struct_name, fields: dict = {}):
        self.struct_name = struct_name
        self.fields = fields  # 表示字段的值

    def __repr__(self):
        return f"StructDeclarationNode(name={self.struct_name}, fields={self.fields})"


# Point{x:1,y:2}
class StructAssignNode(Node):
    def __init__(self, struct_name, struct_fields_values):
        # id 比如 Point
        self.struct_name = struct_name
        # 一个dict 比如{x:1,y:2}
        self.struct_fields_values = struct_fields_values

    def __repr__(self):
        return f"StructAssignNode(name={self.struct_name}, fields={self.struct_fields_values})"


# p::x 这样访问结构体实例的属性
class StructAccessNode(Node):
    def __init__(self, struct_instance_name, field_name):
        self.struct_instance_name = struct_instance_name
        self.field_name = field_name

    def __repr__(self):
        return f"StructAccessNode(name={self.struct_instance_name}, field_name={self.field_name})"


class EnumDeclarationNode(Node):
    def __init__(self, enum_name, enum_values: list = []):
        self.enum_name = enum_name
        self.enum_values = enum_values

    def __repr__(self):
        return f"EnumDeclarationNode(name={self.enum_name}, fields={self.enum_values})"


# let x= enum::Color::Red;
class EnumAccessNode(Node):
    def __init__(self, enum_name, enum_property):
        self.enum_name = enum_name
        self.enum_property = enum_property

    def __repr__(self):
        return f"EnumAccessNode(enum_name={self.enum_name}, enum_property={self.enum_property})"


class ChainNode(Node):
    def __init__(self, expr, handler_list):
        # 要处理的遍历
        self.expr = expr
        # 处理器列表, 就是一些方法罢了
        self.handler_list = handler_list

    def __repr__(self):
        return f"ChainNode(expr={self.expr}, handler_list={self.handler_list})"


# do { } while(true)
class DoWhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"DoWhileNode(condition={self.condition}, body={self.body})"


# 列表生成器  generator[idx+1; idx = 1 to 10];
class ListGeneratorNode(Node):
    def __init__(self, gen_expr, iter_name, start, end, step):
        self.gen_expr = gen_expr
        self.iter_name = iter_name
        self.start = start
        self.end = end
        self.step = step

    def __repr__(self):
        return f"ListGeneratorNode(gen_expr={self.gen_expr},iter_name={self.iter_name},start={self.start},end={self.end},step={self.step})"


# 求绝对值
class AbsNode(Node):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AbsNode(expr={self.expr})"


# 连续调用
class SerialCall(Node):
    def __init__(self, caller, methods_list: list = [], extra=None):
        self.caller = caller
        self.methods_list = methods_list
        self.extra = extra

    def __repr__(self):
        return f"SerialCall(caller={self.caller},methods_list={self.methods_list},extra={self.extra})"


# id+=expr;
class PlusAssignNode(Node):
    def __init__(self, var_name, inc_val):
        self.var_name = var_name
        self.inc_val = inc_val

    def __repr__(self):
        return f"PlusAssignNode(var_name={self.var_name},inc_val={self.inc_val})"


# id-=expr;
class MinusAssignNode:
    def __init__(self, var_name, dec_val):
        self.var_name = var_name
        self.dec_val = dec_val

    def __repr__(self):
        return f"MinusAssignNode(var_name={self.var_name},dec_val={self.dec_val})"

class MultiplyAssignNode(Node):
    def __init__(self, var_name, mul_val):
        self.var_name = var_name
        self.mul_val = mul_val
    def __repr__(self):
        return f"MultiplyAssignNode(var_name={self.var_name},mul_val={self.mul_val})"


# id/=expr;
class DivideAssignNode(Node):
    def __init__(self, var_name, div_val):
        self.var_name = var_name
        self.div_val = div_val

    def __repr__(self):
        return f"DivideAssignNode(var_name={self.var_name},div_val={self.div_val})"


# d{key} = val
class ObjectAssignNode(Node):
    def __init__(self, object_name, key_expr, value_expr):
        self.object_name = object_name
        self.key_expr = key_expr
        self.value_expr = value_expr

    def __repr__(self):

        return f"ObjectAssignNode(object_name={self.object_name},key_expr={self.key_expr},value_expr={self.value_expr})"


# lst[index] = val;
class ListAssignNode(Node):
    def __init__(self, list_name, index_expr, value_expr):
        self.list_name = list_name
        self.index_expr = index_expr
        self.value_expr = value_expr

    def __repr__(self):
        return f"ListAssignNode(list_name={self.list_name},index_expr={self.index_expr},value_expr={self.value_expr})"

