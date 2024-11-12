int printf(const char *format, ...);
int scanf(const char *format, ...);
int strlen(const char *str);

void isPalindrome(char s[]) {
    int len = strlen(s);
    int i;
    for (i = 0; i < len / 2; i++) {
        if (s[i] != s[len - i - 1]) {
            printf("False\n");
            return;
        }
    }
    printf("True\n");
}

int main() {
    char s[100];
    printf("请输入字符串: ");
    scanf("%s", s);
    isPalindrome(s);
    return 0;
}