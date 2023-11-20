# ce programme est vérifiable, grâce à la pré-condition
int ex_falso()
  requires false;
  ensures return == 2;
{
  return 1;
}