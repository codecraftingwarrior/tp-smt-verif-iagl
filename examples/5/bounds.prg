# la vérification de ce programme doit échouer faute de garantie sur la valeur de x
int bounds(int x)
    ensures true;
{
    int r[2];
    r[x] = 7;
    return 0;
}