from vepar import *
from Token import *
import re
from typing import List

rt.funkcijeSada = ['Z', 'Sc']
rt.funkcijeAST = Memorija(redefinicija=True)

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
        assert self.n > 0, 'Indeks koordinatne projekcije I_' + str(self.n) + ' mora biti pozitivan!'
        assert self.n <= len(x), 'Mjesnost (' + str(len(x)) + ') koordinatne projekcije je manja od njenog indeksa ' + str(self.n) + '!'
        return x[self.n - 1]
            
class Program(AST):
    naredbe: List[AST]
    
    def izvrši(self):
        funkcije = rt.funkcijeAST
        rt.funkcijeSada = ['Z', 'Sc']
        self.def_inicijalne(funkcije)
        returnString = ''
        for naredba in self.naredbe:
            if naredba is not nenavedeno:
                if not isinstance(naredba, Definicija):
                    try:
                        returnString += str(naredba.izvrši(Memorija(), funkcije)) + '\n'
                    except Exception as e:
                        returnString += 'Semantička greška: ' + str(e) + '\n'
                else:
                    try:
                        naredba.izvrši(Memorija(), funkcije)
                        rt.funkcijeAST = funkcije
                    except Exception as e:
                        returnString += 'Semantička greška: ' + str(e) + '\n'
        return returnString
    
    def def_inicijalne(self, funkcije):
        funkcije[Token(T.IME, 'Z')] = PythonFunction(Token(T.IME, 'Z'), Z)
        funkcije[Token(T.IME, 'Sc')] = PythonFunction(Token(T.IME, 'Sc'), Sc)

    def stablo(self):
        self.ime = Token(T.IME, 'PROGRAM')
        self.djeca = self.naredbe
        for naredba in self.naredbe:
            if naredba is not nenavedeno:
                naredba.stablo()

class PythonFunction(AST):
    ime: Token
    izraz: AST
    
    def pozovi(self, argumenti, memorija, funkcije):
        return funkcije[self.ime].izraz(argumenti[0])
    
class Dummy(AST):
    ime: Token
    def izvrši(self, memorija, funkcije):
        assert False, 'Nedostaje #Base ili #Step verzija funkcije ' + self.ime.sadržaj + '!'

class Definicija(AST):
    ime: Token
    parametri: List[AST]
    izraz: AST
    izr: str
    
    def izvrši(self, memorija, funkcije):
        funkcije[self.ime] = self   # definiraj ovu funkciju
        if stepString in self.ime.sadržaj:
            ime = Token(T.IME, self.ime.sadržaj[:-len(stepString)])
            funkcije[ime] = Definicija(ime, self.parametri[:-1], Dummy(ime), ime.sadržaj + baseString + ': ' + funkcije[ime.sadržaj + baseString].izr + '<br>' + ime.sadržaj + stepString + ': ' + funkcije[self.ime].izr)
            if isinstance(funkcije[ime].parametri[-1], Poziv): funkcije[ime].parametri[-1] = funkcije[ime].parametri[-1].parametri[0]  # zamijeni Sc(y) s y u običnoj verziji funkcije
            if isinstance(funkcije[self.ime].parametri[-2], Poziv): funkcije[self.ime].parametri[-2] = funkcije[self.ime].parametri[-2].parametri[0]    # zamijeni Sc(y) s y u #Step verziji funkcije
        self.provjeri_parametre()
    
    def pozovi(self, argumenti, memorija, funkcije):
        assert len(self.parametri) == len(argumenti), 'Funkcija ' + self.ime.sadržaj + ' je mjesnosti ' + str(len(self.parametri)) + ', a ne ' + str(len(argumenti)) + '!'
        if baseString in self.ime.sadržaj:
            return funkcije[self.ime].izraz.izvrši(Memorija(zip(self.parametri, argumenti)), funkcije)
        elif stepString not in self.ime.sadržaj and self.ime.sadržaj + baseString in funkcije:
            z = funkcije[self.ime.sadržaj + baseString].pozovi(argumenti[:-1], memorija, funkcije)
            for i in range(argumenti[-1]):
                args = argumenti[:-1]
                args.append(i)
                args.append(z) 
                z = funkcije[self.ime.sadržaj + stepString].pozovi(args, memorija, funkcije)
            return z
        return funkcije[self.ime].izraz.izvrši(Memorija(zip(self.parametri, argumenti)), funkcije)
    
    def provjeri_parametre(self):
        viđeni = set()
        for param in self.parametri:
            assert param not in viđeni, 'Funkcija ' + self.ime.sadržaj + ' ima više parametara s istim imenom ' + param.sadržaj + '!'
            viđeni.add(param)

    def stablo(self):
        self.djeca = [self.izraz]
        self.izraz.stablo()
    

