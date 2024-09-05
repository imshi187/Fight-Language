import os
import shutil

class FileSystemUtils:

    @staticmethod
    def GetCurrentDirectory() -> str:
        """获取当前工作目录"""
        return os.getcwd()

    @staticmethod
    def ChangeDirectory(path: str) -> None:
        """改变当前工作目录"""
        os.chdir(path)

    @staticmethod
    def ListDirectory(path: str = '.') -> list:
        """列出指定目录中的文件和子目录"""
        return os.listdir(path)

    @staticmethod
    def CreateDirectory(path: str) -> None:
        """创建新目录"""
        os.mkdir(path)

    @staticmethod
    def CreateDirectories(path: str) -> None:
        """递归创建目录"""
        os.makedirs(path)

    @staticmethod
    def RemoveFile(path: str) -> None:
        """删除文件"""
        os.remove(path)

    @staticmethod
    def RemoveDirectory(path: str) -> None:
        """删除空目录"""
        os.rmdir(path)

    @staticmethod
    def RemoveDirectoryTree(path: str) -> None:
        """递归删除目录及其内容"""
        shutil.rmtree(path)

    @staticmethod
    def RenameFile(src: str, new_name: str) -> None:
        """重命名文件或目录"""
        os.rename(src, new_name)

    @staticmethod
    def FileExists(path: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(path)

    @staticmethod
    def IsDirectory(path: str) -> bool:
        """检查路径是否为目录"""
        return os.path.isdir(path)

    @staticmethod
    def IsFile(path: str) -> bool:
        """检查路径是否为文件"""
        return os.path.isfile(path)

    @staticmethod
    def GetFileSize(path: str) -> int:
        """获取文件大小（字节）"""
        return os.path.getsize(path)

    @staticmethod
    def GetFileModificationTime(path: str) -> float:
        """获取文件的最后修改时间（时间戳）"""
        return os.path.getmtime(path)

    @staticmethod
    def JoinPath(*paths) -> str:
        """连接路径"""
        return os.path.join(*paths)

    @staticmethod
    def GetAbsolutePath(path: str) -> str:
        """获取绝对路径"""
        return os.path.abspath(path)

    @staticmethod
    def SplitPath(path: str) -> list:
        """分割路径为目录和文件名"""
        return list(os.path.split(path))

    @staticmethod
    def GetFileExtension(path: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(path)[1]

    @staticmethod
    def CopyFile(src: str, dst: str) -> None:
        """复制文件"""
        shutil.copy2(src, dst)

    @staticmethod
    def MoveFile(src: str, dst: str) -> None:
        """移动文件"""
        shutil.move(src, dst)

    @staticmethod
    def GetEnvironmentVariable(name: str) -> str:
        """获取环境变量"""
        return os.environ.get(name)

    @staticmethod
    def SetEnvironmentVariable(name: str, value: str) -> None:
        """设置环境变量"""
        os.environ[name] = value

    @staticmethod
    def GetSystemName() -> str:
        """获取操作系统名称"""
        return os.name

    @staticmethod
    def ExecuteCommand(command: str) -> int:
        """执行系统命令"""
        return os.system(command)
