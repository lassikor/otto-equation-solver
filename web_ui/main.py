# -*- coding: utf8 -*-

'''
Main file for the web UI otto-equation-solver application
This file is part of the otto-equation-solver project.
Copyright (C) 2020-2025 Lassi Korhonen
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

'''
import sys
import os
rootpath = "C:\\Users\\lassikor\\OneDrive - University of Oulu and Oamk\\projects\\otto-equation-solver\\"
sys.path.append(rootpath+'web_ui\\')
sys.path.append(rootpath+'web_ui\\static\\')
sys.path.append(rootpath+'web_ui\\templates\\')
sys.path.append(rootpath+'web_ui\\sessions\\')
sys.path.append(rootpath+'equtools\\')
import web
import json
import re as rgex
import webelements
import webtex
from otlatex import latex
import otequhandle
import otops
from otsympify import otsympify, SympifyError
from sympy import Poly, Integer, Rational, simplify, ratsimp

from lib2to3.pgen2.literals import simple_escapes

web.config.debug = False

render = web.template.render(rootpath+'web_ui\\templates\\')

#url mappings
urls = ('/','index',
        '/instr_fi', 'instr_fi',
        '/advview', 'advview',
        '/simpleview', 'simpleview',
        '/newadvquestion','newadvquestion',
        '/oldadvquestion','oldadvquestion',
        '/createadvquestion','createadvquestion',
        '/newsimplequestion','newsimplequestion',
        '/oldsimplequestion','oldsimplequestion',
        '/createsimplequestion','createsimplequestion',
        '/advquestionsolved','advquestionsolved',
        '/simplequestionsolved','simplequestionsolved',
        '/inverseview','inverseview',
        '/oldinversequestion','oldinversequestion')

app = web.application(urls, globals())
web.config.session_parameters['cookie_path'] = '\\'
#init new session. Sessions are needed for storing equations
session = web.session.Session(app, web.session.DiskStore(rootpath+'web_ui\\sessions'))
#session.kill()

#error messages
errs = {'own_equs_full': u'<script>window.alert("Vain kymmenen omaa yhtälöä sallittu!")</script>',
        'expr_error':u'<script>window.alert("Syöttämääsi lauseketta ei voitu muodostaa! Unohditko näppäillä kertomerkin?")</script>',
        'inp_expr_error': u'<script>window.alert("Syöttämäsi lauseke ei kelpaa. Vain lineaariset lausekkeet kelpaavat!")</script>',        
        'equ_error':u'<script>window.alert("Syöttämääsi yhtälöä ei voitu muodostaa!")</script>',
        'equ_error_load':u'<script>window.alert("Tuomasi tiedosto ei kelpaa!")</script>',
        'equ_error_create':u'<script>window.alert("Muodostamasi yhtälö ei kelpaa!")</script>',
        'session_expired': u'<script>window.alert("Istuntosi on aikakatkaistu ja tiedot kadonneet!")</script>',
        'muldiv_error': u'<script>window.alert("Kertominen tai jakaminen on luvallista vain nollasta poikkeavalla luvulla!")</script>',
        'zero_comm_fact': u'<script>window.alert("Nolla ei voi olla yhteinen tekijä!")</script>'}

#front page
class index:
    
    def GET(self):
        return render.index()

#instructions front page    
class ohjeet:
    
    def GET(self):
        return render.instr_fi()
    
