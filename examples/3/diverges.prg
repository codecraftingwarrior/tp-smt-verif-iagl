# la vérification de la terminaison doit échouer car l'expression '-r' n'a pas de borne inférieure
int diverges(int x)
{
  int r;
  r = x;
  while (r >= 0)
    decreases -r;
  {
    r = r + 1;
  }
  return r;
}