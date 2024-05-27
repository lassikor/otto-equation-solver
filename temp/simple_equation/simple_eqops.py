
def addlr(inp_expr,orig_expr_l,orig_expr_r):
    errorFlag = 0
    outp_expr_l = orig_expr_l+inp_expr
    outp_expr_r = orig_expr_r+inp_expr
    return outp_expr_l, outp_expr_r, errorFlag
    
def substrlr(inp_expr,orig_expr_l,orig_expr_r):
    errorFlag = 0
    outp_expr_l = orig_expr_l-inp_expr
    outp_expr_r = orig_expr_r-inp_expr
    return outp_expr_l, outp_expr_r, errorFlag

def multiplr(inp_expr,orig_expr_l,orig_expr_r):
    errorFlag = 0
    outp_expr_l = orig_expr_l*inp_expr
    outp_expr_r = orig_expr_r*inp_expr
    return outp_expr_l, outp_expr_r, errorFlag

def dividelr(inp_expr,orig_expr_l,orig_expr_r):
    errorFlag = 0
    try:
        outp_expr_l = orig_expr_l/inp_expr
        outp_expr_r = orig_expr_r/inp_expr
        
    except ZeroDivisionError:
        outp_expr_l = orig_expr_l
        outp_expr_r = orig_expr_r
        errorFlag = 1
          
    return outp_expr_l, outp_expr_r, errorFlag
    