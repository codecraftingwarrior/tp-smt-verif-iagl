int div(int x, int y)
  requires x >= 0;
  requires y > 0;
  ensures x / y == return;
{
  int r;
  int z;
  z = x;
  r = 0;
  while (z >= y)
    invariant z + (r * y) == x;
    invariant 0 <= z;
    invariant z <= x;
    invariant y > 0;
    decreases z;
  {
    z = z - y;
    r = r + 1;
  }
  return r;
}