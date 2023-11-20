int seven(int x)
    requires x >= 0;
    ensures return == 7;
{
    if (x < 0) {
        return 8;
    }
    int y;
    y = 3;
    if (y == 3) {
        y = y + 4;
    }
    if (y == 6) {
        return 4;
    } else {
        return y;
    }
}