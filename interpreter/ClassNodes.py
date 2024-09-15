from interpreter.Node import Node


# 接口定义
class InterfaceNode(Node):
    def __init__(self, interface_name, methods: list = [],params_types: list = [],return_type = None):
        self.interface_name = interface_name
        self.methods = methods
        self.name = interface_name
        self.params_types = params_types
        self.return_type  = return_type

    def __repr__(self):
        return f"InterfaceNode(interface_name = {self.interface_name},methods = {self.methods},params_types = {self.params_types},return_type = {self.return_type})"


# return this; 这样的语句  this的使用需要记录当前的类名
class ThisNode(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return "ThisNode()"


# this->xx(); 这样的语句  this的使用需要记录当前的类名
class CallClassInnerMethod(Node):
    def __init__(self, method_name, arguments,named_args: dict = {}):
        # self.current_class_name = current_class_name
        self.method_name = method_name
        self.arguments = arguments
        self.named_args = named_args

    def __repr__(self):
        return f"CallClassInnerMethod(method_name = {self.method_name},arguments = {self.arguments},named_args = {self.named_args})"


# 获取成员的属性
# class GetMemberNode(Node):
#     def __init__(self, instance_name, member_name):
#         self.instance_name = instance_name
#         self.member_name = member_name
#
#     def __repr__(self):
#         return f"GetMemberNode(instance_name = {self.instance_name},member_name = {self.member_name})"
class GetMemberNode(Node):
    def __init__(self, instance_or_class_name, member_name):
        self.instance_or_class_name = instance_or_class_name
        # member_name 可能是属性名，也可能是方法名
        self.member_name = member_name

    def __repr__(self):
        return f"GetMemberNode(class_or_instance_name = {self.instance_or_class_name}, field ={self.member_name})"


# 比如  let p = new Person("Tom", 20);
# p->sayHello(); 这样的表达式
class MethodCallNode(Node):
    def __init__(self, instance_name, method_name, arguments, extra=None,named_args: dict = {}):
        self.instance_name = instance_name
        self.method_name = method_name
        self.arguments = arguments
        # 命名参数
        self.named_args = named_args
        self.extra = extra

    def __repr__(self):
        return f"MethodCallNode(instance_name = {self.instance_name},method_name = {self.method_name},arguments = {self.arguments},named_args = {self.named_args},extra = {self.extra})"


# let z = new 类名(参数); 这样的表达式
class NewObjectNode(Node):
    def __init__(self, object_name, class_name, arguments: list = []):
        # 实例对象的名称
        self.object_name = object_name
        # 类名
        self.class_name = class_name
        self.arguments = arguments  # 只能是位置参数
        self.name = class_name

    def __repr__(self):
        return f"NewObjectNode(object_name = {self.object_name},class_name = {self.class_name},arguments = {self.arguments})"


class ClassDeclarationNode(Node):
    def __init__(self, classname, methods=None, fields=None, init=None, static_methods=None, static_fields=None,
                 parent_name="", interfaces: list = [], fields_annotations: dict = {},fields_types: dict = {}):
        self.fields_annotations = fields_annotations
        self.classname = classname
        self.name = classname  # 为了导包
        self.methods = methods
        self.fields = fields
        self.init = init
        # 静态的属性和方法
        self.static_methods = static_methods
        self.static_fields = static_fields
        # 继承的父类
        self.parent_name = parent_name
        # 实现的接口
        self.interfaces = interfaces
        # 格式: annotations: {方法名称:{key:value}}

        # 字段的类型
        self.fields_types = fields_types

    def __repr__(self):
        return f"ClassDeclarationNode(fields_types = {self.fields_types},init = {self.init},fields_annotations = {self.fields_annotations},interfaces = {self.interfaces},parent_name = {self.parent_name},classname = {self.classname},methods = {self.methods},fields = {self.fields},static_methods = {self.static_methods},static_fields = {self.static_fields})"


class MethodDeclarationNode(Node):
    def __init__(self, class_name, params, body, is_public=True):
        self.class_name = class_name
        self.is_public = is_public
        self.params = params
        self.body = body

    def __repr__(self):
        return f"MethodDeclarationNode(class_name = {self.class_name},params = {self.params},body = {self.body},is_public = {self.is_public})"


class AttributeDeclarationNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"AttributeDeclarationNode(name = {self.name},value = {self.value})"


class NewInstanceNode(Node):
    def __init__(self, class_name, arguments):
        self.class_name = class_name
        self.arguments = arguments

    def __repr__(self):
        return f"NewInstanceNode(class_name = {self.class_name},arguments = {self.arguments})"


# this->属性名称; 这样的表达式  this的使用需要记录当前的类名
class GetMemberNodeByThis(Node):
    def __init__(self, member_name):
        self.member_name = member_name

    def __repr__(self):
        return f"GetMemberNodeByThis(member_name = {self.member_name})"


# 连续调用方法
# p->sayHello()->sayWorld()
class SerialMethodCallNode(Node):
    def __init__(self, instance_name, methods_list: list = []):
        self.instance_name = instance_name
        self.methods_list = methods_list

    def __repr__(self):
        return f"SerialMethodCallNode(instance_name = {self.instance_name},methods_list = {self.methods_list})"


class SuperNode(Node):
    def __init__(self, key_value_pairs: dict = {}, instance_name=None):
        self.key_value_pairs = key_value_pairs
        self.cur_instance_name = instance_name

    def __repr__(self):
        return f"SuperNode(key_value_pairs = {self.key_value_pairs},cur_instance_name = {self.cur_instance_name})"


# 导入第三方类
class ImportThirdPartyClassNode(Node):
    def __init__(self, class_name, file_path):
        self.class_name = class_name
        self.file_path = file_path

    def __repr__(self):
        return f"ImportThirdPartyClassNode(class_name = {self.class_name},file_path = {self.file_path})"


# import <类名>
class ImportBuiltinClassNode(Node):
    def __init__(self, class_name):
        self.class_name = class_name

    def __repr__(self):
        return f"ImportBuiltinClassNode(class_name = {self.class_name})"


# use (x,y) from "module_path"
class UseModuleNode(Node):
    def __init__(self, use_elements, module_path,is_builtin=False):
        self.use_elements = use_elements
        self.module_path = module_path
        self.is_builtin = is_builtin

    def __repr__(self):
        return f"UseModuleNode(import_elements = {self.use_elements},module_path = {self.module_path},is_builtin = {self.is_builtin})"


# exports = ["x","y"]
class ExportsNode(Node):
    def __init__(self, exports_list: list):
        self.exports_list = exports_list

    def __repr__(self):
        return f"ExportsNode(exports_list = {self.exports_list})"

# 类属性赋值 A->x = 10;
class ClassPropertyAssignNode(Node):
    def __init__(self, class_name, property_name, value):
        self.class_name = class_name
        self.property_name = property_name
        self.value = value

    def __repr__(self):
        return f"ClassPropertyAssignNode(class_name = {self.class_name},property_name = {self.property_name},value = {self.value})"