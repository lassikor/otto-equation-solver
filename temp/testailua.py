import unicodedata
import jyrclasses
from itertools import combinations
import jyrlatex
from jyrops import handleTree
from jyrsympify import *
from sympy import Add, Mul, Pow, Integer,Rational,symbols, ratsimp
from jyrequhandle import *
import webelements

x = symbols('x')
a=jyrsympify('x-2*(x-1)+1', evaluate = False)
#a = Mul(-1,x-1,evaluate = False)
print(jyrlatex.latex(a))
# 
# def common_factor_combs(expr_args,new_expr_args,factor):
#     comb_terms = list(combinations(expr_args,2))
#     for termpair in comb_terms:
#         addterm = Add(termpair[0],termpair[1], evaluate = False)
#         divid = ratsimp(Mul(addterm,Pow(factor,-1), evaluate = True))
#         if isinstance(divid, (Integer, int, Rational)):
#             new_expr_args.append(Mul(divid, factor, evaluate = False))
#             expr_args.remove(termpair[0])
#             expr_args.remove(termpair[1])
#             expr_args, new_expr_args = common_factor_combs(expr_args, new_expr_args, factor)
#             break
#     return expr_args, new_expr_args
# x = symbols('x')
# alist = [Mul(2,x+1,evaluate=False),-x,-1]
# print(common_factor_combs(alist, [], x+1))
#===============================================================================
# ex1 = Add(2,3,evaluate=False)
# ex1 = Mul(3,ex1,evaluate=False)
# ex1 = Add(3,ex1,evaluate=False)
# print(ex1)
# expr_str1 = 'x+2*3*(x-3*(x+2))'
# equT = EquTable()
# equlhs_str, equrhs_str = equT.getEquTable()
# equlhs, equrhs = jyrsympify(equlhs_str, evaluate = False), jyrsympify(equrhs_str, evaluate = False)
# last_equ_lhs,last_equ_rhs = equlhs[-1],equrhs[-1]
# num_colors_l = jyrops.get_colors_num(last_equ_lhs,'x')
# num_colors_r = jyrops.get_colors_num(last_equ_rhs,'x')
# # equT.exprMods('poista_sulut', 'black', 'right', 'dum')
# equT.equTransf('lisaa', '4*(x-5)')
# equlhs_str, equrhs_str = equT.getEquTable()
# equlhs, equrhs = jyrsympify(equlhs_str, evaluate = False), jyrsympify(equrhs_str, evaluate = False)
# last_equ_lhs,last_equ_rhs = equlhs[-1],equrhs[-1]
# num_colors_l = jyrops.get_colors_num(last_equ_lhs,'x')
# num_colors_r = jyrops.get_colors_num(last_equ_rhs,'x')
# dropmenu_color_l = webelements.get_color_dropmenu(num_colors_l,'l')
# dropmenu_color_r = webelements.get_color_dropmenu(num_colors_r,'r')
# 
# # expr_str2 = '2+2*x+(4+2+3)*(x-2)'
# # expr_str3 = '2+2*(2*x+2*x+2)'
# # expr_str4 = '2+2*(x-2)+2*x'
# 
# sym_expr1 = jyrsympify(expr_str1, evaluate=False)
# # sym_expr2 = jyrsympify(expr_str2)
# # sym_expr3 = jyrsympify(expr_str3)
# # sym_expr4 = jyrsympify(expr_str4)
# latex(sym_expr1)
# 
# # latex(sym_expr2)
# # latex(sym_expr3)
# # latex(sym_expr4)
# hT1 = handleTree(sym_expr1)
# print(hT1.color_dict)
# expr2,dum=hT1.remove_braces('green')
# latex(expr2)
# hT2 =handleTree(expr2)
# hT2.remove_braces('green')
# # hT3 = handleTree(sym_expr3)
# # hT2 = handleTree(sym_expr2)
# # print(hT1.color_dict)
# # print(sym_expr1.args)
# # print(hT1.remove_braces('green'))
#===============================================================================
