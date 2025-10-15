from sympy import Add, Mul, Pow, Symbol, symbols, Rational, Integer, ratsimp, simplify
from otlatex import latex
from otsympify import otsympify, SympifyError
from itertools import combinations
x = symbols('x')

def tidymul(expr):
    expr_args = list(expr.args)
    for term in expr_args:
        if term.is_Mul:
            new_term_ix = expr_args.index(term)
            new_term_list = list(term.args)
            for j in range(1,len(new_term_list)):
                if isinstance(new_term_list[j], (Integer, int)):
                    new_term_list[0]=Mul(new_term_list[j],new_term_list[0],evaluate=True)
                    new_term_list.pop(j)
                    expr_args[new_term_ix]=Mul(*new_term_list,evaluate=False)
                if j>=len(new_term_list):
                    break
                
    return expr.func(*expr_args, evaluate=False)

def tidyexpr(expr_str):
    expr_str = expr_str.replace(" - 1*"," - ")
    expr_str = expr_str.replace("1*(","(")

def cleanzeros(inp_expr_str, evaluate=False):
    inp_expr  = otsympify(inp_expr_str, evaluate=evaluate)   
    if isinstance(inp_expr, Add):
        args_old = list(inp_expr.args)
        if 0 in args_old:
            zero_ix = args_old.index(0)
            args_new = args_old
            args_new.remove(0)
            if len(args_new)==1:
                return str(args_new[0])
            else:
                outp_expr = Add(*args_new, evaluate=evaluate)
                return str(outp_expr)
        else:
            return inp_expr_str
    else:
        return inp_expr_str

def cleanzeros_sym(inp_expr, evaluate=False):
    if isinstance(inp_expr, Add):
        args_old = list(inp_expr.args)
        if 0 in args_old:
            zero_ix = args_old.index(0)
            args_new = args_old
            args_new.remove(0)
            if len(args_new)==1:
                return args_new[0]
            else:
                outp_expr = Add(*args_new, evaluate=evaluate)
                return outp_expr
        else:
            return inp_expr
    else:
        return inp_expr

def addlr(inp_expr_str, orig_expr_l_str, orig_expr_r_str, evaluate=False):
    errorFlag = 0
    inp_expr = otsympify(inp_expr_str, evaluate=evaluate)
    orig_expr_l = otsympify(orig_expr_l_str, evaluate=evaluate)
    orig_expr_r = otsympify(orig_expr_r_str, evaluate=evaluate)
    outp_expr_l = Add(orig_expr_l, inp_expr, evaluate=evaluate)
    outp_expr_r = Add(orig_expr_r, inp_expr, evaluate=evaluate)
    return str(outp_expr_l), str(outp_expr_r), errorFlag

def addlr_eval(inp_expr_str, orig_expr_l_str, orig_expr_r_str, evaluate=False):
    errorFlag = 0
    inp_expr = otsympify(inp_expr_str, evaluate=evaluate)
    orig_expr_l = otsympify(orig_expr_l_str, evaluate=evaluate)
    orig_expr_r = otsympify(orig_expr_r_str, evaluate=evaluate)
    outp_expr_l = Add(orig_expr_l, inp_expr)
    outp_expr_r = Add(orig_expr_r, inp_expr)
    return str(outp_expr_l), str(outp_expr_r), errorFlag
    
def substrlr(inp_expr_str, orig_expr_l_str, orig_expr_r_str, evaluate=False):
    errorFlag = 0
    inp_expr = otsympify(inp_expr_str, evaluate=evaluate)
    orig_expr_l = otsympify(orig_expr_l_str, evaluate=evaluate)
    orig_expr_r = otsympify(orig_expr_r_str, evaluate=evaluate)
    if inp_expr.func == Add:
        neg_inp_expr = Mul(-1, inp_expr, evaluate=True)
    else:
        neg_inp_expr = Mul(-1, inp_expr, evaluate=True)
        
    outp_expr_l = Add(orig_expr_l, neg_inp_expr, evaluate=evaluate)
    outp_expr_r = Add(orig_expr_r, neg_inp_expr, evaluate=evaluate)
    return str(outp_expr_l), str(outp_expr_r), errorFlag

