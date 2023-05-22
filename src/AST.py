from vepar import *
from Token import *

baseString = '#Base'
stepString = '#Step'

def nađiZadnju(memorija):
    return list(memorija.podaci.keys())[-1]

class Povratak(NelokalnaKontrolaToka):
    """Signal koji šalje naredba vrati."""

class Program(AST):

    def __init__(self, naredbe, funkcije, relacije, karakteristične_funkcije):
        self.naredbe = naredbe
        self.funkcije = funkcije
        self.relacije = relacije
        self.karakteristične_funkcije = karakteristične_funkcije
    
    def izvrši(self):
        print(self.funkcije.podaci.keys())
        for naredba in self.naredbe:
            if isinstance(naredba, Call):
                if hasattr(naredba.parametri[-1], 'sadržaj') and int(naredba.parametri[-1].sadržaj) == 0 and naredba.ime.sadržaj + baseString in self.funkcije.podaci.keys():
                    defaultNaredba = naredba
                    defaultNaredba.ime = Token(T.IME, naredba.ime.sadržaj + baseString)
                    print(defaultNaredba.izvrši(Memorija(), self.funkcije))
                else:
                    print(naredba.izvrši(Memorija(), self.funkcije))

class PythonFunction(AST):
    def __init__(self, ime, parametri, izraz):
        self.ime = ime
        self.parametri = parametri
        self.izraz = izraz

    def izvrši(self, memorija, funkcije):
        funkcije[self.ime] = self
    
    def pozovi(self, argumenti, funkcije):
        return self.izraz(argumenti[0])

class Function(AST):
    def __init__(self, ime, parametri, izraz):
        self.ime = ime
        self.parametri = parametri
        self.izraz = izraz
    
    def izvrši(self, memorija, funkcije):
        funkcije[self.ime] = self

    def pozovi(self, argumenti, funkcije):
        if baseString not in self.ime.sadržaj and stepString not in self.ime.sadržaj and self.ime.sadržaj + baseString in funkcije.podaci.keys():
            z = funkcije[self.ime.sadržaj + baseString].pozovi(argumenti[:-1], funkcije)
            for i in range(argumenti[-1]):
                args = argumenti[:-1]
                args.append(i)
                args.append(z)
                z = funkcije[self.ime.sadržaj + stepString].pozovi(args, funkcije)
            return z
        pomocni = self.parametri.copy()
        if stepString in self.ime.sadržaj:
            pomocni[-2] = Token(T.IME, self.parametri[-2].parametri[0].sadržaj) # promijeni Sc(x) u x
            lokalna = Memorija(zip(pomocni, argumenti))
            return self.izraz.izvršiStep(self.ime.sadržaj[:-len(stepString)], argumenti[-1], lokalna, funkcije)
        lokalna = Memorija(zip(pomocni, argumenti))
        return self.izraz.izvrši(lokalna, funkcije)
    