#simple equation solving training page handling      
class simpleview:

    def GET(self):
        
        #generate new equation table if missing
        if not hasattr(session,'simplequT'):
            session.simplequT = otequhandle.EquTable('simple')
            session.sidebarStatus = 0    
        return simpleview_render()
    
    def POST(self):
        if not hasattr(session,'simplequT'):
            session.simplequT = otequhandle.EquTable('simple')
            session.sidebarStatus = 0
            return simpleview_render('session_expired')

        #catch inputs
        webinp = web.input()
        session.sidebarStatus = webinp.sidebarStatus

        #check what the user has tried to do
        if webinp.postBut == "modequ":
            try:
                sym_expr = otsympify(webinp.inp_expr_lr, evaluate=False)
                
            except SympifyError:
                return simpleview_render('expr_error')
            
            else:
                if webinp.op_drop_lr in ['mul', 'div'] and (not isinstance(sym_expr, (Integer, int, Rational)) or sym_expr == 0):
                    return simpleview_render('muldiv_error')
                op = webinp.op_drop_lr
                str_expr = str(sym_expr)
                session.simplequT.equTransf(op,str_expr)
                return simpleview_render()
            
        elif webinp.postBut == 'modequ_j':
            op = 'merge_terms'
            session.simplequT.exprMods(op, 'black', 'both', 'const')
            return simpleview_render()
        
        elif webinp.postBut == 'modequ_x':
            op = 'merge_terms'
            session.simplequT.exprMods(op, 'black', 'both', 'xterm')
            return simpleview_render()
        
        elif webinp.postBut == "upload_solution_file":
        
            f = web.input(upload_solution={})
            try:
                uplEquArray = json.load(f['upload_solution'].file)
                newEqusL = uplEquArray[0]
                newEqusR = uplEquArray[1]
                newEqusText = uplEquArray[2]
                sym_equ_lhs, sym_equ_rhs = otsympify(newEqusL),otsympify(newEqusR)
                last_sym_equ_lhs, last_sym_equ_rhs = sym_equ_lhs[-1], sym_equ_rhs[-1]
            except (SyntaxError,IOError, SympifyError, ValueError):
                return simpleview_render('equ_error_load')
            else:
                if not test_linpoly(last_sym_equ_lhs, 'simple') or not test_linpoly(last_sym_equ_rhs, 'simple')\
                or not test_linpoly(last_sym_equ_lhs-last_sym_equ_rhs, 'simple'):
                    return simpleview_render('equ_error_load')
                
                session.simplequT.initEquTable(0,'file_import', newEqusL, newEqusR, newEqusText)
                
                return simpleview_render()
            
        elif webinp.postBut == "download_solution":
            web.header('Content-Type','application/json')
            web.header('Content-disposition', 'attachment; filename=oma_ratkaisu.txt')
            sessid = str(session.session_id)
            with open(rootpath+'/web_ui/sessions/'+sessid+'_oma_ratkaisu.txt','w') as outfile:
                json.dump([session.simplequT.equTableLhs, session.simplequT.equTableRhs, session.simplequT.equTableText],outfile)
            return open(rootpath+'/web_ui/sessions/'+sessid+'_oma_ratkaisu.txt').read()        
            
#advanced equation solving training page handling
class advview:

    #load page
    def GET(self):
        if not hasattr(session,'equT'):
            session.equT = otequhandle.EquTable()
            session.sidebarStatus = 0
        return advview_render()

    #handle form
    def POST(self):
        if not hasattr(session,'equT'):
            session.equT = otequhandle.EquTable()
            session.sidebarStatus = 0
            return advview_render('session_expired')
               
        webinp = web.input()
        session.sidebarStatus = webinp.sidebarStatus
        mode = 'adv'

        #if equation's both sides are modified
        if webinp.postBut == "modequ":
            try:
                sym_expr = otsympify(webinp.inp_expr_lr, evaluate = False)
                
            except SympifyError:
                return advview_render('expr_error')
            else:
                if not test_linpoly(sym_expr, mode):
                    return advview_render('inp_expr_error')
                op = webinp.op_drop_lr
                str_expr = str(sym_expr)
                session.equT.equTransf(op,str_expr)
                return advview_render()
            
        #if solutiom is uploaded    
        elif webinp.postBut == "upload_solution_file":
        
            f = web.input(upload_solution={})
            try:
                uplEquArray = json.load(f['upload_solution'].file)
                newEqusL = uplEquArray[0]
                newEqusR = uplEquArray[1]
                newEqusText = uplEquArray[2]
                sym_equ_lhs, sym_equ_rhs = otsympify(newEqusL),otsympify(newEqusR)
                last_sym_equ_lhs, last_sym_equ_rhs = sym_equ_lhs[-1], sym_equ_rhs[-1]                
            except (SyntaxError,IOError, SympifyError,ValueError):
                return advview_render('equ_error_load')
            else:
                if not test_linpoly(last_sym_equ_lhs, mode) or not test_linpoly(last_sym_equ_rhs, mode)\
                or not test_linpoly(last_sym_equ_lhs-last_sym_equ_rhs, mode):
                    return advview_render('equ_error_load')
                else:           
                    session.equT.initEquTable(0,'file_import', newEqusL, newEqusR, newEqusText)
                    return advview_render()
                
        #if solution is downloaded    
        elif webinp.postBut == "download_solution":
            web.header('Content-Type','application/json')
            web.header('Content-disposition', 'attachment; filename=oma_ratkaisu.txt')
            sessid = str(session.session_id)
            with open(rootpath+'/web_ui/sessions/'+sessid+'_oma_ratkaisu.txt','w') as outfile:
                json.dump([session.equT.equTableLhs, session.equT.equTableRhs, session.equT.equTableText],outfile)
            return open(rootpath+'/web_ui/sessions/'+sessid+'_oma_ratkaisu.txt').read()

        #if only one side is modified
        elif webinp.postBut.find("right") > -1:
            side = 'right'
            return advops_handler(webinp, side)

        elif webinp.postBut.find("left") > -1:
            side = 'left'
            return advops_handler(webinp, side)
        else:
            return advview_render()

