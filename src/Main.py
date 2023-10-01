from vepar import *
from AST import *
from Token import *
from Parser import *
from Lekser import *
import pathlib

ulaz = pathlib.Path('Inputs/Primjer_programa_u_funkcijskom_jeziku.txt').read_text(encoding='utf-8')
ulaz += '\n'
ast = P(ulaz)
ast.izvrši()