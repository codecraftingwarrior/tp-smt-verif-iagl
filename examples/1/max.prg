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