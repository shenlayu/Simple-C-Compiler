#include <iostream>
#include <fstream>
#include "antlr4-runtime.h"
#include "CLexer.h"
#include "CParser.h"

using namespace antlr4;

// 自定义错误监听器
class MyErrorListener : public BaseErrorListener {
public:
    static MyErrorListener INSTANCE;

    void syntaxError(Recognizer *recognizer, Token *offendingSymbol, 
                    size_t line, size_t charPositionInLine, 
                    const std::string &msg, std::exception_ptr e) override {
        std::cerr << "Syntax error at line " << line << ":" 
                  << charPositionInLine << " - " << msg << std::endl;
    }
};

MyErrorListener MyErrorListener::INSTANCE;

int main(int argc, const char* argv[]) {
    // 检查输入参数
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input-file>" << std::endl;
        return 1;
    }

    // 读取输入文件
    std::ifstream stream(argv[1]);
    if (!stream.is_open()) {
        std::cerr << "Failed to open input file: " << argv[1] << std::endl;
        return 1;
    }

    // 创建输入流
    antlr4::ANTLRInputStream input(stream);

    // 创建词法分析器
    CLexer lexer(&input);
    antlr4::CommonTokenStream tokens(&lexer);
    tokens.fill(); // 确保所有令牌都被读取

    // 创建解析器
    CParser parser(&tokens);

    // 设置错误处理器
    parser.removeErrorListeners();
    parser.addErrorListener(&MyErrorListener::INSTANCE);

    // 使用入口规则进行解析
    antlr4::tree::ParseTree* tree = parser.compilationUnit();

    // 打印解析树
    std::cout << tree->toStringTree(&parser) << std::endl;

    return 0;
}
