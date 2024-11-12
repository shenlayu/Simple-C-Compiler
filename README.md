# Simple C11 Syntax Analyzer

This repository contains a simple yet efficient syntax analyzer for the C programming language, based on the **C11 standard** as defined in the [ISO/IEC 9899:2011 document (N1570)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf). The project is designed to be lightweight and independent of existing parser generators like **ANTLR** or **YACC**, utilizing a **LALR(1)** parsing technique to provide high performance and compact storage.

---

## Features

- **Full C11 Syntax Support (excluding preprocessing):**
  - Handles all C11 grammar rules and constructs except for preprocessing directives.
  - Based on the formal grammar and lexical rules from the C11 standard (N1570).
- **Independent Parsing Implementation:**
  - Does not rely on any external tools like ANTLR or YACC.
- **Efficient Table Generation:**
  - Implements LALR(1) parsing from scratch, optimizing **ACTION** and **GOTO** tables to reduce memory usage.
  - Faster parsing speed compared to traditional LR(1) parsing.
- **Alternative Parsing Methods (Deprecated):**
  - Supports parsing based on **ANTLR** and **C++ implementations** but is no longer maintained and may not guarantee correctness.

---

## Getting Started

### Prerequisites

- **Python 3.8+**: Ensure you have Python installed on your system.

### Installation

1. Clone the repository:
   ```bash
   $ git clone https://github.com/shenlayu/Simple-C-Compiler.git
   $ cd Simple-C-Compiler/antlr_free/python
   $ python builder.py
   $ python parser.py
   (input the c file)
   ```
