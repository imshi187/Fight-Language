import time


class TimeUtils:
    @staticmethod
    def GetCurrentTimestamp() -> float:
        """
        获取当前时间戳。

        Returns:
            float: 表示当前时间的浮点数时间戳，精确到秒。
        """
        return time.time()

    @staticmethod
    def Sleep(seconds: int) -> None:
        """
        暂停程序指定的秒数。
        Args:
            seconds (float): 要暂停的秒数。

        Returns:
            None
        """
        time.sleep(seconds)

    @staticmethod
    def GetCurrentTimeObj() -> dict:
        """
        获取当前时间的字典表示。

        Returns:
            dict: 包含当前时间信息的字典。
        """
        t = time.localtime()
        return {
            "year": t.tm_year,
            "month": t.tm_mon,
            "day": t.tm_mday,
            "hour": t.tm_hour,
            "minute": t.tm_min,
            "second": t.tm_sec,
            "weekday": t.tm_wday,
            "yearday": t.tm_yday
        }

    @staticmethod
    def FormatTime(format_string: str) -> str:
        """
        根据格式化字符串返回当前时间的格式化字符串。

        Args:
            format_string (str): 时间格式化字符串。

        Returns:
            str: 格式化后的时间字符串。
        """
        return time.strftime(format_string)

    @staticmethod
    def ParseTime(time_string: str, format_string: str) -> dict:
        """
        将时间字符串解析为时间字典。

        Args:
            time_string (str): 要解析的时间字符串。
            format_string (str): 与时间字符串匹配的格式化字符串。

        Returns:
            dict: 解析后的时间字典。

        Raises:
            ValueError: 如果字符串格式与给定的格式不匹配。
        """
        t = time.strptime(time_string, format_string)
        return {
            "year": t.tm_year,
            "month": t.tm_mon,
            "day": t.tm_mday,
            "hour": t.tm_hour,
            "minute": t.tm_min,
            "second": t.tm_sec,
            "weekday": t.tm_wday,
            "yearday": t.tm_yday
        }

    @staticmethod
    def TimeNs() -> int:
        """
        返回当前时间的纳秒时间戳。

        Returns:
            int: 表示当前时间的整数纳秒时间戳。
        """
        return time.time_ns()


# 使用示例
if __name__ == "__main__":
    print("Current Timestamp:", TimeUtils.GetCurrentTimestamp())

    print("Sleeping for 2 seconds...")
    TimeUtils.Sleep(2)
    print("Awoke after sleep.")

    current_time = TimeUtils.GetCurrentTimeObj()
    print("Current Time Dict:", current_time)

    formatted_time = TimeUtils.FormatTime("%Y-%m-%d %H:%M:%S")
    print("Formatted Time:", formatted_time)

    parsed_time = TimeUtils.ParseTime("2023-05-01 14:30:00", "%Y-%m-%d %H:%M:%S")
    print("Parsed Time Dict:", parsed_time)

    print("Current Time in Nanoseconds:", TimeUtils.TimeNs())
