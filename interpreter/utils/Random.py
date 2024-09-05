import random

class RandomUtils:
    @staticmethod
    def SetSeed(seed: int) -> None:
        """设置随机数种子"""
        random.seed(seed)

    @staticmethod
    def GetInt(a: int, b: int) -> int:
        """生成指定范围内的随机整数"""
        return random.randint(a, b)

    @staticmethod
    def GetFloat01() -> float:
        """生成0到1之间的随机浮点数"""
        return random.random()

    @staticmethod
    def GetFloatRange(a: float, b: float) -> float:
        """生成指定范围内的随机浮点数"""
        return random.uniform(a, b)

    @staticmethod
    def GetChoice(sequence):
        """从序列中随机选择一个元素"""
        return random.choice(sequence)

    @staticmethod
    def GetSample(sequence, k: int):
        """从序列中随机选择k个不重复的元素"""
        return random.sample(sequence, k)

    @staticmethod
    def Shuffle(lst: list) -> None:
        """随机打乱列表顺序"""
        random.shuffle(lst)

    @staticmethod
    def GetBool() -> bool:
        """生成随机布尔值"""
        return random.choice([True, False])

    @staticmethod
    def GetWeightedChoice(sequence, weights):
        """根据权重从序列中随机选择一个元素"""
        return random.choices(sequence, weights=weights, k=1)[0]

    @staticmethod
    def GetGaussian(mu: float = 0.0, sigma: float = 1.0) -> float:
        """生成符合高斯分布的随机数"""
        return random.gauss(mu, sigma)

    @staticmethod
    def GetByte() -> int:
        """生成一个随机字节（0-255之间的整数）"""
        return random.randint(0, 255)

    @staticmethod
    def GetBytes(n: int) -> bytes:
        """生成n个随机字节"""
        return random.randbytes(n)

    @staticmethod
    def GetBits(k: int) -> int:
        """生成一个具有k个随机比特位的整数"""
        return random.getrandbits(k)

    @staticmethod
    def GetChoices(sequence, k: int):
        """从序列中进行可重复的随机选择，选择k次"""
        return random.choices(sequence, k=k)

    @staticmethod
    def GetSystemFloat() -> float:
        """使用操作系统的随机源生成0到1之间的随机浮点数"""
        return random.SystemRandom().random()

    @staticmethod
    def ShuffleInPlace(lst: list) -> None:
        """就地随机打乱列表顺序"""
        random.shuffle(lst)

    @staticmethod
    def GetExponential(lambd: float = 1.0) -> float:
        """生成符合指数分布的随机数"""
        return random.expovariate(lambd)
