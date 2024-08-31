"""
    有些方法是原地操作的，将操作后的结果返回就可以调用该方法
    包括：
        reverse、sort
"""


class ListUtils:
    @staticmethod
    def ListLength(lst: list) -> int:
        """返回列表的长度"""
        return len(lst)

    @staticmethod
    def ListAppend(lst: list, item) -> None:
        """向列表追加一个元素"""
        lst.append(item)

    @staticmethod
    def ListExtend(lst: list, items: list) -> None:
        """扩展列表，将另一个列表的元素添加到当前列表"""
        lst.extend(items)

    @staticmethod
    def ListInsert(lst: list, index: int, item) -> None:
        """在指定位置插入元素"""
        lst.insert(index, item)

    @staticmethod
    def ListRemove(lst: list, item) -> None:
        """从列表中移除指定元素"""
        lst.remove(item)

    @staticmethod
    def ListPop(lst: list, index: int = -1):
        """移除并返回指定位置的元素，默认移除最后一个元素"""
        return lst.pop(index)

    @staticmethod
    def ListIndex(lst: list, item) -> int:
        """查找元素的索引"""
        return lst.index(item)

    @staticmethod
    def ListCount(lst: list, item) -> int:
        """统计元素在列表中出现的次数"""
        return lst.count(item)


    @staticmethod
    def ListReverse(lst: list) -> list:
        """反转列表"""
        lst.reverse()
        return lst

    @staticmethod
    def ListSlice(lst: list, start: int, end: int) -> list:
        """返回列表的切片"""
        return lst[start:end]

    @staticmethod
    def ListShallowCopy(lst: list) -> list:
        """返回列表的浅拷贝"""
        return lst.copy()

    @staticmethod
    def ListClear(lst: list) -> None:
        """清空列表"""
        lst.clear()

    @staticmethod
    def ListJoin(separator: str, lst: list) -> str:
        """使用指定的分隔符连接列表元素"""
        return separator.join(map(str, lst))
