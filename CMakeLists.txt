cmake_minimum_required(VERSION 3.10)
project(LHW1_Project)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# 启用 macOS 的 RPATH 支持
set(CMAKE_MACOSX_RPATH TRUE)

# 设置 ANTLR 工具路径
set(ANTLR_JAR /Users/qiaoshenyu/Desktop/antlr/antlr-4.13.2-complete.jar) # 请替换为实际路径

# 设置生成的源代码目录
set(GENERATED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generated)

# 创建生成目录（如果不存在）
file(MAKE_DIRECTORY ${GENERATED_DIR})

# 初始化生成的源文件和头文件列表
set(GENERATED_SOURCES)
set(GENERATED_HEADERS)

# 手动为每个 .g4 文件指定生成的文件名

# 处理 CLexer.g4
set(G4_FILE_LEXER "${CMAKE_CURRENT_SOURCE_DIR}/rule/C.g4")
set(OUTPUT_PARSER_CPP "${GENERATED_DIR}/CParser.cpp")
set(OUTPUT_PARSER_H "${GENERATED_DIR}/CParser.h")
set(OUTPUT_LEXER_CPP "${GENERATED_DIR}/CLexer.cpp")
set(OUTPUT_LEXER_H "${GENERATED_DIR}/CLexer.h")
set(OUTPUT_BASELISTENER_CPP "${GENERATED_DIR}/CBaseListener.cpp")
set(OUTPUT_BASELISTENER_H "${GENERATED_DIR}/CBaseListener.h")


add_custom_command(
    OUTPUT ${OUTPUT_LEXER_CPP} ${OUTPUT_LEXER_H} ${OUTPUT_PARSER_CPP} ${OUTPUT_PARSER_H} ${OUTPUT_BASELISTENER_CPP} ${OUTPUT_BASELISTENER_H}
    COMMAND java -jar ${ANTLR_JAR} -Dlanguage=Cpp -o ${GENERATED_DIR} ${G4_FILE_LEXER}
    DEPENDS ${G4_FILE_LEXER}
    COMMENT "Generating C++ files from ${G4_FILE_LEXER}"
)

list(APPEND GENERATED_SOURCES ${OUTPUT_LEXER_CPP})
list(APPEND GENERATED_HEADERS ${OUTPUT_LEXER_H})

list(APPEND GENERATED_SOURCES ${OUTPUT_PARSER_CPP})
list(APPEND GENERATED_HEADERS ${OUTPUT_PARSER_H})



# 添加生成的源文件和头文件到一个静态库
add_library(lhw1_parser STATIC ${GENERATED_SOURCES} ${GENERATED_HEADERS})

# 查找 ANTLR4 运行时库

# 1. 查找 ANTLR4 运行时的包含目录
find_path(ANTLR4_INCLUDE_DIR antlr4-runtime.h
    PATHS /usr/local/include/antlr4-runtime /usr/include
    NO_DEFAULT_PATH
)

if(NOT ANTLR4_INCLUDE_DIR)
    message(FATAL_ERROR "Could not find ANTLR4 runtime include directory")
endif()

# 2. 查找 ANTLR4 运行时库
find_library(ANTLR4_LIB antlr4-runtime
    PATHS /usr/local/lib /usr/lib
    NO_DEFAULT_PATH
)

if(NOT ANTLR4_LIB)
    message(FATAL_ERROR "Could not find ANTLR4 runtime library")
endif()

# 3. 包含生成的头文件目录和 ANTLR4 运行时库的包含路径
target_include_directories(lhw1_parser PUBLIC 
    ${GENERATED_DIR} 
    ${ANTLR4_INCLUDE_DIR}
)

# 4. 链接 ANTLR4 运行时库
target_link_libraries(lhw1_parser PUBLIC ${ANTLR4_LIB})

# 设置库的 RPATH，以便依赖库在运行时能被找到
set_target_properties(lhw1_parser PROPERTIES
    BUILD_RPATH "/usr/local/lib"
    INSTALL_RPATH "/usr/local/lib"
)

# 添加可执行文件
add_executable(lhw1_executable src/main.cpp)

# 包含生成的头文件目录
target_include_directories(lhw1_executable PUBLIC ${GENERATED_DIR})

# 链接解析器库和 ANTLR4 运行时库
target_link_libraries(lhw1_executable PRIVATE lhw1_parser ${ANTLR4_LIB})

# 设置可执行文件的 RPATH，使其在运行时查找 /usr/local/lib
set_target_properties(lhw1_executable PROPERTIES
    BUILD_RPATH "/usr/local/lib"
    INSTALL_RPATH "/usr/local/lib"
    BUILD_WITH_INSTALL_RPATH TRUE
)
