from abc import *
from enum import Enum
from lark import Lark, Transformer, v_args
import sys
import z3

# le nom de la variable qui correspond à la valeur de retour de la méthode
RETURN_VAR = "return"


class VarType(Enum):
    INT = 1
    BOOL = 2

class Instr:

    @abstractmethod
    def weakest_precondition(self, postcondition):
        pass

class SkipInstr(Instr):

    def weakest_precondition(self, postcondition):
        # pour le programme vide, la pré-condition la plus faible pour une post-condition Q, est Q
        return postcondition

class SeqInstr(Instr):

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def weakest_precondition(self, postcondition):
        intermediate_condition = self.p2.weakest_precondition(postcondition)
        return self.p1.weakest_precondition(intermediate_condition)

class CondInstr(Instr):

    def __init__(self, condition, ptrue, pfalse):
        if not z3.is_bool(condition):
            raise Exception("loop condition must be a boolean expression")
        self.condition = condition
        self.ptrue = ptrue
        self.pfalse = pfalse

    def weakest_precondition(self, postcondition):
        wp_true = self.ptrue.weakest_precondition(postcondition)
        wp_false = self.pfalse.weakest_precondition(postcondition)
        return z3.Or(z3.And(self.condition, wp_true), z3.And(z3.Not(self.condition), wp_false))
    
class AsgnInstr(Instr):

    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def weakest_precondition(self, postcondition):
        return z3.substitute(postcondition, (self.var, self.expr))

class AnalyzerException(Exception):
    pass

