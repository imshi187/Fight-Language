class DictUtils:
    @staticmethod
    def ObjectGet(d: dict, key, default=None):
        """获取指定键的值，如果键不存在则返回默认值"""
        return d.get(key, default)

    @staticmethod
    def ObjectSet(d: dict, key, value) -> None:
        """设置指定键的值"""
        d[key] = value

    @staticmethod
    def ObjectKeys(d: dict) -> list:
        """返回字典中所有键的列表"""
        return list(d.keys())

    @staticmethod
    def ObjectValues(d: dict) -> list:
        """返回字典中所有值的列表"""
        return list(d.values())

    @staticmethod
    def ObjectClear(d: dict) -> None:
        """清空字典"""
        d.clear()

    @staticmethod
    def ObjectCopy(d: dict) -> dict:
        """返回字典的浅拷贝"""
        return d.copy()

    @staticmethod
    def ObjectUpdate(d: dict, other: dict) -> None:
        """更新字典，将另一个字典的键值对添加到当前字典"""
        d.update(other)

    @staticmethod
    def ObjectPop(d: dict, key, default=None):
        """移除指定键并返回其值，如果键不存在则返回默认值"""
        return d.pop(key, default)

    @staticmethod
    def ObjectContains(d: dict, key) -> bool:
        """检查字典中是否包含指定键"""
        return key in d

    @staticmethod
    def ObjectMerge(dicts: list) -> dict:
        """合并多个字典"""
        result = {}
        for d in dicts:
            result.update(d)
        return result

    @staticmethod
    def ObjHasAttribute(obj, attr):
        if not isinstance(obj, dict):
           raise TypeError("object to be checked must be a dict object ! ")
        for key in obj:
            if key == attr:
                return True
        return False
