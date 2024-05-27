import sympy
import random
import simple_eqops
from sympy.abc import x,y


class simpleEquTable(object):
    
    def __init__(self):
        #operations in use. check eqops.py
        self.functions = {'lisaa':simple_eqops.addlr,
                          'vahenna':simple_eqops.substrlr,
                          'kerro':simple_eqops.multiplr,
                          'jaa':simple_eqops.dividelr}
        self.sizetable = 30 #number of maximum phases
        self.equbase = EquBase() #create instance from equation database
        self.sizeLhs, self.sizeRhs = self.equbase.get_dbSize() #get the size of predefined equation database
        
        #pick the left and right hand sides for equation randomly
        self.randLhs = random.randint(0,self.sizeLhs-1) 
        self.randRhs = random.randint(0,self.sizeRhs-1)
        LhsTmp, RhsTmp = self.equbase.get_equation(self.randLhs,self.randRhs)
        
        #create the equation table
        self.equTableLhs = [LhsTmp]
        self.equTableRhs = [RhsTmp]
        self.equTableIndx = 0
    
    #method for eqaution transformations    
    def equTransf(self,op,mod_expr):
        func = self.functions[op] #operation chosen
        newLhs, newRhs, errorF = func(mod_expr,self.equTableLhs[self.equTableIndx],self.equTableRhs[self.equTableIndx])
        self.equTableLhs.append(newLhs)
        self.equTableRhs.append(newRhs)
        self.equTableIndx += 1
        
    def getEquTable(self):
        return self.equTableLhs, self.equTableRhs
    
    def getLastEqu(self):
        return self.equTableLhs[self.equTableIndx],self.equTableRhs[self.equTableIndx]
        
class EquBase(object):
        
    def __init__(self):
        self.equlistLeft = [x-2,2*x+1,x+4]
        self.equlistRight = [3,-x-5,3*x+6]
        
    def get_equation(self,ixLeft,ixRight):
        return self.equlistLeft[ixLeft],self.equlistRight[ixRight]
        
    def get_dbSize(self):
        return len(self.equlistLeft), len(self.equlistRight)
        
        
    