def multiplr_expr(inp_expr_str, orig_expr_l_str, orig_expr_r_str, evaluate=False):
    errorFlag = 0
    inp_expr = otsympify(inp_expr_str, evaluate=evaluate)
    if not inp_expr == 0 and isinstance(inp_expr, (Integer, int, Rational)):     
        orig_expr_l = otsympify(orig_expr_l_str, evaluate=evaluate)
        orig_expr_r = otsympify(orig_expr_r_str, evaluate=evaluate)
        if isinstance(orig_expr_l,Add):
            outp_expr_l = Mul(orig_expr_l, inp_expr, evaluate=False)
        else:
            outp_expr_l = Mul(orig_expr_l, inp_expr, evaluate=True)
            
        if isinstance(orig_expr_r,Add):
            outp_expr_r = Mul(orig_expr_r, inp_expr, evaluate=False)
        else:
            outp_expr_r = Mul(orig_expr_r, inp_expr, evaluate=True)   

        return str(outp_expr_l), str(outp_expr_r), errorFlag
    else:
        errorFlag = 1
        return orig_expr_l_str, orig_expr_r_str, errorFlag

def multiplr(inp_expr_str, orig_expr_l_str, orig_expr_r_str, evaluate=False):
    errorFlag = 0
    inp_expr = simplify(otsympify(inp_expr_str, evaluate=True))
    orig_expr_l = otsympify(orig_expr_l_str, evaluate=evaluate)
    orig_expr_r = otsympify(orig_expr_r_str, evaluate=evaluate)
    if not len(orig_expr_l.free_symbols) == 0:
        symvar = str(orig_expr_l.free_symbols.pop())
    elif not len(orig_expr_r.free_symbols) == 0:
        symvar = str(orig_expr_r.free_symbols.pop())
    else:
        symvar = 'x'
        
    if not inp_expr == 0 and isinstance(inp_expr, (Integer, int, Rational)):
        if orig_expr_l.func == Add:
            new_args = []
            for term in orig_expr_l.args:
                new_args = multiply_by_terms(new_args, inp_expr, term, symvar)
            
            outp_expr_l = Add(*new_args, evaluate=False)
        else:
            new_args = [] 
            new_args = multiply_by_terms(new_args, inp_expr, orig_expr_l, symvar)
            outp_expr_l = new_args[0]
        
        if orig_expr_r.func == Add:
            new_args = []
            for term in orig_expr_r.args:
                new_args = multiply_by_terms(new_args, inp_expr, term, symvar)
            
            outp_expr_r = Add(*new_args, evaluate=False)
        else:
            new_args = [] 
            new_args = multiply_by_terms(new_args, inp_expr, orig_expr_r, symvar)
            outp_expr_r = new_args[0]            

        return str(outp_expr_l), str(outp_expr_r), errorFlag
    else:
        errorFlag = 1
        return orig_expr_l_str, orig_expr_r_str, errorFlag

def multiply_by_terms(new_args, inp_expr, term, symvar='x'):
    
    if len(term.free_symbols) == 1:
        symvar = str(term.free_symbols.pop())
    
    if isinstance(term, Mul) and not term.as_coefficient(Symbol(symvar)) == None:
        new_term = simplify(Mul(inp_expr, term, evaluate=True))
        new_args.append(new_term)
        
    elif isinstance(term, Mul):
        mul_args = []
        new_multipl = inp_expr    
        for multerm in term.args:
            if isinstance(multerm, (Integer, int, Rational, Pow)):
                if isinstance(multerm, Pow):
                    if isinstance(multerm.args[0], (Integer, int)) and isinstance(multerm.args[1], (Integer, int)):
                        new_multipl = simplify(Mul(new_multipl, multerm, evaluate=True))
                    else:
                        mul_args.append(multerm)
                else:
                    new_multipl = simplify(Mul(new_multipl, multerm, evaluate=True))
            else:
                mul_args.append(multerm)
        if Mul(*mul_args, evaluate=False) == 1:
            new_args.append(Mul(new_multipl, Mul(*mul_args, evaluate=False), evaluate=True))
        else:
            new_args.append(Mul(new_multipl, Mul(*mul_args, evaluate=False), evaluate=False))
    else:
        new_args.append(Mul(inp_expr, term, evaluate=True))
            
    return new_args

