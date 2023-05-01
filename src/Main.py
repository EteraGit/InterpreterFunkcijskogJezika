from vepar import *
from AST import *
from Token import *
from Parser import *
import pathlib
import sys

sys.setrecursionlimit(10000)

ulaz = pathlib.Path('Inputs/SampleInput.txt').read_text(encoding='utf-8')

# Lexer(ulaz)

kôd = P(ulaz)

# prikaz(kôd)

kôd.izvrši()