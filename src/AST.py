from vepar import *
from Token import *
import re
from typing import List

baseString = '#Base'
stepString = '#Step'
prevString = '#Prev'

def Z(x):
    return 0
def Sc(x):
    return x + 1
class I:
    n: int
    def __init__(self, n):
        self.n = n
    def __call__(self, *x):
        return x[self.n - 1]
            
class Program(AST):
    naredbe: List[AST]
    
    def izvrši(self):
        funkcije = Memorija()
        self.def_inicijalne(funkcije)
        for naredba in self.naredbe:
            if naredba is not nenavedeno:
                print(naredba.izvrši(Memorija(), funkcije)) if isinstance(naredba, Poziv) else naredba.izvrši(Memorija(), funkcije)

    def def_inicijalne(self, funkcije):
        funkcije[Token(T.IME, 'Z')] = PythonFunction(Token(T.IME, 'Z'), Z)
        funkcije[Token(T.IME, 'Sc')] = PythonFunction(Token(T.IME, 'Sc'), Sc)

class PythonFunction(AST):
    ime: Token
    izraz: AST
    
    def pozovi(self, argumenti, memorija, funkcije):
        return funkcije[self.ime].izraz(argumenti[0])

class Funkcija(AST):
    ime: Token
    parametri: List[AST]
    izraz: AST
    
    def izvrši(self, memorija, funkcije):
        funkcije[self.ime] = self
        if stepString in self.ime.sadržaj:
            ime = Token(T.IME, self.ime.sadržaj[:-len(stepString)])
            funkcije[ime] = Funkcija(ime, self.parametri[:-1], self.izraz)
            if isinstance(funkcije[self.ime].parametri[-2], Poziv): self.parametri[-2] = self.parametri[-2].parametri[0]
            if isinstance(funkcije[self.ime].izraz, Poziv): funkcije[self.ime].izraz.zamijeni(ime, funkcije)
    
    def pozovi(self, argumenti, memorija, funkcije):
        assert len(self.parametri) == len(argumenti), 'Funkcija ' + self.ime.sadržaj + ' je mjesnosti ' + str(len(self.parametri)) + ', a ne ' + str(len(argumenti)) + '!'
        if baseString in self.ime.sadržaj:
            return self.izraz.izvrši(Memorija(zip(self.parametri, argumenti)), funkcije)
        elif stepString not in self.ime.sadržaj and self.ime.sadržaj + baseString in funkcije:
            z = funkcije[self.ime.sadržaj + baseString].pozovi(argumenti[:-1], memorija, funkcije)
            for i in range(argumenti[-1]):
                args = argumenti[:-1]
                args.append(i)
                args.append(z) 
                z = funkcije[self.ime.sadržaj + stepString].pozovi(args, memorija, funkcije)
            return z
        return self.izraz.izvrši(Memorija(zip(self.parametri, argumenti)), funkcije)
    

class Poziv(AST):
    ime: Token
    parametri: List[AST]
    
    def izvrši(self, memorija, funkcije):
        if re.match(r'I_\d+', self.ime.sadržaj):
            return I(int(self.ime.sadržaj[2:]))(*[parametar.izvrši(memorija, funkcije) for parametar in self.parametri])
        return funkcije[self.ime].pozovi([parametar.izvrši(memorija, funkcije) for parametar in self.parametri], memorija, funkcije)
    
    def zamijeni(self, ime, funkcije):
        for i, parametar in enumerate(self.parametri):
            if hasattr(parametar, 'ime') and parametar.ime.sadržaj == ime.sadržaj:
                self.parametri[i] = Token(T.IME, prevString)
                return self.parametri[i]
            elif isinstance(parametar, Poziv):
                return parametar.zamijeni(ime, funkcije)
            
class Log_ILI(AST):
    disjunkcija: List[AST]
    
    def izvrši(self, memorija, funkcije):
        for konjunkcija in self.disjunkcija:
            value = konjunkcija.izvrši(memorija, funkcije)
            if value: return value
        return 0
    
class Log_I(AST):
    konjunkcija: List[AST]

    def izvrši(self, memorija, funkcije):
        value = 0
        for literal in self.konjunkcija:
            value = literal.izvrši(memorija, funkcije)
            if value == 0: return 0
        if len(self.konjunkcija) == 1: return value
        return 1
    
class Log_NE(AST):
    literal: AST

    def izvrši(self, memorija, funkcije):
        value = self.literal.izvrši(memorija, funkcije)
        if value: return 0
        return 1
    
class Ograničena_Minimizacija(AST):
    varijabla: Token
    plus: int
    ograda: AST
    relacija: AST
    
    def izvrši(self, memorija, funkcije):
        assert self.varijabla not in memorija, 'Varijabla ' + self.varijabla.sadržaj + ' je već definirana!'
        for i in range(self.ograda.izvrši(memorija, funkcije) + self.plus):
            memorija[self.varijabla] = i
            if self.relacija.izvrši(memorija, funkcije): return i
        return self.ograda.izvrši(memorija, funkcije) + self.plus
    
class Neograničena_Minimizacija(AST):
    varijabla: Token
    relacija: AST
    
    def izvrši(self, memorija, funkcije):
        assert self.varijabla not in memorija, 'Varijabla ' + self.varijabla.sadržaj + ' je već definirana!'
        i = 0
        while True:
            memorija[self.varijabla] = i
            if self.relacija.izvrši(memorija, funkcije): return i
            i += 1

class Brojeća(AST):
    varijabla: Token
    plus: int
    ograda: AST
    relacija: AST
    
    def izvrši(self, memorija, funkcije):
        assert self.varijabla not in memorija, 'Varijabla ' + self.varijabla.sadržaj + ' je već definirana!'
        count = 0
        for i in range(self.ograda.izvrši(memorija, funkcije) + self.plus):
            memorija[self.varijabla] = i
            if self.relacija.izvrši(memorija, funkcije): count += 1
        return count
    
class Grananje(AST):
    uvjeti: List[AST]
    vrijednosti: List[AST]
    
    def izvrši(self, memorija, funkcije):
        for i, uvjet in enumerate(self.uvjeti):
            if uvjet.izvrši(memorija, funkcije) and i < len(self.vrijednosti):
                return self.vrijednosti[i].izvrši(memorija, funkcije)
        return self.uvjeti[-1].izvrši(memorija, funkcije)