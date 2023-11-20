# la vérification de la terminaison doit échouer car l'expression 'r' ne décroît pas strictement à chaque itération
int bad_decrease(int x)
    requires x >= 0;
{
  int r;
  r = x;
  while (r >= 0)
      decreases r;
  {
      if (r % 2 == 0) {
          r = r - 1;
      }
  }
  return r;
}