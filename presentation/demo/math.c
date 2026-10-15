// math.c - Исходный код на C для демонстрации компиляции в WebAssembly
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}
