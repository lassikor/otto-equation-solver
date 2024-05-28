# -*- coding: utf8 -*-
from otsympify import otsympify, SympifyError
from otlatex import colorlist_fi as colors
from otlatex import latex

def get_color_dropmenu(n,side):
    
    colors_used = colors[0:n]
    
    dropmenu_colors = r'<select id="color_drop_'+side+r'" name="color_drop_'+side+r'">'
    
    for s in colors_used:
        dropmenu_colors += r'<option value="'+s[0]+r'" style="color:'+s[0]+r';">'
        dropmenu_colors += s[1]+r':</option>'
    
    dropmenu_colors += r'</select>'
    
    return dropmenu_colors
    
def get_userequ_table(equ_lhs_sym,equ_rhs_sym):
    nmb_equs = len(equ_lhs_sym)
    
    equ_table = r'<table id="user_equs">'
    ix = 0
    for row_lhs, row_rhs in zip(equ_lhs_sym, equ_rhs_sym):
        ix_str = str(ix)
        equ_table += r'<tr><td align="right">\('+latex(row_lhs)+r'\)</td><td>\(=\)</td><td align="left">\('+latex(row_rhs)+r'\)</td>'+'\n'
        equ_table += r'<td align="right"><button id="postBut" value="solve_equ'+ix_str+r'" name="postBut" class="icon_but"><i class="material-icons" title="Ratkaise">play_circle_outline</i></button>'+'\n'
        equ_table += r'<button id="postBut" value="edit_equ'+ix_str+r'" name="postBut" class="icon_but"><i class="material-icons" title="Muokkaa">build</i></button>'+'\n'
        equ_table += r'<button id="postBut" value="del_equ'+ix_str+r'" name="postBut" class="icon_but"><i class="material-icons" title="Poista">delete</i></button></td></tr>'
        ix +=1
    equ_table += r'</table>'
    
    return equ_table
    