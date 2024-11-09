int printf(const char *format, ...);
int scanf(const char *format, ...);
int isspace(int c);
int isdigit(int c);
unsigned long strlen(const char *);

#define MAX_SIZE 100

typedef struct {
    int data[100];
    int top;
} Stack;

void initStack(Stack* s) {
    s->top = -1;
}

int isEmpty(Stack* s) {
    return s->top == -1;
}

void push(Stack* s, int val) {
    if (s->top < MAX_SIZE - 1) {
        s->data[++s->top] = val;
    }
}

int pop(Stack* s) {
    if (isEmpty(s)) return 0;
    return s->data[s->top--];
}

int peek(Stack* s) {
    if (isEmpty(s)) return 0;
    return s->data[s->top];
}

int precedence(char op) {
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/') return 2;
    return 0;
}

int applyOp(int a, int b, char op) {
    switch (op) {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/': return a / b;
    }
    return 0;
}

int evaluate(char* tokens) {
    int i;
    Stack values, ops;
    initStack(&values);
    initStack(&ops);

    for (i = 0; i < strlen(tokens); i++) {
        if (isspace(tokens[i])) continue;
        if (tokens[i] == '(') {
            push(&ops, tokens[i]);
        } else if (isdigit(tokens[i])) {
            int val = 0;
            while (i < strlen(tokens) && isdigit(tokens[i])) {
                val = (val * 10) + (tokens[i] - '0');
                i++;
            }
            i--;
            push(&values, val);
        } else if (tokens[i] == ')') {
            while (!isEmpty(&ops) && peek(&ops) != '(') {
                int val2 = pop(&values);
                int val1 = pop(&values);
                char op = pop(&ops);
                push(&values, applyOp(val1, val2, op));
            }
            pop(&ops);
        } else {
            while (!isEmpty(&ops) && precedence(peek(&ops)) >= precedence(tokens[i])) {
                int val2 = pop(&values);
                int val1 = pop(&values);
                char op = pop(&ops);
                push(&values, applyOp(val1, val2, op));
            }
            push(&ops, tokens[i]);
        }
    }

    while (!isEmpty(&ops)) {
        int val2 = pop(&values);
        int val1 = pop(&values);
        char op = pop(&ops);
        push(&values, applyOp(val1, val2, op));
    }

    return pop(&values);
}

int main() {
    char expr[100];
    printf("请输入表达式: ");
    scanf("%s", expr);
    printf("计算结果: %d\n", evaluate(expr));
    return 0;
}