# la vérification doit échouer car l'invariant est trop faible
int weak_invariant(int x)
    requires x >= 0;
    ensures return % 2 == 0 & return >= 0;
{
    int r;
    int z;
    r = x;
    z = 0;
    while (r >= 0)
        invariant z % 2 == 0;
        invariant x >= 0;
        decreases r;
    {
        z = z + 6;
        r = r - 1;
    }
    return z;
}