grammar = r"""
    ?start: method

    ?method: method_decl specification* "{" method_body "}"

    ?method_body: instrs return_instr -> set_method_body

    ?method_decl: type CNAME "(" [var_decl_list] ")" -> set_method_signature

    ?type : "int" -> int_type
          | "bool" -> bool_type

    ?var_decl_list: var_decl ("," var_decl)*

    ?var_decl: type CNAME -> declare_var

    ?specification: "requires" expr ";" -> add_precondition
                  | "ensures" expr ";" -> add_postcondition

    ?instrs: instr* -> instr_seq

    ?instr: "if" expr "{" instrs "}" ["else" "{" instrs "}"] -> conditional_instr
            | var_decl ";" -> decl_instr
            | CNAME "=" expr ";" -> asgn_instr

    ?return_instr: "return" expr ";" -> return_instr

    ?expr: and_expr ("|" and_expr)* -> disj
    ?and_expr: not_expr ("&" not_expr)* -> conj
    ?not_expr: "!" not_expr -> neg
             | comparison
             | arith_expr
    ?comparison: arith_expr comp_op arith_expr -> comp
    ?arith_expr: factor_expr (arith_op factor_expr)* -> arith
    ?factor_expr: term_expr (factor_op term_expr)* -> arith
    ?term_expr: "-" term_expr -> minus
              | atom
    ?atom: NUMBER -> number
         | "true" -> true
         | "false" -> false
         | CNAME -> var
         | "(" expr ")"
    ?comp_op: "<" -> ltfun
            | "<=" -> lefun
            | ">" -> gtfun
            | ">=" -> gefun
            | "==" -> eqfun
            | "!=" -> nefun
    ?arith_op: "+" -> addfun
             | "-" -> subfun
    ?factor_op: "*" -> mulfun
              | "/" -> divfun
              | "%" -> modfun


    COMMENT: /#[^\n]*/

    %import common.NUMBER
    %import common.CNAME
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""

@v_args(inline=True)
class ProgramAnalyzer(Transformer):

    def __init__(self):
        self.var_types = {}
        self.method_name = None
        self.method_return_type = None
        self.preconditions = []
        self.postconditions = []
        self.method_body = None

    def set_method_body(self, program, return_instr):
        self.method_body = SeqInstr(program, return_instr)

    def set_method_signature(self, return_type, name, ignore_arg1):
        self.method_name = name
        self.method_return_type = return_type
        self.declare_var(return_type, RETURN_VAR)

    def add_precondition(self, expr):
        self.check_type(expr, VarType.BOOL)
        self.preconditions.append(expr)

    def add_postcondition(self, expr):
        self.check_type(expr, VarType.BOOL)
        self.postconditions.append(expr)

    def instr_seq(self, *instr):        
        if len(instr) == 0:
            return SkipInstr()
        elif len(instr) == 1:
            return instr[0]
        else:
            return SeqInstr(instr[0], self.instr_seq(*instr[1:]))

    def skip_instr(self):
        return SkipInstr()

    def asgn_instr(self, name, expr):
        if name not in self.var_types:
            raise AnalyzerException("variable '" + name + "' is not defined")
        match self.var_types[name]:
            case VarType.INT:
                self.check_type(expr, VarType.INT)
                var = z3.Int(name)
            case VarType.BOOL:
                self.check_type(expr, VarType.Bool)
                var = z3.Bool(name)
            case default:
                assert False
        return AsgnInstr(var, expr)

    def decl_instr(self, decl):
        return SkipInstr()

    def return_instr(self, e):
        # l'instruction "return" est autorisée uniquement comme dernière instruction d'une méthode
        # on la représente par une affectation à une variable appelée "return"
        return self.asgn_instr(RETURN_VAR, e)
    
    def conditional_instr(self, cond, ptrue, pfalse):
        if pfalse == None:
            return CondInstr(cond, ptrue, SkipInstr())
        return CondInstr(cond, ptrue, pfalse)

    def declare_var(self, ty, name):
        if name in self.var_types:
            raise Exception("duplicate variable name")
        self.var_types[name] = ty

    def true(self):
        return z3.And()

    def false(self):
        return z3.Or()

    def neg(self, e):
        self.check_type(e, VarType.BOOL)
        return z3.Not(e)

    def conj(self, *exprs):
        if len(exprs) == 1:
            # les règles du parseur font remonter les expressions arithmétiques comme des conjonctions unaires
            return exprs[0]
        for e in exprs:
            self.check_type(e, VarType.BOOL)
        return z3.And(exprs)

    def disj(self, *exprs):
        if len(exprs) == 1:
            # les règles du parseur font remonter les expressions arithmétiques comme des disjonctions unaires
            return exprs[0]
        for e in exprs:
            self.check_type(e, VarType.BOOL)
        return z3.Or(exprs)

    def comp(self, e1, op, e2):
        self.check_type(e1, VarType.INT)
        self.check_type(e2, VarType.INT)
        return op(e1, e2)

    def arith(self, *exprs):
        if len(exprs) == 1:
            # les règles du parser font remonter certaines expressions booléennes comme opérations arithmétiques unaires
            return exprs[0]
        else:
            self.check_type(exprs[0], VarType.INT)
            assert len(exprs) > 2
            e2 = self.arith(*exprs[2:])
            self.check_type(e2, VarType.INT)
            return exprs[1](exprs[0], e2)

    def number(self, n):
        return z3.IntVal(n)

    def ltfun(self):
        return z3.ArithRef.__lt__

    def lefun(self):
        return z3.ArithRef.__le__

    def gtfun(self):
        return z3.ArithRef.__gt__

    def gefun(self):
        return z3.ArithRef.__ge__

    def eqfun(self):
        return z3.ExprRef.__eq__

    def nefun(self):
        return z3.ExprRef.__ne__

    def minus(self, e):
        self.check_type(e, VarType.INT)
        return z3.ArithRef.__neg__(e)

    def addfun(self):
        return z3.ArithRef.__add__

    def subfun(self):
        return z3.ArithRef.__sub__

    def mulfun(self):
        return z3.ArithRef.__mul__

    def divfun(self):
        return z3.ArithRef.__div__

    def modfun(self):
        return z3.ArithRef.__mod__
        
    def var(self, name):
        if name not in self.var_types:
            raise AnalyzerException("variable '" + name + "' is not defined")
        match self.var_types[name]:
            case VarType.INT:
                return z3.Int(name)
            case VarType.BOOL:
                return z3.Bool(name)
            case default:
                assert False

    def check_type(self, expr, ty):
        match ty:
            case VarType.INT:
                expected = "int"
                well_typed = z3.is_int(expr)

            case VarType.BOOL:
                expected = "bool"
                well_typed = z3.is_bool(expr)
            case default:
                assert False
        if not well_typed:
            raise AnalyzerException("typing error, expression '" + str(expr) + "' is expected to be of type '" + expected + "'")
        
    def int_type(self):
        return VarType.INT

    def bool_type(self):
        return VarType.INT

analyzer = ProgramAnalyzer()
parser = Lark(grammar, parser='lalr', transformer=analyzer)
program = parser.parse

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: python verify.py FILE")
        exit()

    with open(sys.argv[1], 'r') as file:
        try:
            program(file.read())
        except AnalyzerException as e:
            print(str(e))
            exit()
    
    # Extrait les pré-conditions et post-conditions définies dans le programme analysé
    preconditions = analyzer.preconditions
    postconditions = analyzer.postconditions
    method_body = analyzer.method_body

    # Initialisation du solveur Z3
    s = z3.Solver()
    
    # Ajoute les pré-conditions du programme au solveur Z3 comme contraintes
    for pre in preconditions: s.add(pre)

    # Calcul de la pré-condition la plus faible pour tout le programme
    wp = method_body.weakest_precondition(z3.And(postconditions))

    # Ajoute la négation de la pré-condition la plus faible au solveur pour tester sa validité
    s.add(z3.Not(wp))

    # Résultat de la vérification
    if s.check() == z3.sat:
        print("La vérification a échoué. Les pré-conditions ne garantissent pas la post-condition. => Le programme répond à sa spécification.")
    else:
        print("La vérification a réussi. Les pré-conditions garantissent la post-condition. => Le programme ne répond pas à sa specification.")