def dividelr(inp_expr_str, orig_expr_l_str, orig_expr_r_str, evaluate=False):
    errorFlag = 0
    inp_expr = simplify(otsympify(inp_expr_str, evaluate=True))
    if not inp_expr == 0 and isinstance(inp_expr, (Integer, int, Rational)):
        if isinstance(inp_expr, (Integer, int)):
            multerm = Rational(1, inp_expr)
        else:
            multerm = simplify(Rational(1, inp_expr))
        
        str_outp_expr_l, str_outp_expr_r, errorFlag = multiplr(str(multerm), orig_expr_l_str, orig_expr_r_str)

    else:    
        str_outp_expr_l = orig_expr_l_str
        str_outp_expr_r = orig_expr_r_str
        errorFlag = 1
    
    return str_outp_expr_l, str_outp_expr_r, errorFlag


def open_braces(orig_expr_str, color):
    errorFlag = 0
    orig_expr = otsympify(orig_expr_str, evaluate=False)
    
    # attach colors for nodes with braces
    latex(orig_expr)
    
    expHTree = handleTree(orig_expr)
    if expHTree.color_dict == {}:
        errorFlag = 1
        mod_expr = orig_expr 
    else:
        mod_expr, errorFlag = expHTree.remove_braces(color)
        

    return str(mod_expr), errorFlag

def collect_comm_fact(orig_expr_str, color, str_factor):    
    orig_expr = otsympify(orig_expr_str, evaluate=False)

    # attach colors for nodes with braces
    latex(orig_expr)
    expHTree = handleTree(orig_expr)
    mod_expr, errorFlag = expHTree.inc_common_factor(color, str_factor)
    
    return str(mod_expr), errorFlag

def collect_terms(orig_expr_str, color, term_type):
    orig_expr = otsympify(orig_expr_str, evaluate=False)
    
    # attach colors for nodes with braces
    latex(orig_expr)
    
    expHTree = handleTree(orig_expr)
    mod_expr, errorFlag = expHTree.merge_terms(color, term_type)
    
    return str(mod_expr), errorFlag
    
def get_colors_num(a, var='x'):
    latex(a, mode='plain')
    expr_Tree = handleTree(a, var)
    num_colors = len(expr_Tree.color_dict)
    return num_colors
        
    
    