class Variable(AST):
    def __init__(self, ime):
        self.ime = ime
    
    def vrijednost(self, memorija, funkcije):
        return memorija[self.ime]
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
    def izvršiStep(self, ime, prev, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
class Integer(AST):
    def __init__(self, broj):
        self.broj = broj
    
    def vrijednost(self, memorija, funkcije):
        return self.broj
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
    def izvršiStep(self, ime, prev, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
class Previous(AST):
    def __init__(self, ime, value):
        self.value = value
        self.ime = Token(T.IME, ime)
    
    def vrijednost(self, memorija, funkcije):
        return self.value
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
    def izvršiStep(self, ime, prev, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)

    
class Call(AST):
    def __init__(self, ime, parametri):
        self.ime = ime
        self.parametri = parametri

    def vrijednost(self, memorija, funkcije):
        parametri = [parametar.vrijednost(memorija, funkcije) for parametar in self.parametri]
        return funkcije[self.ime].pozovi(parametri, funkcije)
    
    def izvrši(self, memorija, funkcije):
        parametri = [parametar.vrijednost(memorija, funkcije) for parametar in self.parametri]
        return funkcije[self.ime].pozovi(parametri, funkcije)

    def izvršiStep(self, ime, prev, memorija, funkcije):
        self.find(ime, prev)
        parametri = [parametar.vrijednost(memorija, funkcije) for parametar in self.parametri]
        return funkcije[self.ime].pozovi(parametri, funkcije)
    
    def find(self, ime, prev):
        for i, parametar in enumerate(self.parametri):
            if hasattr(parametar, 'ime') and parametar.ime.sadržaj == ime:
                self.parametri[i] = Previous(ime, prev)
                return self.parametri[i]
            elif isinstance(parametar, Call):
                return parametar.find(ime, prev)
        

class Minimize(AST):
    def __init__(self, min_var, ime, argumenti):
        self.min_var = min_var
        self.ime = ime
        self.argumenti = argumenti
    
    def vrijednost(self, memorija, funkcije):
        memorija[self.min_var] = 0
        while ...:
            argumenti = [argument.vrijednost(memorija, funkcije) for argument in self.argumenti]
            if funkcije[self.ime].pozovi(argumenti, funkcije):
                break
            memorija[self.min_var] += 1 
        return memorija[self.min_var]
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
class MinimizeRelations(AST):
    def __init__(self, min_var, relacije, argumenti, logic):
        self.min_var = min_var
        self.relacije = relacije
        self.argumenti = argumenti
        self.logic = logic

    def vrijednost(self, memorija, funkcije):
        memorija[self.min_var] = 0
        while ...:
            povratne = []
            for i,argumentiRelacije in enumerate(iter(self.argumenti)):
                argumenti = [argument.vrijednost(memorija, funkcije) for argument in argumentiRelacije]
                povratne.append(funkcije[self.relacije[i]].pozovi(argumenti, funkcije))
            if self.check(povratne):
                break
            memorija[self.min_var] += 1
        return memorija[self.min_var]
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
    def check(self, povratne):
        value = povratne[0]
        for i in range(1, len(povratne)):
            if self.logic[i-1] == 'and':
                value = value and povratne[i]
            elif self.logic[i-1] == 'or':
                value = value or povratne[i]
        return value
    
class Logic(AST):
    def __init__(self, terms, logic):
        self.terms = terms
        self.logic = logic

    def vrijednost(self, memorija, funkcije):
        value = self.terms[0].vrijednost(memorija, funkcije)
        for i in range(1, len(self.terms)):
            if self.logic[i-1] == 'and':
                value = value and self.terms[i].vrijednost(memorija, funkcije)
            elif self.logic[i-1] == 'or':
                value = value or self.terms[i].vrijednost(memorija, funkcije)
        if value:
            return 1
        return 0


    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
class Literal(AST):
    def __init__(self, istinitost, term):
        self.istinitost = istinitost
        self.term = term

    def vrijednost(self, mem, unutar):
        return self.term.vrijednost(mem, unutar) if self.istinitost == 'aff' else not self.term.vrijednost(mem, unutar)
    

class Cardinality(AST):
    def __init__(self, card_var, inequality, bound, relacija, argumenti):
        self.card_var = card_var
        self.inequality = inequality
        self.bound = bound
        self.relacija = relacija
        self.argumenti = argumenti
    
    def vrijednost(self, memorija, funkcije):
        memorija[self.card_var] = 0
        plus = 0
        if self.inequality.sadržaj == '<=':
            plus = 1
        ograda = self.bound.vrijednost(memorija, funkcije)
        argumenti = [argument.vrijednost(memorija, funkcije) for argument in self.argumenti]
        for i in (range(ograda + plus)):
            check = funkcije[self.relacija].pozovi(argumenti, funkcije)
            if check == 1:
                memorija[self.card_var] += 1.
            for i,arg in enumerate(iter(self.argumenti)):
                if arg.ime == self.card_var.sadržaj:
                    argumenti[i] += 1
                    break 
        return memorija[self.card_var]
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)

