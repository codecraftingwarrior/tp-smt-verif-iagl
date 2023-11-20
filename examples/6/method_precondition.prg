int f(int x)
    requires x >= 3;
{
    return x + 1;
}

# la vérification de ce programme doit échouer faute de garantie sur la valeur de x passée à f
int g(int x)
    requires x >= 0;
{
    return f(x) + 2;
}