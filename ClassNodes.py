from interpreter.Node import Node


# 接口定义
class InterfaceNode(Node):
    def __init__(self, interface_name, methods: list = []):
        self.interface_name = interface_name
        self.methods = methods

    def __repr__(self):
        return f"Interfacenode(interface_name = {self.interface_name},methods = {self.methods})"


# return this; 这样的语句  this的使用需要记录当前的类名
class ThisNode(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return "ThisNode()"


# this->xx(); 这样的语句  this的使用需要记录当前的类名
class CallClassInnerMethod(Node):
    def __init__(self, method_name, arguments):
        # self.current_class_name = current_class_name
        self.method_name = method_name
        self.arguments = arguments

    def __repr__(self):
        return f"CallClassInnerMethod(method_name = {self.method_name},arguments = {self.arguments})"


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
    def __init__(self, instance_name, method_name, arguments,extra = None):
        self.instance_name = instance_name
        self.method_name = method_name
        self.arguments = arguments
        self.extra = extra

    def __repr__(self):
        return f"MethodCallNode(instance_name = {self.instance_name},method_name = {self.method_name},arguments = {self.arguments},extra = {self.extra})"


# let z = new 类名(参数); 这样的表达式
class NewObjectNode(Node):
    def __init__(self, object_name, class_name, arguments: list = []):
        self.object_name = object_name
        self.class_name = class_name
        self.arguments = arguments  # 只能是位置参数

    def __repr__(self):
        return f"NewObjectNode(object_name = {self.object_name},class_name = {self.class_name},arguments = {self.arguments})"


class ClassDeclarationNode(Node):
    def __init__(self, classname, methods=None, fields=None, init=None, static_methods=None, static_fields=None,
                 parent_name = "",interfaces: list = [],fields_annotations:dict = {}):
        self.fields_annotations = fields_annotations
        self.classname = classname
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

    def __repr__(self):
        return f"ClassDeclarationNode(fields_annotations = {self.fields_annotations},interfaces = {self.interfaces},parent_name = {self.parent_name},classname = {self.classname},methods = {self.methods},fields = {self.fields},init = {self.init},static_methods = {self.static_methods},static_fields = {self.static_fields})"


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