#equation creation page handling        
class inverseview:
    
    def GET(self):
        #init button strings
        but_str = webelements.get_button_strings()

        #check if the equation is not established
        if not hasattr(session,'invequT'):
            session.invequT = otequhandle.EquTable('inv')
            return render.inverseview([],[],[],[],but_str)
        elif session.invequT.equTableLhs == ['0'] and session.invequT.equTableRhs == ['0']:
            return render.inverseview([],[],[],[],but_str)
        else:
            return inverseview_render()
    
    def POST(self):
        if not hasattr(session,'invequT'):
            session.invequT = otequhandle.EquTable('inv')
            return inverseview_render('session_expired')
 
        webinp = web.input()
        mode = 'adv'
        
        #user starts creation
        if webinp.postBut == "start":
            try:
                sym_equ_lhs = otsympify(webinp.inp_equ_lhs, evaluate = False)
                sym_equ_rhs = otsympify(webinp.inp_equ_rhs, evaluate = False)
  
            except (SympifyError, IndexError):
                return render.inverseview([],[],[],errs['expr_error'])
            else:
                if not test_linpoly(sym_equ_lhs, 'adv') or not test_linpoly(sym_equ_rhs, 'adv')\
                or not test_linpoly(sym_equ_lhs-sym_equ_rhs, 'adv'):
                    return inverseview_render('equ_error_create')
                else:
                    session.invequT.initEquTable(0,'new',str(sym_equ_lhs),str(sym_equ_rhs))
                    return inverseview_render()
        
        elif webinp.postBut == "modequ":
            try:
                sym_expr = otsympify(webinp.inp_expr_lr, evaluate = False)
                
            except SympifyError:
                return inverseview_render('expr_error')
            else:
                if not test_linpoly(sym_expr, mode):
                    return inverseview_render('inp_expr_error')
                if webinp.op_drop_lr in ['mul_expr', 'div'] and (not isinstance(sym_expr, (Integer, int, Rational)) or sym_expr == 0):
                        return inverseview_render('muldiv_error')
                op = webinp.op_drop_lr
                str_expr = str(sym_expr)
                session.invequT.equTransf(op,str_expr)
                return inverseview_render()
            
        elif webinp.postBut.find("left") > -1:
            side = 'left'
            return advops_handler(webinp, side, 'inv')  
                                           
        elif webinp.postBut.find("right") > -1:
            side = 'right'
            return advops_handler(webinp, side, 'inv')
        
        elif webinp.postBut == "save_adv_equ":
            mode = 'adv'
            return save_invequ(mode)
            
        elif webinp.postBut == "save_simple_equ":
            mode = 'simple'
            return save_invequ(mode)

        #if tried to upload solution    
        elif webinp.postBut == "upload_equation_file":
        
            f = web.input(upload_equation={})
            try:
                uplEquArray = json.load(f['upload_equation'].file)
                newEquL = uplEquArray[0]
                newEquR = uplEquArray[1]
                if len(uplEquArray) == 3:
                    newEquText = uplEquArray[2]
                elif len(newEquL) == 1:
                    newEquText = []
                else:
                    raise IOError
                sym_equ_lhs, sym_equ_rhs = otsympify(newEquL),otsympify(newEquR)
                last_sym_equ_lhs, last_sym_equ_rhs = sym_equ_lhs[-1], sym_equ_rhs[-1]
            except (SyntaxError,IOError, SympifyError, ValueError):
                return inverseview_render('equ_error_load')
            else:
                if not test_linpoly(last_sym_equ_lhs, 'adv') or not test_linpoly(last_sym_equ_rhs, 'adv')\
                or not test_linpoly(last_sym_equ_lhs-last_sym_equ_rhs, 'adv'):
                    return inverseview_render('equ_error_load')
                else:
                    session.invequT.initEquTable(0,'file_import', newEquL, newEquR, newEquText)
                    return inverseview_render()

        #if tried to download solution  
        elif webinp.postBut == "download_equation":
            web.header('Content-Type','application/json')
            web.header('Content-disposition', 'attachment; filename=oma_yhtalo.txt')
            sessid = str(session.session_id)
            with open(rootpath+'/web_ui/sessions/'+sessid+'_oma_yhtalo.txt','w') as outfile:
                json.dump([[session.invequT.equTableLhs[-1]], [session.invequT.equTableRhs[-1]]],outfile)
            return open(rootpath+'/web_ui/sessions/'+sessid+'_oma_yhtalo.txt').read()

