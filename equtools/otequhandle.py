# -*- coding: utf8 -*-
import otops
import random
from sympy import latex, solve, Mul, symbols
from otsympify import otsympify


class EquTable(object):
    
    def __init__(self, mode = 'adv'):
        #operations in use. check otops.py
        self.functions = {'add':otops.addlr,
                          'add_eval':otops.addlr_eval,
                          'subs':otops.substrlr,
                          'mul':otops.multiplr,
                          'mul_expr':otops.multiplr_expr,
                          'div':otops.dividelr}
        
        self.func_texts = {'add': r'\ \mbox{ Lis&#228;sin puolittain }',
                          'subs': r'\ \mbox{ V&#228;hensin puolittain }',
                          'mul': r'\ \mbox{ Kerroin puolittain sievent&#228;en termill&#228; }',
                          'div': r'\ \mbox{ Jaoin puolittain sievent&#228;en termill&#228; }',
                          'mul_expr': r'\ \mbox{ Kerroin puolittain termill&#228; }',
                          'err': r'\ \mbox{ Jakajan tai kertojan pit&#228;&#228; olla jokin luku }\neq 0'}
        # self.func_ids = {'add': r'& \ \ \mbox{L}',
        #                   'subs': r'& \ \ \mbox{V}',
        #                   'mul': r'& \ \ \mbox{K}',
        #                   'mul_expr': r'& \ \ \mbox{K}',
        #                   'div': r'& \ \ \mbox{J}'}
      
        self.mod_functions = {'remove_braces':otops.open_braces,
                              'common_factor':otops.collect_comm_fact,
                              'merge_terms':otops.collect_terms}

        if not mode == 'inv': 
            LhsTmp, RhsTmp = create_equ(mode)
            symLhsTmp = otsympify(LhsTmp)
            symRhsTmp = otsympify(RhsTmp)
            self.solution = solve(symLhsTmp-symRhsTmp)
        else:
            LhsTmp, RhsTmp = '0','0'
            symLhsTmp = otsympify(LhsTmp)
            symRhsTmp = otsympify(RhsTmp)

        #create the equation table
        self.equTableLhs = [LhsTmp]
        self.equTableRhs = [RhsTmp]
        self.equTableText = []
        self.equTableIndx = 0
        self.record = u'-'
        self.userEquLhs = []
        self.userEquRhs = []
        self.userEquRecord =[]
        self.userEquIx = None
        self.mode = mode
        if not len(symLhsTmp.free_symbols) == 0:
            self.symvar = str(symLhsTmp.free_symbols.pop())
        elif not len(symRhsTmp.free_symbols) == 0:
            self.symvar = str(symRhsTmp.free_symbols.pop())
        else:
            self.symvar = 'x'
            
    #method for equation transformations   
    def equTransf(self, op, mod_expr, evaluate = False):
        
        func = self.functions[op] #operation chosen
        newLhs, newRhs, errorF = func(mod_expr,self.equTableLhs[self.equTableIndx],self.equTableRhs[self.equTableIndx], evaluate = evaluate)
        mod_expr_tex = latex(otsympify(mod_expr, evaluate = False))
        if errorF == 1:
            newText = self.func_texts['err']+'.'
        else:
            newText = self.func_texts[op]+mod_expr_tex+'.'

        #check if there is zero addition or -1 multiplication and remove it
        #breakpoint()
        newLhs = otops.cleanzeros(newLhs)
        newRhs = otops.cleanzeros(newRhs)   
        newLhs = newLhs.replace(" - 1*"," - ")
        newRhs = newRhs.replace(" - 1*"," - ")
        newLhs = newLhs.replace("1*(","(")
        newRhs = newRhs.replace("1*(","(")
        #add both sides to table
        self.equTableLhs.append(newLhs)
        self.equTableRhs.append(newRhs)
        self.equTableText.append(newText)
        if not self.mode == 'inv' and newLhs == self.symvar and newRhs == str(self.solution[0]):
            self.equTableText.append(r'\ \mbox{ Hienoa! L&#246;ysin ratkaisun.}')
        elif not self.mode == 'inv' and newRhs == self.symvar and newLhs == str(self.solution[0]):
            self.equTableText.append(r'\ \mbox{ Hienoa! Ratkaisu on siis }'+self.symvar+r'='+str(self.solution[0]))
        self.equTableIndx += 1
    
    #Method for equation modifications   
    def exprMods(self, op, color, side, param1):
        breakpoint()
        func = self.mod_functions[op] #operation chosen
       
        if op == 'remove_braces':
            if side == 'left':
                newLhs, errorF = func(self.equTableLhs[self.equTableIndx], color)
                newRhs = self.equTableRhs[self.equTableIndx]
                newText = r'\ {\color{'+color+r'}\mbox{ Poistin sulut vasemmalta.}}'
            elif side == 'right':
                newRhs, errorF = func(self.equTableRhs[self.equTableIndx], color)
                newLhs = self.equTableLhs[self.equTableIndx]
                newText = r'\ {\color{'+color+r'}\mbox{ Poistin sulut oikealta.}}'
                
        elif op == 'common_factor':
            if side == 'left':
                newLhs, errorF = func(self.equTableLhs[self.equTableIndx], color, param1)
                newRhs = self.equTableRhs[self.equTableIndx]
                #param1 = latex(otsympify(param1, evaluate = False))
                newText = r'\ {\color{'+color+r'}\mbox{ Otin yhteisen tekij&#228;n }'+param1+r'\mbox{ vasemmalta.}}'
            elif side == 'right':
                newRhs, errorF = func(self.equTableRhs[self.equTableIndx], color, param1)
                newLhs = self.equTableLhs[self.equTableIndx]
                newText = r'\ {\color{'+color+r'}\mbox{ Otin yhteisen tekij&#228;n }'+param1+r'\mbox{ oikealta.}}'
                
        elif op == 'merge_terms':
            if side == 'left':
                newLhs, errorF = func(self.equTableLhs[self.equTableIndx], color, param1)
                newRhs = self.equTableRhs[self.equTableIndx]
                if param1 == 'const':
                    newText = r'\ {\color{'+color+r'}\mbox{ Yhdistin luvut vasemmalta.}}'
                else:
                    newText = r'\ {\color{'+color+r'}\mbox{ Yhdistin \('+self.symvar+r'\)-termit vasemmalta.}}'
                    
            elif side == 'right':
                newRhs, errorF = func(self.equTableRhs[self.equTableIndx], color, param1)
                newLhs = self.equTableLhs[self.equTableIndx]
                if param1 == 'const':
                    newText = r'\ {\color{'+color+r'}\mbox{ Yhdistin luvut oikealta.}} '
                else:
                    newText = r'\ {\color{'+color+r'}\mbox{ Yhdistin \('+self.symvar+r'\)-termit oikealta.}}'
                    
            elif side == 'both':
                newRhs, errorF = func(self.equTableRhs[self.equTableIndx], color, param1)
                newLhs, errorF = func(self.equTableLhs[self.equTableIndx], color, param1)
                if param1 == 'const':
                    newText = r'\ {\color{'+color+r'}\mbox{ Yhdistin luvut.}}'
                else:
                    newText = r'\ {\color{'+color+r'}\mbox{ Yhdistin \(x\)-termit.}}'
                
  
        #clean zeros
        newLhs = otops.cleanzeros(newLhs)
        newRhs = otops.cleanzeros(newRhs)    

        newLhs = newLhs.replace(" - 1*"," - ")
        newRhs = newRhs.replace(" - 1*"," - ")
        #breakpoint()
        #newLhs = newLhs.replace("1*(","(")
        #newRhs = newRhs.replace("1*(","(")

        #add both sides to table
        self.equTableLhs.append(newLhs)
        self.equTableRhs.append(newRhs)
        self.equTableText.append(newText)
        if not self.mode == 'inv' and newLhs == self.symvar and newRhs == str(self.solution[0]):
            self.equTableText.append(r'\ \mbox{ Hienoa! L&#246;ysin ratkaisun.}')
        elif not self.mode == 'inv' and newRhs == self.symvar and newLhs == str(self.solution[0]):
            self.equTableText.append(r'\ \mbox{ Hienoa! Ratkaisu on siis }'+self.symvar+r'='+str(self.solution[0])) 
        self.equTableIndx += 1
               
            
        
    def getEquTable(self):
        return self.equTableLhs, self.equTableRhs, self.equTableText
    
    def clearEquTable(self, mode=' adv', new = 0):
        old_equ_lhs,  old_equ_rhs = self.equTableLhs[0], self.equTableRhs[0]
        self.equTableLhs = []
        self.equTableRhs = []
        self.equTableText = []
        self.equTableIndx = 0
        if new == 0:
            self.equTableLhs.append(old_equ_lhs)
            self.equTableRhs.append(old_equ_rhs)
        else:
            LhsTmp, RhsTmp = create_equ(mode)
            symLhsTmp = otsympify(LhsTmp)
            symRhsTmp = otsympify(RhsTmp)
            self.solution = solve(symLhsTmp-symRhsTmp)
            if not len(symLhsTmp.free_symbols) == 0:
                self.symvar = str(symLhsTmp.free_symbols.pop())
            elif not len(symRhsTmp.free_symbols) == 0:
                self.symvar = str(symRhsTmp.free_symbols.pop())

            #create the equation table
            self.equTableLhs = [LhsTmp]
            self.equTableRhs = [RhsTmp]
            self.record = u'-'
            self.userEquIx = None
    
    def getLastEqu(self):
        return self.equTableLhs[self.equTableIndx],self.equTableRhs[self.equTableIndx]
    
    #Method for quation table initialization
    def initEquTable(self, k, mode='user',new_equ_lhs='', new_equ_rhs='', new_equ_text=''):
        
        if mode == 'user':
            self.equTableLhs = []
            self.equTableRhs = []
            self.equTableLhs.append(self.userEquLhs[k])
            self.equTableRhs.append(self.userEquRhs[k])
            symLhsTmp = otsympify(self.userEquLhs[k])
            symRhsTmp = otsympify(self.userEquRhs[k]) 
            if not len(symLhsTmp.free_symbols) == 0:
                self.symvar = str(symLhsTmp.free_symbols.pop())
            elif not len(symRhsTmp.free_symbols) == 0:
                self.symvar = str(symRhsTmp.free_symbols.pop())
            else:
                self.symvar = 'x'
            self.userEquIx = k
            self.solution = solve(otsympify(self.userEquLhs[k])-otsympify(self.userEquRhs[k]))
            self.equTableText = []
            self.equTableIndx = 0
            self.record = self.userEquRecord[k]
        
        elif mode == 'new':
            self.equTableLhs = []
            self.equTableRhs = []
            self.equTableText = []
            self.equTableIndx = 0
            self.userEquIx = None
            self.record = u'-'
            self.equTableLhs.append(new_equ_lhs)
            self.equTableRhs.append(new_equ_rhs)
            symLhsTmp = otsympify(new_equ_lhs)
            symRhsTmp = otsympify(new_equ_rhs) 
            if not len(symLhsTmp.free_symbols) == 0:
                self.symvar = str(symLhsTmp.free_symbols.pop())
            elif not len(symRhsTmp.free_symbols) == 0:
                self.symvar = str(symRhsTmp.free_symbols.pop())
            else:
                self.symvar = 'x'
            self.solution = solve(symLhsTmp-symRhsTmp)
        
        elif mode == 'file_import':
            
            self.equTableLhs = new_equ_lhs
            self.equTableRhs = new_equ_rhs
            self.equTableText = new_equ_text
            self.equTableIndx = len(new_equ_lhs)-1
            self.userEquIx = None
            self.record = u'-'
            symLhsTmp = otsympify(new_equ_lhs[0])
            symRhsTmp = otsympify(new_equ_rhs[0]) 
            if not len(symLhsTmp.free_symbols) == 0:
                self.symvar = str(symLhsTmp.free_symbols.pop())
            elif not len(symRhsTmp.free_symbols) == 0:
                self.symvar = str(symRhsTmp.free_symbols.pop())
            else:
                self.symvar = 'x'
            self.solution = solve(symLhsTmp-symRhsTmp)
            
            
    def addUserEqu(self, equ_lhs_str, equ_rhs_str):
        self.userEquLhs.append(equ_lhs_str)
        self.userEquRhs.append(equ_rhs_str)
        self.userEquRecord.append(u'-')
        
    def replaceUserEqu(self, equ_lhs_str, equ_rhs_str, k):
        self.userEquLhs[k] = equ_lhs_str
        self.userEquRhs[k] = equ_rhs_str
        self.userEquRecord[k] = u'-'
        
    def removeUserEqu(self,k):
        self.userEquLhs.pop(k)
        self.userEquRhs.pop(k)
        self.userEquRecord.pop(k)
        
    def getUserEqu(self,k):
        return self.userEquLhs[k], self.userEquRhs[k]
    
    def getUserEqus(self):
        return self.userEquLhs, self.userEquRhs
        

