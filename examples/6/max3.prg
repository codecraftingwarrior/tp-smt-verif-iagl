int max(int x, int y)
    ensures return == x | return == y;
    ensures return >= x;
    ensures return >= y;
{
    int r;
    if (x >= y) {
        r = x;
    } else {
        r = y;
    } 
    return r;
}

int max_of_three(int x, int y, int z)
    ensures return == x | return == y | return == z;
    ensures return >= x;
    ensures return >= y;
    ensures return >= z;
{
    return max(x, max(y, z));
}