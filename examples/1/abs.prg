int abs(int x)
  ensures return == x | return == -x;
  ensures return >= 0;
{
  int r;
  r = x;
  if (r < 0) {
    r = -r;
  } 
  return r;
}