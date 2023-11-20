int multiple_of_three(int x)
    requires x >= 0;
    requires exists (int m). x == 3 * m;
    ensures return % 3 == 1;
{
    return x + 1;
}