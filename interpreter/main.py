import os
import sys

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将父目录添加到 Python 路径
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from interpreter.Evaluator import Evaluator
from interpreter.Parser import Parser
from interpreter.Tokenizer import Tokenizer

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No file path provided. Usage: python main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r') as file:
            code = file.read()
        print("Code from file:", code)

        # 其余的代码处理逻辑...

    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print("=================tokenizer======================\n")
    # 词法分析
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    # for i in tokens:
    #     print(i)

    print("=================parser========================\n")
    # 语法分析
    parser = Parser(tokens)
    ast = parser.parse()  # 生成AST, 多个xxNode组成的列表
    # print("AST: ")
    # for node in ast:
        # print(node)

    # 求值器
    evaluator = Evaluator()
    print("=================evaluator=====================\n")
    for node in ast:
        r = evaluator.evaluate(node)
        # 如果有返回值，可以打印出来
        # if r is not None:
        #     print(f"Result: {r}")

    # print("environment: \n\t", evaluator.environment)
