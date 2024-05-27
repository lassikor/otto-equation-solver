from __future__ import print_function, division

from sympy.core import *


class jyrInt(Integer):
    def __new__(cls, value,*args,**kwargs):
        return super(jyrInt,cls).__new__(cls, int(value))            

class jyrSym(Symbol):
    pass

class jyrAdd(Add):    
    pass

class jyrMul(Mul):
    pass
    
class jyrPow(Pow):
    pass

class jyrExpr(Expr):
    pass