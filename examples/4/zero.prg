int zero()
  ensures forall (int y). y * return == return;
{
  return 0;
}