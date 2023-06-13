from vepar import *
from Token import *
from typing import List

baseString = '#Base'
stepString = '#Step'

class Program(AST):

    def __init__(self, naredbe, funkcije):
        self.naredbe = naredbe
        self.funkcije = funkcije
    
    def izvrši(self):
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
        # print('pozivam funkciju', self.ime.sadržaj, 's argumentima', argumenti)
        if baseString not in self.ime.sadržaj and stepString not in self.ime.sadržaj and self.ime.sadržaj + baseString in funkcije:
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
            value = self.izraz.izvršiStep(self.ime.sadržaj[:-len(stepString)], argumenti[-1], lokalna, funkcije)
            return value
        lokalna = Memorija(zip(pomocni, argumenti))
        return self.izraz.izvrši(lokalna, funkcije)
    
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
    def __init__(self, min_var, inequality, bound, relacija):
        self.min_var = min_var
        self.inequality = inequality
        self.bound = bound
        self.relacija = relacija
    
    def vrijednost(self, memorija, funkcije):
        memorija[self.min_var] = 0
        if self.bound is None:
            while True:
                val = self.relacija.vrijednost(memorija, funkcije)
                if val == 1:
                    break
                memorija[self.min_var] += 1
            return memorija[self.min_var]
        else:
            plus = 0
            if self.inequality.sadržaj == '<=':
                plus = 1
            ograda = self.bound.vrijednost(memorija, funkcije)
            for i in (range(ograda + plus)):
                val = self.relacija.vrijednost(memorija, funkcije)
                if val == 1:
                    break
                memorija[self.min_var] += 1
            return memorija[self.min_var]
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
class Cardinality(AST):
    def __init__(self, card_var, inequality, bound, relacija):
        self.card_var = card_var
        self.inequality = inequality
        self.bound = bound
        self.relacija = relacija
    
    def vrijednost(self, memorija, funkcije):
        memorija[self.card_var] = 0
        plus = 0
        if self.inequality.sadržaj == '<=':
            plus = 1
        ograda = self.bound.vrijednost(memorija, funkcije)
        count = 0
        for _ in (range(ograda + plus)):
            if self.relacija.vrijednost(memorija, funkcije):
                count += 1
            memorija[self.card_var] += 1
        return count
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
class Logical_OR(AST):
    logicalAND_list: List[AST]

    def __init__(self, logicalAND_list):
        self.logicalAND_list = logicalAND_list

    def vrijednost(self, memorija, funkcije):
        for log_and in self.logicalAND_list:
            value = log_and.vrijednost(memorija, funkcije)
            if value:
                return value
        return 0
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
    def izvršiStep(self, ime, prev, memorija, funkcije):
        return self.logicalAND_list[0].izvršiStep(ime, prev, memorija, funkcije)
    
    def find(self, ime, prev):
        for i, parametar in enumerate(self.logicalAND_list):
            if hasattr(parametar, 'ime') and parametar.ime.sadržaj == ime:
                self.logicalAND_list[i] = Previous(ime, prev)
                return self.logicalAND_list[i]
            else:
                return parametar.find(ime, prev)
    
class Logical_AND(AST):
    literal_list: List[AST]

    def __init__(self, literal_list):
        self.literal_list = literal_list

    def vrijednost(self, memorija, funkcije):
        value = 0
        for literal in self.literal_list:
            value = literal.vrijednost(memorija, funkcije)
            if not value:
                return value
        if len(self.literal_list) == 1:
            return value
        return 1
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
    def izvršiStep(self, ime, prev, memorija, funkcije):
        return self.literal_list[0].izvršiStep(ime, prev, memorija, funkcije)
    
    def find(self, ime, prev):
        for i, parametar in enumerate(self.literal_list):
            if hasattr(parametar, 'ime') and parametar.ime.sadržaj == ime:
                self.literal_list[i] = Previous(ime, prev)
                return self.literal_list[i]
            else:
                return parametar.find(ime, prev)
    
class Logical_NOT(AST):
    def __init__(self, literal):
        self.literal = literal

    def vrijednost(self, memorija, funkcije):
        value = self.literal.vrijednost(memorija, funkcije)
        if value: return 0
        return 1
    
    def izvrši(self, memorija, funkcije):
        return self.vrijednost(memorija, funkcije)
    
    def izvršiStep(self, ime, prev, memorija, funkcije):
        return self.literal.izvršiStep(ime, prev, memorija, funkcije)
    
    def find(self, ime, prev):
        if hasattr(self.literal, 'ime') and self.literal.ime.sadržaj == ime:
            self.literal = Previous(ime, prev)
            return self.literal
        else:
            return self.literal.find(ime, prev)

