from vepar import *
from Token import *

defaultString = 'Default'

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
        for value in self.funkcije.podaci.values():
            print(value.ime)
        for naredba in self.naredbe:
            if isinstance(naredba, Call):
                if hasattr(naredba.parametri[-1], 'sadržaj') and int(naredba.parametri[-1].sadržaj) == 0 and naredba.ime.sadržaj + defaultString in self.funkcije.podaci.keys():
                    defaultNaredba = naredba
                    defaultNaredba.ime = Token(T.IME, naredba.ime.sadržaj + defaultString)
                    print(defaultNaredba.izvrši(Memorija(), self.funkcije))
                else:
                    print(naredba.izvrši(Memorija(), self.funkcije))

class Function(AST):
    def __init__(self, ime, parametri, izraz):
        self.ime = ime
        self.parametri = parametri
        self.izraz = izraz
    
    def izvrši(self, memorija, funkcije):
        funkcije[self.ime] = self

    def pozovi(self, argumenti, funkcije):
        pomocni = self.parametri.copy()
        if self.parametri[-1].sadržaj[-2:] == '+1':
            argumenti[-1] -= 1
            pomocni[-1] = Token(T.IME, self.parametri[-1].sadržaj[:-2])
        lokalna = Memorija(zip(pomocni, argumenti))
        try:
            return self.izraz.izvrši(lokalna, funkcije)
        except Povratak as povratak:
            return povratak.vrijednost

class Add(AST):
    def __init__(self, izraz):
        self.izraz = izraz
    
    def vrijednost(self, memorija, funkcije):
        return sum(term.vrijednost(memorija, funkcije) for term in self.izraz)
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
class Variable(AST):
    def __init__(self, ime):
        self.ime = ime
    
    def vrijednost(self, memorija, funkcije):
        return memorija[self.ime]
    
    def izvrši(self, memorija, funkcije):
        #if memorija.__len__() != 0 and memorija[nađiZadnju(memorija)] > 0:
            #memorija[nađiZadnju(memorija)] -= 1
        return self.vrijednost(memorija, funkcije)
    
class Integer(AST):
    def __init__(self, broj):
        self.broj = broj
    
    def vrijednost(self, memorija, funkcije):
        return self.broj
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)

    
class Call(AST):
    def __init__(self, ime, parametri):
        self.ime = ime
        self.parametri = parametri

    def vrijednost(self, memorija, funkcije):
        if memorija.__len__() != 0 and memorija[nađiZadnju(memorija)] <= 0 and self.ime.sadržaj + defaultString in funkcije.podaci.keys():
            defaultIme = Token(T.IME, self.ime.sadržaj + defaultString)
            povratak = funkcije[defaultIme].izraz.izvrši(memorija, funkcije)
            return povratak
        if len(self.parametri) > 0:
            vrijednosti, pomocne = [], []
            for i,parametar in enumerate(self.parametri):
                pomocne.append(funkcije[self.ime].parametri[i])
                vrijednosti.append(parametar.vrijednost(memorija, funkcije))
            if pomocne[-1].sadržaj[-2:] == '+1':
                pomocne[-1] = Token(T.IME, pomocne[-1].sadržaj[:-2])
            povratak = funkcije[self.ime].pozovi(vrijednosti, funkcije)
            return povratak
        vrijednosti = []
        for parametar in self.parametri:
            vrijednosti.append(parametar.vrijednost(memorija, funkcije))
        povratak = funkcije[self.ime].pozovi(vrijednosti, funkcije)
        return povratak
    
    def izvrši(self, memorija, funkcije):
        parametri = [parametar.vrijednost(memorija, funkcije) for parametar in self.parametri]
        if parametri[-1] == 0 and defaultString not in self.ime.sadržaj and self.ime.sadržaj + defaultString in funkcije.podaci.keys():
            defaultIme = Token(T.IME, self.ime.sadržaj + defaultString)
            return funkcije[defaultIme].pozovi(parametri, funkcije)
        return funkcije[self.ime].pozovi(parametri, funkcije)
        

class Minimize(AST):
    def __init__(self, min_var, ime, argumenti):
        self.min_var = min_var
        self.ime = ime
        self.argumenti = argumenti
    
    def vrijednost(self, memorija, funkcije):
        memorija[self.min_var] = 0
        while ...:
            argumenti = [argument.vrijednost(memorija, funkcije) for argument in self.argumenti]
            check = funkcije[self.ime].pozovi(argumenti, funkcije)
            if check == 1:
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

