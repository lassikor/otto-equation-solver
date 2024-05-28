from otlatex import latex

def inlineLatex(orig_expr):
    tex_expr = r'\('
    tex_expr += latex(orig_expr,mode='plain')
    tex_expr += r'\)'  
    return(tex_expr)

def equationLatex(orig_expr):
    tex_expr = r'\['
    tex_expr += latex(orig_expr,mode='plain')
    tex_expr += r'\]'
    return(tex_expr)

def concEqutoAlign(lhs,rhs,descrtext='empty'):
    rows = len(lhs)
    
    if descrtext == 'empty':
    
        tex_expr = r'\[\require{color}\begin{align}\begin{split}'
        for i in range(rows):
            tex_expr+=latex(lhs[i],mode='plain')+r'&='+latex(rhs[i],mode='plain')+r'&\qquad\\'
    
        tex_expr += r'\end{split}\end{align}\]'
    else:
        descrtextpad = list(descrtext)
        descrtextpad.append(' ')
        tex_expr = r'\[\require{color}\begin{align}\begin{split}'
        for i in range(rows):
            tex_expr+=latex(lhs[i],mode='plain')+r'&='+latex(rhs[i],mode='plain')+r'&\qquad'+descrtextpad[i]+r'\\'
    
        tex_expr += r'\end{split}\end{align}\]'

    return tex_expr