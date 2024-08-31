import math


class MathUtils:
    @staticmethod
    def Sqrt(x: float) -> float:
        """计算平方根"""
        return math.sqrt(x)

    @staticmethod
    def Factorial(n: int) -> int:
        """计算阶乘"""
        return math.factorial(n)

    @staticmethod
    def Pow(base: float, exp: float) -> float:
        """计算幂"""
        return math.pow(base, exp)

    @staticmethod
    def Sin(x: float) -> float:
        """计算正弦值"""
        return math.sin(x)

    @staticmethod
    def Cos(x: float) -> float:
        """计算余弦值"""
        return math.cos(x)

    @staticmethod
    def Tan(x: float) -> float:
        """计算正切值"""
        return math.tan(x)

    @staticmethod
    def Asin(x: float) -> float:
        """计算反正弦值"""
        return math.asin(x)

    @staticmethod
    def Acos(x: float) -> float:
        """计算反余弦值"""
        return math.acos(x)

    @staticmethod
    def Atan(x: float) -> float:
        """计算反正切值"""
        return math.atan(x)

    @staticmethod
    def Atan2(y: float, x: float) -> float:
        """计算反正切值，返回弧度"""
        return math.atan2(y, x)

    @staticmethod
    def Exp(x: float) -> float:
        """计算e的x次方"""
        return math.exp(x)

    @staticmethod
    def Log(x: float, base: float = math.e) -> float:
        """计算以base为底x的对数"""
        return math.log(x, base)

    @staticmethod
    def Log10(x: float) -> float:
        """计算以10为底x的对数"""
        return math.log10(x)

    @staticmethod
    def Ceil(x: float) -> int:
        """向上取整"""
        return math.ceil(x)

    @staticmethod
    def Floor(x: float) -> int:
        """向下取整"""
        return math.floor(x)

    @staticmethod
    def Round(x: float, n: int = 0) -> float:
        """四舍五入"""
        return round(x, n)

    @staticmethod
    def Pi() -> float:
        """返回圆周率"""
        return math.pi

    @staticmethod
    def Degrees(radians: float) -> float:
        """将弧度转换为角度"""
        return math.degrees(radians)

    @staticmethod
    def Radians(degrees: float) -> float:
        """将角度转换为弧度"""
        return math.radians(degrees)

    @staticmethod
    def Hypot(x: float, y: float) -> float:
        """计算欧几里得范数，即 sqrt(x*x + y*y)"""
        return math.hypot(x, y)

    @staticmethod
    def Comb(n: int, k: int) -> int:
        """计算组合数 C(n, k)"""
        return math.comb(n, k)

    @staticmethod
    def Perm(n: int, k: int) -> int:
        """计算排列数 P(n, k)"""
        return math.perm(n, k)

    @staticmethod
    def Gcd(a: int, b: int) -> int:
        """计算最大公约数"""
        return math.gcd(a, b)

    @staticmethod
    def Lcm(a: int, b: int) -> int:
        """计算最小公倍数"""
        return abs(a * b) // math.gcd(a, b) if a and b else 0
