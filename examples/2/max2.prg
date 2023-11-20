int max(int x, int y)
    ensures return == x | return == y;
    ensures return >= x;
    ensures return >= y; 
{
    if (x >= y) {
        return x;
    } else {
        return y;
    }
}