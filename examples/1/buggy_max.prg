# la vérification de ce programme doit échouer
int max(int x, int y)
  ensures return == x | return == y;
  ensures return >= x;
  ensures return >= y; 
{
  int r;
  if (x >= y) {
    r = x;
  } else {
    if (x == 2) {
      r = 3;
    } else {
      r = y;
    }
  } 
  return r;
}