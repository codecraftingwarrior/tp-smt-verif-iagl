int array()
    ensures return == 7;
{
    int r[2];
    r[0] = 2;
    r[1] = 3;
    r[1] = r[0] + r[1];
    r[1] = r[0] + r[1];
    return r[1];
}