#classes for other pages handling      
class newadvquestion:
    
    def GET(self):
        if not hasattr(session,'equT'):
            session.equT = otequhandle.EquTable()        
        session.equT.clearEquTable('adv',1)
        
        raise web.seeother("/advview")
    
class oldadvquestion:
    
    def GET(self):
        if not hasattr(session,'equT'):
            session.equT = otequhandle.EquTable()                
        session.equT.clearEquTable('adv',0)
        
        raise web.seeother("/advview")
    
class createadvquestion:
    
    def GET(self):
        if not hasattr(session,'equT'):
            session.equT = otequhandle.EquTable()
        return createquestion_render('adv',2)
    
    def POST(self):
        if not hasattr(session,'equT'):
            session.equT = otequhandle.EquTable()
            return createquestion_render('adv',5)                   
        webinp = web.input()
        mode = 'adv'
        equtable = session.equT
        redirect = "/advview"
        redirect2 = "/createadvquestion"
        return createquestion_handler(webinp, mode, equtable, redirect, redirect2)
        
class createsimplequestion:
    
    def GET(self):
        if not hasattr(session,'simplequT'):
            session.simplequT = otequhandle.EquTable('simple')
        return createquestion_render('simple',err=2)
    
    def POST(self):
        if not hasattr(session,'simplequT'):
            session.simplequT = otequhandle.EquTable('simple')
            return createquestion_render('simple', err=5)             
                   
        webinp = web.input()
        mode = 'simple'
        equtable = session.simplequT
        redirect = "/simpleview"
        redirect2 = "/createsimplequestion"
        return createquestion_handler(webinp, mode, equtable, redirect, redirect2)
        
              
class advquestionsolved:
    
    def GET(self):
        
        return questionsolved_render('adv')
        
    def POST(self):
        #catch inputs
        webinp = web.input()
        
        #check what the user has tried to do
        return handleFileIO(webinp, 'adv')
        
                     
class newsimplequestion:
    
    def GET(self):
        session.simplequT.clearEquTable('simple',1)    
        raise web.seeother("/simpleview")
    
class oldsimplequestion:
    
    def GET(self):
        session.simplequT.clearEquTable('simple',0)    
        raise web.seeother("/simpleview")
    
class oldinversequestion:
    
    def GET(self):
        if hasattr(session, 'invequT'):
            session.invequT.clearEquTable()         
        raise web.seeother("/inverseview")
        
class simplequestionsolved:
    
    def GET(self):
        
        return questionsolved_render('simple')
    
    def POST(self):
        #catch inputs
        webinp = web.input()
        
        #check what the user has tried to do
        return handleFileIO(webinp, 'simple')
        
"""
Methods for supporting otequation handling and rendering
"""

def simpleview_render(err=0):
    #variable used
    svar = session.simplequT.symvar
    #button strings
    but_str = webelements.get_button_strings(svar)
    
    if not hasattr(session,'sidebarStatus'):
        session.sidebarStatus = 0  
        
    equlhs_str, equrhs_str, equtext = session.simplequT.getEquTable()
    if not equtext == []:
        if not rgex.search(r'Hie', equtext[-1]) == None:
            raise web.seeother("/simplequestionsolved")

    #symbolize strings        
    equlhs, equrhs = otsympify(equlhs_str, evaluate = False), otsympify(equrhs_str, evaluate = False)
    
    #render page
    if err == 0:
        return render.simpleview(webtex.concEqutoAlign(equlhs, equrhs, equtext),
                                 session.simplequT.equTableIndx, session.simplequT.record, session.simplequT.symvar, session.sidebarStatus, but_str)
    else:
        return render.simpleview(webtex.concEqutoAlign(equlhs, equrhs, equtext),
                              session.simplequT.equTableIndx, session.simplequT.record, session.simplequT.symvar,  session.sidebarStatus, but_str,
                              errs[err])       