class Poziv(AST):
    ime: Token
    parametri: List[AST]
    
    def izvrši(self, memorija, funkcije):
        if re.match(r'I_\d+', self.ime.sadržaj):
            return I(int(self.ime.sadržaj[2:]))(*[parametar.izvrši(memorija, funkcije) for parametar in self.parametri])
        return funkcije[self.ime].pozovi([parametar.izvrši(memorija, funkcije) for parametar in self.parametri], memorija, funkcije)
    
    def stablo(self):
        self.djeca = self.parametri
        for parametar in self.parametri:
            parametar.stablo()
            
class Log_ILI(AST):
    disjunkcija: List[AST]
    
    def izvrši(self, memorija, funkcije):
        for konjunkcija in self.disjunkcija:
            value = konjunkcija.izvrši(memorija, funkcije)
            if value: return value
        return 0
    
    def stablo(self):
        self.ime = Token(T.IME, 'ILI')
        self.djeca = self.disjunkcija
        for konjunkcija in self.disjunkcija:
            konjunkcija.stablo()
    
class Log_I(AST):
    konjunkcija: List[AST]

    def izvrši(self, memorija, funkcije):
        value = 0
        for literal in self.konjunkcija:
            value = literal.izvrši(memorija, funkcije)
            if value == 0: return 0
        if len(self.konjunkcija) == 1: return value
        return 1
    
    def stablo(self):
        self.ime = Token(T.IME, 'I')
        self.djeca = self.konjunkcija
        for literal in self.konjunkcija:
            literal.stablo()
    
class Log_NE(AST):
    literal: AST

    def izvrši(self, memorija, funkcije):
        value = self.literal.izvrši(memorija, funkcije)
        if value: return 0
        return 1
    
    def stablo(self):
        self.ime = Token(T.IME, 'NE')
        self.djeca = [self.literal]
        self.literal.stablo()
    
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
    
    def stablo(self):
        self.ime = Token(T.IME, 'OGR_MIN')
        self.djeca = [self.relacija]
        self.relacija.stablo()
    
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

    def stablo(self):
        self.ime = Token(T.IME, 'NEOGR_MIN')
        self.djeca = [self.relacija]
        self.relacija.stablo()

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
    
    def stablo(self):
        self.ime = Token(T.IME, 'BROJEĆA')
        self.djeca = [self.relacija]
        self.relacija.stablo()
    
class Grananje(AST):
    uvjeti: List[AST]
    vrijednosti: List[AST]
    
    def izvrši(self, memorija, funkcije):
        for i, uvjet in enumerate(self.uvjeti):
            if uvjet.izvrši(memorija, funkcije) and i < len(self.vrijednosti):
                return self.vrijednosti[i].izvrši(memorija, funkcije)
        return self.uvjeti[-1].izvrši(memorija, funkcije)
    
    def stablo(self):
        self.ime = Token(T.IME, 'IF')
        self.djeca = self.vrijednosti
        for vrijednost in self.vrijednosti:
            vrijednost.stablo()
        