# class for handling expression tree    
class handleTree(object):
    
    def __init__(self, a, symvar='x'):
        if len(a.free_symbols) == 1:
            symvar = str(a.free_symbols.pop())
        clear_path_color(a)
        latex(a)
        self.expr = a
        self.color_dict = {'black': [0]}
        self.find_path_color(a, [], -1)
        latex(a)
        self.symvar = symvar
     #   
    def merge_terms(self, color, term_id):
        errorFlag = 0
        if color == 'black' and self.expr.func == Add:
            args_old = list(self.expr.args)
            args_new = []
            new_term = 0
            
            for term in args_old:
                if term.is_number:
                    new_term = Add(new_term, simplify(term))
                elif isinstance(term, (Symbol, Mul)) and term_id == 'xterm' and not term.as_coefficient(Symbol(self.symvar)) == None:
                    new_term = Add(new_term, term)    
                else:
                    args_new.append(term)

            if not new_term == 0:        
                args_new.append(simplify(new_term))
            expr = Add(*args_new, evaluate=False)
            
        elif not color == 'black':
            br_path = list(self.color_dict[color])
            arg_path = list(br_path)
            arg_path.reverse()
            arg_to_check, arg_chain, fun_chain = self.get_argfun_chain(br_path, self.expr, [], [])
            
            if arg_to_check.func == Add:
                fun_chain.reverse()
                arg_chain.reverse()
                
                # arguments to be checked    
                args_old = list(arg_to_check.args)
                args_new = []
                new_term = 0
  
                for term in args_old:
                    if term.is_number:
                        new_term = Add(new_term, simplify(term))
                           
                    elif isinstance(term, (Symbol, Mul)) and term_id == 'xterm' and not term.as_coefficient(Symbol(self.symvar)) == None:
                        new_term = Add(new_term, term)    
                    else:
                        args_new.append(term)
                if not new_term == 0:       
                    args_new.append(simplify(new_term))
                expr = Add(*args_new, evaluate=False)
                
                for i in range(len(fun_chain)):
                    arg_list = list(arg_chain[i])
                    arg_list.insert(arg_path[i], expr)
                    
                    if fun_chain[i] == Add:
                        expr = Add(*arg_list, evaluate=False)
                    elif fun_chain[i] == Mul:
                        if 0 in arg_list:
                            expr = Mul(*arg_list, evaluate=True)
                        else:
                            expr = Mul(*arg_list, evaluate=False)    
                    else:
                        errorFlag = 1
                        expr = self.expr
            else:
                errorFlag = 1
                expr = self.expr
        else:
            errorFlag = 1
            expr = self.expr
            
        return expr, errorFlag
            
    
    #find common factor
    def inc_common_factor(self, color, str_factor):
        from sympy import sympify
        errorFlag = 0
        factor = sympify(str_factor, evaluate=False)
        if factor == 1 or factor == -1:
            expr = self.expr
            return expr, errorFlag
        elif factor == 0:
            expr = self.expr
            errorFlag = 1
            return expr, errorFlag
        # if the factorization will be done at top level
        if color == 'black' and self.expr.func == Add:
            args_old = list(self.expr.args)
            args_new = []
            # check if there is a combination of terms which can be factored
            args_old, args_new = self.common_factor_combs(args_old, [], factor)
            
            if not args_new == []:                 
                args_old.extend(args_new)
                args_new = []        
                
            # check all arguments and if there is a multiplication check if it could be factorized using common factor
            expr = self.common_factor_mul(args_old, args_new, factor)
           
        # if the factorization will be some other level            
        elif not color == 'black': 
            br_path = list(self.color_dict[color])
            arg_path = list(br_path)
            arg_path.reverse()
            arg_to_fact, arg_chain, fun_chain = self.get_argfun_chain(br_path, self.expr, [], [])
        
            # common factor can be formed only from addition
            if arg_to_fact.func == Add:
                fun_chain.reverse()
                arg_chain.reverse()
                
                # arguments to be checked    
                args_old = list(arg_to_fact.args)
                args_new = []
            
                # check if there is a combination of terms which can be factored
                args_old, args_new = self.common_factor_combs(args_old, [], factor)
                
                if not args_new == []:                 
                    args_old.extend(args_new)
                    args_new = []
                    
                # check all arguments and if there is a multiplication check if it could be factorized using common factor
                expr = self.common_factor_mul(args_old, args_new, factor)
                
                for i in range(len(fun_chain)):
                    arg_list = list(arg_chain[i])
                    arg_list.insert(arg_path[i], expr)
                    
                    if fun_chain[i] == Add:
                        expr = Add(*arg_list, evaluate=False)
            
                    elif fun_chain[i] == Mul:
                        expr = Mul(*arg_list, evaluate=False)
                        
                    else:
                        errorFlag = 1
                        expr = self.expr
            else:
                errorFlag = 1
                expr = self.expr
                
        else:
            errorFlag = 1
            expr = self.expr
            
        return expr, errorFlag
            
    #remove braces from multiplications    
    def remove_braces(self, color):
        errorFlag = 0
        if color == 'black':
            return self.expr, 1
        else:

            br_path = list(self.color_dict[color])
            arg_path = list(br_path)
            arg_path.reverse()
            arg_to_open, arg_chain, fun_chain = self.get_argfun_chain(br_path, self.expr, [], [])
            fun_chain.reverse()
            arg_chain.reverse()
            expr = arg_to_open
        
            for i in range(len(fun_chain)):
                arg_list = list(arg_chain[i])
                arg_list.insert(arg_path[i], expr)
                # if i==0 remove braces from multiplication
                if i == 0 and fun_chain[i] == Mul:
                    if arg_path[i] == 0:  # if term with braces is the first term in list
                        arg_w_br = arg_list[arg_path[0]]
                        multipl_list = list(arg_list)
                        multipl_list.pop(arg_path[i])
                        multipl = Mul(*multipl_list)
                        # multipl =  arg_list[arg_path[1]]
                        tmp_expr = 0
                        for term in arg_w_br.args:
                            tmp_expr = Add(tmp_expr, Mul(multipl, term, evaluate=True), evaluate=False)
                            tmp_expr = cleanzeros_sym(tmp_expr,False)
                            # tmp_expr = Mul(arg_list[0],arg_list[1],evaluate=True)
                        if len(arg_list) == 2:  # if there are only two terms to multiply the result is lifted directly to next level in tree
                            expr = tmp_expr
                        else:  # else do the multiplication of the term with braces and the other term
                            upd_arg_list = list(arg_list)
                        
                            # remove the terms multiplied from the list
                            upd_arg_list.pop(0)
                            upd_arg_list.pop(1)
                        
                            # replace the terms removed with the new one
                            upd_arg_list.insert(0, tmp_expr)
                        
                            # do the computations remaining
                            expr = Mul(*upd_arg_list, evaluate=False)
                        br_i = i
                    else:  # if the term with braces is not the first one
                        arg_w_br = arg_list[arg_path[i]]
                        multipl_list = list(arg_list)
                        multipl_list.pop(arg_path[i])
                        multipl = Mul(*multipl_list)
                        # multipl =  arg_list[arg_path[i]-1]
                        tmp_expr = 0
                        for term in arg_w_br.args:
                            if term.is_Mul:
                                new_term_list = list(term.args)
                                new_term_list[0]=Mul(multipl,new_term_list[0],evaluate=True)
                                for j in range(1, len(new_term_list)):
                                    if isinstance(new_term_list[j], (Integer, int)):
                                        new_term_list[0]=Mul(new_term_list[j],new_term_list[0],evaluate=True)
                                        new_term_list.pop(j)
                                    if j>=len(new_term_list):
                                        break       
                                
                                tmp_expr = Add(tmp_expr, Mul(*new_term_list, evaluate=False), evaluate=False)
                                tmp_expr = cleanzeros_sym(tmp_expr,False)
                            else:
                                tmp_expr = Add(tmp_expr, Mul(multipl, term, evaluate=True), evaluate=False)
                                tmp_expr = cleanzeros_sym(tmp_expr,False)
                            # tmp_expr = Mul(arg_list[arg_path[i]-1],arg_list[arg_path[i]],evaluate = True)