#render advanced solver page       
def advview_render(err = 0):
    #variable used
    svar = session.equT.symvar
    
    #equation table for viewing
    equlhs_str, equrhs_str, equtext = session.equT.getEquTable()
    
    if not hasattr(session,'sidebarStatus'):
        session.sidebarStatus = 0

    #button strings
    but_str = webelements.get_button_strings(svar)  
    
    #if eqation is solved
    if not equtext == []:
        if not rgex.search(r'Hie', equtext[-1]) == None:
            raise web.seeother("/advquestionsolved")
    #else
    # symbolize strings        
    equlhs, equrhs = otsympify(equlhs_str, evaluate=False), otsympify(equrhs_str, evaluate=False)
    #last equations and colors for web elements
    last_equ_lhs, last_equ_rhs = equlhs[-1], equrhs[-1]
    num_colors_l = otops.get_colors_num(last_equ_lhs)
    num_colors_r = otops.get_colors_num(last_equ_rhs)
    dropmenu_color_l = webelements.get_color_dropmenu(num_colors_l, 'l')
    dropmenu_color_r = webelements.get_color_dropmenu(num_colors_r, 'r')
    
    #render page
    if err == 0:       
        return render.advview(webtex.concEqutoAlign(equlhs, equrhs, equtext),
                              dropmenu_color_l, dropmenu_color_r,
                              session.equT.equTableIndx, session.equT.record,session.equT.symvar,session.sidebarStatus,but_str)
    else:
        return render.advview(webtex.concEqutoAlign(equlhs, equrhs, equtext),
                              dropmenu_color_l, dropmenu_color_r,
                              session.equT.equTableIndx, session.equT.record, session.equT.symvar,session.sidebarStatus, but_str,
                              errs[err])           
  
#render inverse solver page
def inverseview_render(err = 0):
    #variable used
    svar = session.invequT.symvar

    #equation table for viewing
    equlhs_str, equrhs_str, equtext = session.invequT.getEquTable()

    #button strings
    but_str = webelements.get_button_strings(svar)  

    #symbolize strings  
    equlhs, equrhs = otsympify(equlhs_str, evaluate=False), otsympify(equrhs_str, evaluate=False)
    #last equations and colors for web elements
    last_equ_lhs, last_equ_rhs = equlhs[-1], equrhs[-1]
    num_colors_l = otops.get_colors_num(last_equ_lhs)
    num_colors_r = otops.get_colors_num(last_equ_rhs)
    dropmenu_color_l = webelements.get_color_dropmenu(num_colors_l, 'l')
    dropmenu_color_r = webelements.get_color_dropmenu(num_colors_r, 'r')
    
    #render page
    if err == 0:        
        return render.inverseview(webtex.concEqutoAlign(equlhs, equrhs, equtext), dropmenu_color_l, dropmenu_color_r, svar, but_str)
    elif err == 'session_expired':
        return render.inverseview([],[],[],errs['session_expired'])
    
    else:
        return render.inverseview(webtex.concEqutoAlign(equlhs, equrhs, equtext), dropmenu_color_l, dropmenu_color_r, svar, but_str, errs[err])             

#render question creation page           
def createquestion_render(mode, err=0, new_equ_lhs ='', new_equ_rhs=''):

    #detect equation type    
    if mode == 'adv':
        renderfunc = render.createadvquestion
        equtable = session.equT
    elif mode == 'simple':
        renderfunc = render.createsimplequestion
        equtable = session.simplequT

    #get equations already created    
    user_equlhs_str, user_equrhs_str = equtable.getUserEqus()
    #tidy strings if multiplied by -1
    new_equ_lhs_str = str(new_equ_lhs)
    new_equ_rhs_str = str(new_equ_rhs)
    new_equ_lhs_str = new_equ_lhs_str.replace(" - 1*"," - ")
    new_equ_rhs_str = new_equ_rhs_str.replace(" - 1*"," - ")

    #make symbolic representations    
    user_equlhs = otsympify(user_equlhs_str, evaluate = False)
    user_equrhs = otsympify(user_equrhs_str, evaluate = False)
        
    if err == 0:
            
        return renderfunc(webtex.concEqutoAlign([new_equ_lhs], [new_equ_rhs]),
                          new_equ_lhs_str, new_equ_rhs_str,
                          webelements.get_userequ_table(user_equlhs, user_equrhs))                   
    elif err == 1:
        return renderfunc('','','',
                          webelements.get_userequ_table(user_equlhs, user_equrhs),errs['equ_error'])
    elif err == 2:
        return renderfunc('',new_equ_lhs_str,new_equ_rhs_str,
                          webelements.get_userequ_table(user_equlhs, user_equrhs))
        
    elif err == 3:
        return renderfunc('',new_equ_lhs_str,new_equ_rhs_str,
                          webelements.get_userequ_table(user_equlhs, user_equrhs),errs['own_equs_full'])
    elif err == 4:
        return renderfunc('',new_equ_lhs_str,new_equ_rhs_str,
                          webelements.get_userequ_table(user_equlhs, user_equrhs),errs['equ_error_load'])
    elif err == 5:
        return renderfunc('',new_equ_lhs_str,new_equ_rhs_str,
                          webelements.get_userequ_table(user_equlhs, user_equrhs),errs['session_expired'])

