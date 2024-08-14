from interpreter.Evaluator import Evaluator
from interpreter.Parser import Parser
from interpreter.Tokenizer import Tokenizer

if __name__ == '__main__':
    code = """
        let zero = 0;
        @printlnCyan(zero);
    
    """
    # ==================================================================
    print("=================tokenizer======================\n")
    # 词法分析
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    for i in tokens:
        print(i)

    print("=================parser========================\n")
    # 语法分析
    parser = Parser(tokens)
    ast = parser.parse()  # 生成AST, 多个xxNode组成的列表
    print("AST: ")
    for node in ast:
        print(node)

    # 求值器
    evaluator = Evaluator()
    print("=================evaluator=====================\n")
    for node in ast:
        r = evaluator.evaluate(node)
        # print(r)
    print("environment: \n\t", evaluator.environment)