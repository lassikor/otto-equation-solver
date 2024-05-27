# -*- coding: latin-1 -*-
import web
from web import form
import webtex
import jyrequhandle
from jyrsympify import jyrsympify, SympifyError

web.config.debug = False

render = web.template.render('templates/')
urls = ('/','index')
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'),
                              initializer = {'equT':jyrequhandle.EquTable()})

"""
Elemnts for creating forms and form tables
"""

buttNew = form.Button('postBut', form.notnull, value = 'donew', html=u'Uusi tehtävä')

exprForm = form.Form(form.Textbox('inp_expr',form.notnull,description="Lauseke: "),
                     form.Dropdown('op_drop',[('lisaa',u'Lisää'),
                                              ('vahenna',u'Vähennä'),
                                              ('kerro','Kerro'),
                                              ('jaa','Jaa')],
                                   description = 'Toiminto:'),
                     form.Button('postBut', form.notnull, value = 'modequ', html = u'Tee toiminto'))
exprModForm = form.Form(form.Dropdown('op_drop',[('yhdista_luvut', u'Yhdistä luvut'),
                                              ('yhdista_xtermit', u'Yhdistä muuttujatermit'),
                                              ('poista_sulut', u'Poista sulut'),
                                              ('yhteinen_tekija', u'Ota yhteinen tekijä')],
                                       description = 'Toiminto:'),
                         form.Radio('side', [('vasen','Vasen'), ('oikea', 'Oikea')], form.notnull, description = 'Valitse puoli:'),
                         form.Textbox('common_fac', form.notnull, description = u'Yhteinen tekijä: '),
                         form.Button('postBut', form.notnull, value = 'modexp', html = u'Tee toiminto'))


class index:
    
    def GET(self):
        session.equT = jyrequhandle.EquTable()
        equlhs_str,equrhs_str = session.equT.getEquTable()
        equlhs, equrhs = jyrsympify(equlhs_str, evaluate = False), jyrsympify(equrhs_str, evaluate = False)
        
        expform = exprForm()
           
        return render.index(expform,buttNew,webtex.concEqutoAlign(equlhs, equrhs))
        #return render.index(webtex.equationLatex(2*x+5*x/(2+x)**2))
    
    def POST(self):
        equlhs_str, equrhs_str = session.equT.getEquTable()
        equlhs, equrhs = jyrsympify(equlhs_str, evaluate = False), jyrsympify(equrhs_str, evaluate = False)
        
        expform = exprForm()
        
        inp = web.input()
        if not inp.postBut == "donew":
            if not expform.validates():
                #return render.index(expform,webtex.concEqutoAlign(equlhs, equrhs))
                return render.index(expform,buttNew,inp)
        
            else:
                try:
                    sym_expr = jyrsympify(expform.d.inp_expr, evaluate = False)
                
                except SympifyError:
                    return render.index(expform,buttNew,u"Virheellinen syöte!")
                else:
                    op = expform.d.op_drop
                    expr = str(sym_expr)
                    session.equT.equTransf(op,expr)
                    equlhs_str, equrhs_str = session.equT.getEquTable()
                    equlhs, equrhs = jyrsympify(equlhs_str, evaluate = False), jyrsympify(equrhs_str, evaluate = False)
                    return render.index(expform,buttNew,webtex.concEqutoAlign(equlhs, equrhs))
        
        else:
            session.equT = jyrequhandle.EquTable()
            equlhs_str,equrhs_str = session.equT.getEquTable()
            equlhs, equrhs = jyrsympify(equlhs_str, evaluate = False), jyrsympify(equrhs_str, evaluate = False)
            expform = exprForm()       
            return render.index(expform,buttNew,webtex.concEqutoAlign(equlhs, equrhs))
    
if __name__=="__main__":
    
    app.run()