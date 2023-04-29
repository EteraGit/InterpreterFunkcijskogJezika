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
        if memorija.__len__() != 0 and memorija[nađiZadnju(memorija)] > 0:
            memorija[nađiZadnju(memorija)] -= 1
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
            return funkcije[defaultIme].izraz.izvrši(memorija, funkcije)
        elif len(self.parametri) > 0:
            vrijednosti, pomocne = [], []
            for i,parametar in enumerate(self.parametri):
                pomocne.append(funkcije[self.ime].parametri[i])
                vrijednosti.append(parametar.vrijednost(memorija, funkcije))
            if pomocne[-1].sadržaj[-2:] == '+1':
                pomocne[-1] = Token(T.IME, pomocne[-1].sadržaj[:-2])
            pomocna = Memorija(zip(pomocne, vrijednosti))
            return funkcije[self.ime].izraz.izvrši(pomocna, funkcije)
        return funkcije[self.ime].izraz.izvrši(memorija, funkcije)
    
    def izvrši(self, memorija, funkcije):
        if memorija.__len__() != 0 and memorija[nađiZadnju(memorija)] > 0:
            memorija[nađiZadnju(memorija)] -= 1
        parametri = [parametar.vrijednost(memorija, funkcije) for parametar in self.parametri]
        if parametri[-1] == 0 and defaultString not in self.ime.sadržaj:
            defaultIme = Token(T.IME, self.ime.sadržaj + defaultString)
            return funkcije[defaultIme].pozovi(parametri, funkcije)
        return funkcije[self.ime].pozovi(parametri, funkcije)
    

