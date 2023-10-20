from vepar import *
from AST import *
from Token import *
from Parser import *
from Lekser import *

with open('Inputs/Primjer_programa_u_funkcijskom_jeziku.txt', 'r') as ulaz:
    naredbe = []
    for linija in ulaz:
        if ':=' in linija: P.start = P.definicija 
        elif linija == '\n': continue
        else: P.start = P.evaluacija_izraza
        naredbe.append(P(linija))
    ast = Program(naredbe)
    ast.izvrši()