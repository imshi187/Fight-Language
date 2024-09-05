"""
    下面几个方法可以判断对象和dict类型
"""
import numbers


class CommonUtils:
    @staticmethod
    def GetType(obj):
        returnType = type(obj).__name__
        if returnType == "str":
            return "string"
        elif returnType == "int":
            return "number"
        elif returnType == "float":
            return "number"
        elif returnType == "list":
            return "list"
        elif returnType == "dict":
            return "object"
        else:
            return returnType

    @staticmethod
    def ToInteger(content):
        try:
            return int(content)
        except ValueError:
            return False

    @staticmethod
    def ToFloat(content):
        try:
            return float(content)
        except ValueError:
            return False

    @staticmethod
    def ToNumber(content):
        if isinstance(content, numbers.Number):
            return content
        elif isinstance(content, str):
            try:
                return float(content)
            except ValueError:
                return int(content)
        else:
            return False

    # 字符串到布尔值转换
    @staticmethod
    def ToBoolean(content):
        if isinstance(content, bool):
            return content
        elif isinstance(content, str):
            if content == "True":
                return True
            elif content == "False":
                return False
            else:
                return False
        else:
            return False

    @staticmethod
    def ToString(content):
        if isinstance(content, str):
            return content
        elif isinstance(content, bool):
            return str(content)
        elif isinstance(content, numbers.Number):
            return str(content)
        else:
            return None


if __name__ == '__main__':

    obj = {"name": "John", "age": 30, "city": "New York"}
    if type(obj) == dict:
        print("not a dict")
