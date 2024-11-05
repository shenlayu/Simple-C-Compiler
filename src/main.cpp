#include <iostream>
#include <fstream>
#include "antlr4-runtime.h"
#include "CLexer.h"
#include "CParser.h"
#include "XMLGeneratorListener.h"  // 引入XML生成器

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
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input-file>" << std::endl;
        return 1;
    }

    std::ifstream stream(argv[1]);
    if (!stream.is_open()) {
        std::cerr << "Failed to open input file: " << argv[1] << std::endl;
        return 1;
    }

    // 打开输出XML文件
    std::ofstream outputFile("output.xml");
    if (!outputFile.is_open()) {
        std::cerr << "Failed to create output file: output.xml" << std::endl;
        return 1;
    }

    antlr4::ANTLRInputStream input(stream);
    CLexer lexer(&input);
    CommonTokenStream tokens(&lexer);
    CParser parser(&tokens);

    parser.removeErrorListeners();
    parser.addErrorListener(&MyErrorListener::INSTANCE);

    antlr4::tree::ParseTree *tree = parser.compilationUnit();

    // 使用XMLGeneratorListener生成XML，并将其输出到文件
    XMLGeneratorListener xmlListener(outputFile, parser.getVocabulary());
    antlr4::tree::ParseTreeWalker::DEFAULT.walk(&xmlListener, tree);

    // 关闭输出文件
    outputFile.close();

    return 0;
}
