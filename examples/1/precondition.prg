# ce programme est vérifiable, grâce à la pré-condition
int f(int x)
  requires x % 2 == 0;
  ensures return % 2 == 1;
{
  return x + 5;
}