def create_equ(mode):
    """

    Vasemman ja oikean puolen lausekkeet muodostetaan erillisina stringeina
    Allaolevassa toteutuksessa lausekkeet ovat listassa ja palautetaan sielta erikseen oikealle ja vasemmalle puolelle
    """
    if mode == 'adv':
        advsw = random.randrange(0,2,1)
        rnd1 = random.randrange(-7,7,1)
        rnd2 = rnd1*random.randrange(-3,3,1)
        rnd3 = random.randrange(-5,5,1)
        x = symbols('x')
        rndex = Mul(rnd1,x+rnd3, evaluate=False)
        termDbL = ['x+3*(x-3*(x+2))','2*x-4+4*(x-5)','3*x+2*(x+3)', '3*(x-7)+5',str(rndex)]
        termDbR = ['3*(x+2)','x-7', '2-5*(x+3)','2*x-10',str(rnd2)]
        termDbadvL = ["3*(x+4)", "3*(x+3)", "3*(2*x+5)+5*(2*x+5)", "3*(x+4)+3*(x+4)", "2*(y-3)+5", "18", "3*(z-2)+4*(z-2)", "3*(z-2)+15"]
        termDbadvR = ["9", "2*(x+3)+4", "6", "6", "4*(y-3)", "6*(3*x-1)", "6*(z-2)", "2*(z-2)-12"]
        
        if advsw == 0:
            rangeL, rangeR = len(termDbL), len(termDbR)
            expL = termDbL[random.randrange(0,rangeL,1)]
            expR = termDbR[random.randrange(0,rangeR,1)]
        else:
            rangeLR = len(termDbadvL)
            ix = random.randrange(0,rangeLR,1)
            expL = termDbadvL[ix]
            expR = termDbadvR[ix]          
            
    elif mode == 'simple':
        termDbL = ['x-2','2*x+1','x+4', '2*x+2-x','x+2','4*x', '5*x+3', '20*x-10*x+1']
        termDbR = [str(random.randrange(-7,7,1)),'-x-5','3*x+6', '5*x+2+4-2*x']
        rangeL, rangeR = len(termDbL), len(termDbR)
        expL = termDbL[random.randrange(0,rangeL,1)]
        expR = termDbR[random.randrange(0,rangeR,1)]    
        
    return expL, expR
 
 
    
    