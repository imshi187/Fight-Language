class StringUtils:
    @staticmethod
    def StrLength(s: str) -> int:
        """返回字符串的长度"""
        return len(s)

    @staticmethod
    def StrUpper(s: str) -> str:
        """将字符串转换为大写"""
        return s.upper()

    @staticmethod
    def StrLower(s: str) -> str:
        """将字符串转换为小写"""
        return s.lower()

    @staticmethod
    def StrConcat(s1: str, s2: str) -> str:
        """连接两个字符串"""
        return s1 + s2

    @staticmethod
    def StrSplit(s: str, separator: str = ' ') -> list:
        """根据分隔符分割字符串"""
        return s.split(separator)

    @staticmethod
    def StrJoin(strings: list, separator: str) -> str:
        """使用指定的分隔符连接字符串列表"""
        return separator.join(strings)

    @staticmethod
    def StrStrip(s: str) -> str:
        """去除字符串两端的空白字符"""
        return s.strip()

    @staticmethod
    def StrReplace(s: str, old: str, new: str) -> str:
        """替换字符串中的子字符串"""
        return s.replace(old, new)

    @staticmethod
    def StrFind(s: str, substring: str) -> int:
        """查找子字符串的索引"""
        return s.find(substring)

    @staticmethod
    def StrStartsWith(s: str, prefix: str) -> bool:
        """检查字符串是否以指定的前缀开始"""
        return s.startswith(prefix)

    @staticmethod
    def StrEndsWith(s: str, suffix: str) -> bool:
        """检查字符串是否以指定的后缀结束"""
        return s.endswith(suffix)

    @staticmethod
    def StrContains(s: str, substring: str) -> bool:
        """检查字符串中是否包含子字符串"""
        return substring in s

    @staticmethod
    def StrCapitalize(s: str) -> str:
        """将字符串的首字母大写"""
        return s.capitalize()

    @staticmethod
    def StrTitle(s: str) -> str:
        """将字符串的每个单词首字母大写"""
        return s.title()

    @staticmethod
    def StrSwapcase(s: str) -> str:
        """将字符串中的大写字母转换为小写，小写字母转换为大写"""
        return s.swapcase()

    @staticmethod
    def StrIsNumeric(s: str) -> bool:
        """检查字符串是否为数字"""
        return s.isnumeric()

    @staticmethod
    def StrIsAlpha(s: str) -> bool:
        """检查字符串是否全部为字母"""
        return s.isalpha()

    @staticmethod
    def StrIsAlphanumeric(s: str) -> bool:
        """检查字符串是否包含字母和数字"""
        return s.isalnum()

    @staticmethod
    def StrCount(s: str, substring: str) -> int:
        """统计子字符串在字符串中出现的次数"""
        return s.count(substring)

    @staticmethod
    def StrIndex(s: str, substring: str) -> int:
        """查找子字符串的索引（找不到时会抛出异常）"""
        return s.index(substring)

    @staticmethod
    def StrFormatString(template: str, *args) -> str:
        """格式化字符串"""
        return template.format(*args)

    @staticmethod
    def StrReverse(s: str) -> str:
        """反转字符串"""
        return s[::-1]