#                         if len(arg_list) == 2:
#                             expr = tmp_expr
#                         else:
#                             upd_arg_list=list(arg_list)
#                             upd_arg_list.pop(arg_path[i])
#                             upd_arg_list.pop(arg_path[i]-1)
#                             upd_arg_list.insert(arg_path[i]-1,tmp_expr)
#                             expr = Mul(*upd_arg_list,evaluate = False)
                        expr = tmp_expr
                        br_i = i
                elif fun_chain[i] == Add:
                    expr = Add(*arg_list, evaluate=False)
            
                elif fun_chain[i] == Mul:
                    if i-1 == br_i:
                        expr = Mul(*arg_list, evaluate=True)
                    else:
                        expr = Mul(*arg_list, evaluate=False)
                
                else:
                    expr = self.expr 
                    errorFlag = 1
                   
            return expr, errorFlag
    
    def get_argfun_chain(self, path, expr, arglist, funlist):
        for i in path:
            arglist_tmp = list(expr.args)
            arglist_tmp.pop(i)
            arglist.append(arglist_tmp)
            funlist.append(expr.func)
            arg = expr.args[i]
            fin_arg = arg
            path.pop(0)
            if not path == []:  
                fin_arg, _, _ = self.get_argfun_chain(path, arg, arglist, funlist)
        return fin_arg, arglist, funlist
        
    def find_path_color(self, expr, path, level):
        level += 1
        if level >= len(path):
            path.extend([0])
        for i in range(len(expr.args)):
            path[level] = i
            arg = expr.args[i]
            if hasattr(arg, 'color') and not arg.color == []:
                self.color_dict[arg.color[0]] = list(path)
                if len(arg.color) > 1:
                    arg.color.pop(0)
                  
            self.find_path_color(arg, path, level)
            
        level -= 1
        path.pop(-1)
    
    def common_factor_combs(self, expr_args, new_expr_args, factor):
        comb_terms = list(combinations(expr_args, 2))
        for termpair in comb_terms:
            divid_si1 = ratsimp(Mul(termpair[0], Pow(factor, -1), evaluate=True))
            divid_si2 = ratsimp(Mul(termpair[1], Pow(factor, -1), evaluate=True))
            if not (isinstance(divid_si1, (Integer, int, Rational)) or (isinstance(divid_si2, (Integer, int, Rational)))):
                addterm = Add(termpair[0], termpair[1], evaluate=False)
                divid = ratsimp(Mul(addterm, Pow(factor, -1), evaluate=True))
                if isinstance(divid, (Integer, int, Rational)):
                    new_expr_args.append(Mul(divid, factor, evaluate=False))
                    expr_args.remove(termpair[0])
                    expr_args.remove(termpair[1])
                    expr_args, new_expr_args = self.common_factor_combs(expr_args, new_expr_args, factor)
                    break
        return expr_args, new_expr_args
    
    def common_factor_mul(self, args_old, args_new, factor):
        fact_term_list = []
        for term in args_old:
            if term.func == Mul:
                mul_terms = term.as_ordered_factors()
                new_mul_terms = list(mul_terms)  
                for i in range(len(mul_terms)):
                    divid = ratsimp(Mul(mul_terms[i], Pow(factor, -1), evaluate=True))
                    if isinstance(divid, (int, Integer, Rational)):
                        new_mul_terms[i] = divid
                        term = Mul(*new_mul_terms, evaluate=True)
                        fact_term_list.append(term) 
                        break
                if mul_terms == new_mul_terms:
                    args_new.append(term)
            # elif isinstance(term, (int, Integer, Rational)):
            #     divid = ratsimp(Mul(term, Pow(factor, -1), evaluate=True))
            #     if isinstance(divid, (int, Integer)):
            #         new_mul_terms[i] = divid
            #         term = Mul(*new_mul_terms, evaluate=True)
            #         fact_term_list.append(term)
            #         break             
            elif term.as_coefficient(factor) == None:
                args_new.append(term)
            else:
                fact_term_list.append(term.as_coefficient(factor))
        if not fact_term_list == []:        
            new_term = simplify(Add(*fact_term_list, evaluate=True))
            if new_term == 0 or new_term == 1 or new_term == -1: #terms eliminate each other or trivial multiplication
                new_term = Mul(new_term, factor, evaluate=True)
            else:
                new_term = Mul(new_term, factor, evaluate=False) 
            args_new.append(new_term)
                    
        expr = Add(*args_new, evaluate=False)
        return expr
    

def clear_path_color(expr):

    for i in range(len(expr.args)):
        arg = expr.args[i]
        if hasattr(arg, 'color'):
            arg.color = []
                              
        clear_path_color(arg)
            
            
        
            
        
    