#render question solved page
def questionsolved_render(mode,err=0):
    
    if mode == 'adv':
        equtable = session.equT
        renderfunc = render.advquestionsolved
        redirect = "/advview"
    elif mode == 'simple':
        equtable = session.simplequT
        renderfunc = render.simplequestionsolved
        redirect = "/simpleview"
    equlhs_str, equrhs_str, equtext = equtable.getEquTable()
    equlhs, equrhs = otsympify(equlhs_str, evaluate = False), otsympify(equrhs_str, evaluate = False)
    
    if equtext == []:
        raise web.seeother(redirect)
    elif rgex.search(r'Hie', equtext[-1]) == None:   
        raise web.seeother(redirect)
        
    if err == 0:    
        if isinstance(equtable.record,str):
            equtable.record = equtable.equTableIndx
            if not equtable.userEquIx == None:
                equtable.userEquRecord[equtable.userEquIx] = equtable.equTableIndx
            return renderfunc(webtex.concEqutoAlign(equlhs, equrhs, equtext),
                                        equtable.equTableIndx, equtable.record)
        elif equtable.record > equtable.equTableIndx :
            equtable.record = equtable.equTableIndx
            
            return renderfunc(webtex.concEqutoAlign(equlhs, equrhs, equtext),
                                        equtable.equTableIndx, equtable.record)
        else:
            return renderfunc(webtex.concEqutoAlign(equlhs, equrhs, equtext),
                                        equtable.equTableIndx, equtable.record)
    elif err == 2:
        return renderfunc(webtex.concEqutoAlign(equlhs, equrhs, equtext),equtable.equTableIndx,
                          equtable.record, errs['equ_error_load'])


