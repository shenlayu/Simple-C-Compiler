int printf(const char *format, ...);
int scanf(const char *format, ...);
int strlen(const char *str);

void computeLPSArray(char* pat, int M, int* lps) {
    int len = 0, i = 1;
    lps[0] = 0;
    while (i < M) {
        if (pat[i] == pat[len]) {
            len++;
            lps[i] = len;
            i++;
        } else {
            if (len != 0) {
                len = lps[len - 1];
            } else {
                lps[i] = 0;
                i++;
            }
        }
    }
}

void KMPSearch(char* pat, char* txt) {
    int M = strlen(pat);
    int N = strlen(txt);
    int lps[M];
    computeLPSArray(pat, M, lps);

    int i = 0, j = 0, found = 0;
    while (i < N) {
        if (pat[j] == txt[i]) {
            j++;
            i++;
        }
        if (j == M) {
            printf("%d ", i - j);
            found = 1;
            j = lps[j - 1];
        } else if (i < N && pat[j] != txt[i]) {
            if (j != 0)
                j = lps[j - 1];
            else
                i++;
        }
    }
    if (!found) {
        printf("False");
    }
    printf("\n");
}

int main() {
    char s[100], t[100];
    printf("请输入主字符串: ");
    scanf("%s", s);
    printf("请输入模板字符串: ");
    scanf("%s", t);
    KMPSearch(t, s);
    return 0;
}