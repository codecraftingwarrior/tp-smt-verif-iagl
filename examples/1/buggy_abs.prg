# la vérification de ce programme doit échouer
int abs(int x)
  ensures return == x | return == -x;
  ensures return >= 0;
{
  int r;
  r = x;
  if (r < 2) {
    r = -r;
  } 
  return r;
}