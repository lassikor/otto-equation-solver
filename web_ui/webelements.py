# -*- coding: utf8 -*-
from otsympify import otsympify, SympifyError
from otlatex import colorlist_fi as colors
from otlatex import latex

#dropdown menu for colors
def get_color_dropmenu(n,side):
    
    colors_used = colors[0:n]
    
    dropmenu_colors = r'<select id="color_drop_'+side+r'" name="color_drop_'+side+r'">'
    
    for s in colors_used:
        dropmenu_colors += r'<option value="'+s[0]+r'" style="color:'+s[0]+r';">'
        dropmenu_colors += s[1]+r':</option>'
    
    dropmenu_colors += r'</select>'
    
    return dropmenu_colors

#strings for user equation table with icons  
def get_userequ_table(equ_lhs_sym,equ_rhs_sym):
    nmb_equs = len(equ_lhs_sym)
    
    equ_table = r'<table id="user_equs">'
    ix = 0
    for row_lhs, row_rhs in zip(equ_lhs_sym, equ_rhs_sym):
        #tidy equations by removing -1 multiplications
        tex_lhs_str = latex(row_lhs)
        tex_rhs_str = latex(row_rhs)
        tex_lhs_str = tex_lhs_str.replace(' - 1 \\cdot',' - ')
        tex_rhs_str = tex_rhs_str.replace(' - 1 \\cdot',' - ')

        ix_str = str(ix)
        
        #create html for user equations
        equ_table += r'<tr><td align="right">\('+tex_lhs_str+r'\)</td><td>\(=\)</td><td align="left">\('+tex_rhs_str+r'\)</td>'+'\n'
        equ_table += r'<td align="right"><button id="postBut" value="solve_equ'+ix_str+r'" name="postBut" class="icon_but"><i class="material-icons" title="Ratkaise">play_circle_outline</i></button>'+'\n'
        equ_table += r'<button id="postBut" value="edit_equ'+ix_str+r'" name="postBut" class="icon_but"><i class="material-icons" title="Muokkaa">build</i></button>'+'\n'
        equ_table += r'<button id="postBut" value="del_equ'+ix_str+r'" name="postBut" class="icon_but"><i class="material-icons" title="Poista">delete</i></button></td></tr>'
        ix +=1
    equ_table += r'</table>'
    
    return equ_table

#strings for button labels
def get_button_strings(svar='x'):
    but_strings = {
                    'but_xj_str' : r'\('+svar+'+'+svar+r'\rightarrow 2'+svar+r'\)',
                    'but_nj_str' : r'\(1+1 \rightarrow 2\)',
                    'but_rp_str' : r'\((' + svar + r')\rightarrow ' + svar + r'\)'
                    }
    return but_strings
    