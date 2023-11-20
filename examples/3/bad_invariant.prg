# la vérification de la boucle doit échouer car l'invariant n'est pas toujours maintenu
int bad_invariant(int x)
    requires x >= 0;
    requires x % 2 == 0;
{
    int r;
    r = x;
    while (r >= 0)
        invariant r % 2 == 0;
        decreases r;
    {
        if (r == 62) {
            r = r - 1;
        } else {
            r = r - 2;
        }
    }
    return r;
}