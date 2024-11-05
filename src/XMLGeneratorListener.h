#ifndef XMLGENERATORLISTENER_H
#define XMLGENERATORLISTENER_H

#include "CBaseListener.h"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include "antlr4-runtime.h"

class XMLGeneratorListener : public CBaseListener {
private:
    int indentLevel = 0;
    std::ofstream& outFile;
    antlr4::dfa::Vocabulary vocab;

    // 非终结符（解析器规则）名称列表
    const std::vector<std::string> ruleNames = {
        "compilationUnit",
        "primaryExpression",
        "genericSelection",
        "genericAssocList",
        "genericAssociation",
        "postfixExpression",
        "argumentExpressionList",
        "unaryExpression",
        "unaryOperator",
        "castExpression",
        "multiplicativeExpression",
        "additiveExpression",
        "shiftExpression",
        "relationalExpression",
        "equalityExpression",
        "andExpression",
        "exclusiveOrExpression",
        "inclusiveOrExpression",
        "logicalAndExpression",
        "logicalOrExpression",
        "conditionalExpression",
        "assignmentExpression",
        "assignmentOperator",
        "expression",
        "constantExpression",
        "declaration",
        "declarationSpecifiers",
        "initDeclaratorList",
        "initDeclarator",
        "storageClassSpecifier",
        "typeSpecifier",
        "structOrUnionSpecifier",
        "structOrUnion",
        "structDeclarationList",
        "structDeclaration",
        "specifierQualifierList",
        "structDeclaratorList",
        "structDeclarator",
        "enumSpecifier",
        "enumeratorList",
        "enumerator",
        "atomicTypeSpecifier",
        "typeQualifier",
        "functionSpecifier",
        "alignmentSpecifier",
        "declarator",
        "directDeclarator",
        "directDeclaratorBase",
        "directDeclaratorSuffix",
        "pointer",
        "typeQualifierList",
        "parameterTypeList",
        "parameterList",
        "parameterDeclaration",
        "identifierList",
        "typeName",
        "abstractDeclarator",
        "directAbstractDeclarator",
        "directAbstractDeclaratorBase",
        "directAbstractDeclaratorSuffix",
        "typedefName",
        "initializer",
        "initializerList",
        "designation",
        "designatorList",
        "designator",
        "staticAssertDeclaration",
        "statement",
        "labeledStatement",
        "compoundStatement",
        "blockItemList",
        "blockItem",
        "expressionStatement",
        "selectionStatement",
        "iterationStatement",
        "jumpStatement",
        "translationUnit",
        "externalDeclaration",
        "functionDefinition",
        "declarationList"
    };


    void printIndent() const {
        for (int i = 0; i < indentLevel; ++i) outFile << "  ";
    }

public:
    // 构造函数，接受一个文件流引用和词汇表
    XMLGeneratorListener(std::ofstream& output, antlr4::dfa::Vocabulary vocab)
        : outFile(output), vocab(vocab) {}

    // 处理非终结符的入口
    void enterEveryRule(antlr4::ParserRuleContext *ctx) override {
        printIndent();
        int ruleIndex = ctx->getRuleIndex();
        if (ruleIndex >= 0 && ruleIndex < ruleNames.size()) {
            outFile << "<" << ruleNames[ruleIndex] << ">" << std::endl;
        } else {
            outFile << "<unknownRule>" << std::endl;
        }
        indentLevel++;
    }

    // 处理非终结符的出口
    void exitEveryRule(antlr4::ParserRuleContext *ctx) override {
        indentLevel--;
        printIndent();
        int ruleIndex = ctx->getRuleIndex();
        if (ruleIndex >= 0 && ruleIndex < ruleNames.size()) {
            outFile << "</" << ruleNames[ruleIndex] << ">" << std::endl;
        } else {
            outFile << "</unknownRule>" << std::endl;
        }
    }

    // 处理终结符（叶节点）
    void visitTerminal(antlr4::tree::TerminalNode *node) override {
        printIndent();
        int tokenType = node->getSymbol()->getType();
        std::string tokenName = (std::string)vocab.getSymbolicName(tokenType);

        // 如果 SymbolicName 不存在，尝试获取 LiteralName
        if (tokenName.empty()) {
            tokenName = vocab.getLiteralName(tokenType);
        }

        // 如果 LiteralName 仍为空，则标记为未知终结符
        if (tokenName.empty()) {
            tokenName = "UNKNOWN_TOKEN";
        } else {
            // 去掉 LiteralName 中的引号，例如：'auto' -> auto
            tokenName.erase(std::remove(tokenName.begin(), tokenName.end(), '\''), tokenName.end());
        }

        std::string text = node->getText();

        // 转义特殊字符以确保 XML 格式正确
        size_t pos = 0;
        while ((pos = text.find('&', pos)) != std::string::npos) {
            text.replace(pos, 1, "&amp;");
            pos += 5;
        }
        pos = 0;
        while ((pos = text.find('<', pos)) != std::string::npos) {
            text.replace(pos, 1, "&lt;");
            pos += 4;
        }
        pos = 0;
        while ((pos = text.find('>', pos)) != std::string::npos) {
            text.replace(pos, 1, "&gt;");
            pos += 4;
        }
        pos = 0;
        while ((pos = text.find('\'', pos)) != std::string::npos) {
            text.replace(pos, 1, "&apos;");
            pos += 6;
        }
        pos = 0;
        while ((pos = text.find('\"', pos)) != std::string::npos) {
            text.replace(pos, 1, "&quot;");
            pos += 6;
        }

        outFile << "<" << tokenName << ">" << text << "</" << tokenName << ">" << std::endl;
    }

};

#endif // XMLGENERATORLISTENER_H