#supporting functions for solver operations
def createquestion_handler(webinp, mode, equtable, redirect, redirect2):

    if webinp.postBut == "file_upload":
        f = web.input(upload_equs={})
        
        try:     
            uplEquArray = json.load(f['upload_equs'].file)
            newUserEqusL = uplEquArray[0]
            newUserEqusR = uplEquArray[1]
            sym_equ_lhs, sym_equ_rhs = otsympify(newUserEqusL),otsympify(newUserEqusR)
            
        except (SyntaxError,IOError, SympifyError, ValueError):
            return createquestion_render(mode,err=4)
        
        else:
            if not test_linpoly(sym_equ_lhs[-1], mode) or not test_linpoly(sym_equ_rhs[-1], mode)\
            or not test_linpoly(sym_equ_lhs[-1]-sym_equ_rhs[-1], mode):
                return createquestion_render(mode,err=4)
            
            else:
                for (equL,equR) in zip(newUserEqusL,newUserEqusR):
                    if len(equtable.userEquLhs) < 10:
                        equtable.addUserEqu(equL, equR)
                    else:
                        return createquestion_render(mode,err=3)
                
                raise web.seeother(redirect2)
        
    elif webinp.postBut == "file_download":
        web.header('Content-Type','application/json')
        web.header('Content-disposition', 'attachment; filename=omat_yhtalot.txt')
        sessid = str(session.session_id)
        with open(rootpath+'/web_ui/sessions/'+sessid+'_omat_yhtalot.txt','w') as outfile:
            json.dump([equtable.userEquLhs,equtable.userEquRhs],outfile)
        return open(rootpath+'/web_ui/sessions/'+sessid+'_omat_yhtalot.txt').read()
    
    elif webinp.postBut == "show_equ":
        try:
            sym_equ_lhs = otsympify(webinp.inp_equ_lhs, evaluate = False)
            sym_equ_rhs = otsympify(webinp.inp_equ_rhs, evaluate = False)

        except (SympifyError, IndexError):
            return createquestion_render(mode,1)
        else:
            return createquestion_render(mode,0,sym_equ_lhs, sym_equ_rhs)
                                            
    elif webinp.postBut == "save_equ":
            
        try:
            sym_equ_lhs = otsympify(webinp.inp_equ_lhs, evaluate = False)
            sym_equ_rhs = otsympify(webinp.inp_equ_rhs, evaluate = False)

                
        except (SympifyError, IndexError):
            return createquestion_render(mode,1)
        else:
            #check if the input equation is linear
            if not test_linpoly(sym_equ_lhs, mode) or not test_linpoly(sym_equ_rhs, mode)\
            or not test_linpoly(sym_equ_lhs-sym_equ_rhs, mode):
                return createquestion_render(mode,1)
           
            user_equsl_tmp,_ = equtable.getUserEqus()
            if len(user_equsl_tmp) < 10:
                new_equlhs_str,  new_equrhs_str = str(sym_equ_lhs), str(sym_equ_rhs)
                equtable.addUserEqu(new_equlhs_str, new_equrhs_str)
                return createquestion_render(mode,0, sym_equ_lhs, sym_equ_rhs)
            else:
                return createquestion_render(mode,3)
        
    elif "solve_equ" in webinp.postBut:
            
        last_char = webinp.postBut[-1]
        if last_char == 'x':
            try:
                sym_equ_lhs = otsympify(webinp.inp_equ_lhs, evaluate = False)
                sym_equ_rhs = otsympify(webinp.inp_equ_rhs, evaluate = False)
                
            except (SympifyError, IndexError):
                return createquestion_render(mode,1)
            else:
                #check if the input equation is linear
                if not test_linpoly(sym_equ_lhs, mode) or not test_linpoly(sym_equ_rhs, mode)\
                or not test_linpoly(sym_equ_lhs-sym_equ_rhs, mode):
                    return createquestion_render(mode,1)
                
                new_equlhs_str,  new_equrhs_str = str(sym_equ_lhs), str(sym_equ_rhs)
                equtable.clearEquTable(mode,1)
                equtable.initEquTable(0,'new',new_equlhs_str,new_equrhs_str)
                raise web.seeother(redirect)
        else:    
            ix = int(webinp.postBut[-1])
            
            equtable.clearEquTable(mode,1)
            equtable.initEquTable(ix,'user')
            raise web.seeother(redirect)
        
    elif "edit_equ" in webinp.postBut:
            
        ix = int(webinp.postBut[-1])  
        edit_equlhs_str, edit_equrhs_str = equtable.getUserEqu(ix)
        edit_equlhs = otsympify(edit_equlhs_str, evaluate = False)
        edit_equrhs = otsympify(edit_equrhs_str, evaluate = False)
        #equtable.removeUserEqu(ix)
        return createquestion_render(mode,0, edit_equlhs, edit_equrhs)
        
    elif "del_equ" in webinp.postBut:
            
        ix = int(webinp.postBut[-1])
        if not webinp.inp_equ_lhs =='':
            tmp_equlhs = otsympify(webinp.inp_equ_lhs, evaluate = False)
        else:
            tmp_equlhs = ''
                
        if not webinp.inp_equ_rhs == '':
            tmp_equrhs = otsympify(webinp.inp_equ_rhs, evaluate = False)
        else:
            tmp_equrhs = ''
            
        equtable.removeUserEqu(ix)
            
        if tmp_equlhs == '' and tmp_equrhs == '':
            return createquestion_render(mode,2, tmp_equlhs, tmp_equrhs)
        else:
            return createquestion_render(mode,0, tmp_equlhs, tmp_equrhs)             
    
def test_linpoly(a, mode):
    if not len(a.free_symbols) == 0:
        if not a.is_polynomial:
            return False
        elif Poly(a).is_multivariate:
            return False
        elif not Poly(a).is_linear:
            return False
        elif mode == 'simple' and not rgex.search('[(]', str(a)) == None:
            return False
        else:
            return True
                
    elif len(a.free_symbols) == 0 and not isinstance(simplify(a),(Integer,Rational)):
        return False
    
    else:
        return True
    
def save_invequ(mode):
    if mode == 'simple':        
        if not hasattr(session,'simplequT'):
            session.simplequT = otequhandle.EquTable('simple')
        equtable = session.simplequT
        redirect = '/createsimplequestion'
        
    elif mode == 'adv':        
        if not hasattr(session,'equT'):
            session.equT = otequhandle.EquTable()
        equtable = session.equT
        redirect = '/createadvquestion'
            
    sym_equ_lhs = otsympify(session.invequT.equTableLhs[-1],evaluate=False)
    sym_equ_rhs = otsympify(session.invequT.equTableRhs[-1], evaluate=False)
    user_equsl_tmp,_ = equtable.getUserEqus()
    if len(user_equsl_tmp) < 10:
        if not test_linpoly(sym_equ_lhs, mode) or not test_linpoly(sym_equ_rhs, mode)\
        or not test_linpoly(sym_equ_lhs-sym_equ_rhs, mode):
            return inverseview_render('equ_error_create')
        else:
            new_equlhs_str,  new_equrhs_str = str(sym_equ_lhs), str(sym_equ_rhs)
            equtable.addUserEqu(new_equlhs_str, new_equrhs_str)
            raise web.seeother(redirect)
    else:
        return inverseview_render('own_equs_full')                      
                

#handle advanced solver and inverse solver operations
def advops_handler(webinp, side, mode='adv'):
    if mode == 'adv':
        equtable = session.equT
        renderfunc = advview_render
        
    elif mode == 'inv':
        equtable = session.invequT
        renderfunc = inverseview_render   
    if side == 'left':
            
        inps = {'postBut': webinp.postBut,
                'color': webinp.color_drop_l,
                'inp_expr': webinp.inp_expr_l}
                    
    elif side == 'right':
            
        inps = {'postBut': webinp.postBut,
                'color': webinp.color_drop_r,
                'inp_expr': webinp.inp_expr_r}
                    
    if inps['postBut'].find("mod_expr_mn") > -1:
        op = 'merge_terms'
        equtable.exprMods(op, inps['color'], side, 'const')
        return renderfunc()
            
    elif inps['postBut'].find("mod_expr_mx") > -1:
        op = 'merge_terms'
        equtable.exprMods(op, inps['color'], side, 'xterm')
        return renderfunc()
            
    elif inps['postBut'].find("mod_expr_rb") > -1:
        op = 'remove_braces'
        equtable.exprMods(op, inps['color'], side, 'dum')
        return renderfunc()
            
    elif inps['postBut'].find("mod_expr_cf") > -1:
        op = 'common_factor'      
        try:
            sym_fact = otsympify(inps['inp_expr'], evaluate=False)
                    
        except SympifyError:
                return renderfunc('expr_error')
  
        else:
            if not test_linpoly(sym_fact, mode):
                return renderfunc('inp_expr_error')
            if ratsimp(sym_fact) == 0:
                return renderfunc('zero_comm_fact')
            str_fact = str(sym_fact)
            equtable.exprMods(op, inps['color'], side, str_fact)
            return renderfunc()


def handleFileIO(webinp, mode):
    if mode == 'adv':
        equtable = session.equT
        redirect2 = "/advview"
    elif mode == 'simple':
        equtable = session.simplequT
        redirect2 = "/simpleview"
        
    if webinp.postBut == "upload_solution_file":
        
        f = web.input(upload_solution={})
        try:
            uplEquArray = json.load(f['upload_solution'].file)
            newEqusL = uplEquArray[0]
            newEqusR = uplEquArray[1]
            newEqusText = uplEquArray[2]
            otsympify(newEqusL),otsympify(newEqusR)            
        except (SyntaxError,IOError, SympifyError, ValueError):
            return questionsolved_render(mode, 2)
        else:
            equtable.clearEquTable()
            equtable.equTableLhs = newEqusL
            equtable.equTableRhs = newEqusR
            equtable.equTableText = newEqusText
            equtable.equTableIndx = len(newEqusL)-1     
            web.seeother(redirect2)
            
    elif webinp.postBut == "download_solution":
        web.header('Content-Type','application/json')
        web.header('Content-disposition', 'attachment; filename=oma_ratkaisu.txt')
        sessid = str(session.session_id)
        with open(rootpath+'web_ui//sessions/'+sessid+'_oma_ratkaisu.txt','w') as outfile:
            json.dump([equtable.equTableLhs, equtable.equTableRhs, equtable.equTableText],outfile)
        return open(rootpath+'/web_ui/sessions/'+sessid+'_oma_ratkaisu.txt').read()   
    
if __name__=="__main__":
    
    
    app.run()
