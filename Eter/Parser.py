from vepar import *
from AST import *
from Token import *
from Lekser import *

class P(Parser):
    trenutna: str
    zamjena: tuple

    def definicija(self):
        if self > KRAJ: return nenavedeno
        self.trenutna = None
        self.zamjena = None
        if self > T.UGOTV: return self.definicija_infix()
        return self.definicija_funkcije()
    
    def definicija_funkcije(self):
        ime = self >> T.IME
        self.trenutna = ime.sadržaj
        self >> T.OTV
        lijeve = self.lijeve_varijable()
        self >> T.ZATV
        self >> T.DEF_FUN
        if ime.sadržaj + baseString in rt.funkcijeSada: self.zamjena = (ime, lijeve.copy())
        izraz = self.izraz()
        self.zamjena = None
        return self.definiraj_i_vrati_funkciju(ime, lijeve, izraz)

    def definicija_infix(self):
        self >> T.UGOTV
        prvi = self.lijeva_varijabla()
        operator = Token(T.IME, (self >> T.OP).sadržaj)
        self.trenutna = operator.sadržaj
        drugi = self.lijeva_varijabla()
        self >> T.UGZATV
        self >> T.DEF_FUN
        if operator.sadržaj + baseString in rt.funkcijeSada: self.zamjena = (operator, [prvi, drugi].copy())
        izraz = self.izraz()
        self.zamjena = None
        return self.definiraj_i_vrati_funkciju(operator, [prvi, drugi], izraz)
    
    def definiraj_i_vrati_funkciju(self, ime, lijeve, izraz):
        if isinstance(lijeve[-1], Token) and lijeve[-1].sadržaj == '0':
            assert ime.sadržaj + baseString not in rt.funkcijeSada, 'Funkcija ' + ime.sadržaj + baseString + ' je već definirana!'
            rt.funkcijeSada.append(ime.sadržaj + baseString)
            return Definicija(Token(T.IME, ime.sadržaj + baseString), lijeve[:-1], izraz, self.izr)
        elif isinstance(lijeve[-1], Poziv) and lijeve[-1].ime.sadržaj == 'Sc':
            assert ime.sadržaj + stepString not in rt.funkcijeSada, 'Funkcija ' + ime.sadržaj + stepString + ' je već definirana!'
            assert ime.sadržaj + baseString in rt.funkcijeSada, 'Funkcija ' + ime.sadržaj + baseString + ' nije definirana!'
            rt.funkcijeSada.append(ime.sadržaj + stepString)
            rt.funkcijeSada.append(ime.sadržaj)
            lijeve.append(Token(T.IME, prevString))
            return Definicija(Token(T.IME, ime.sadržaj + stepString), lijeve, izraz, self.izr)
        assert ime.sadržaj not in rt.funkcijeSada, 'Funkcija ' + ime.sadržaj + ' je već definirana!'
        rt.funkcijeSada.append(ime.sadržaj)
        return Definicija(ime, lijeve, izraz, self.izr)
        
    def lijeve_varijable(self):
        lijeve = [self.lijeva_varijabla()]
        while self >= T.ZAREZ:
            lijeve.append(self.lijeva_varijabla())
        return lijeve
    
    def lijeva_varijabla(self):
        if ime := self >= T.IME:
            if self > T.OTV:
                assert ime.sadržaj == 'Sc', 'Jedini poziv funkcije koji smije biti lijeva varijabla je Sc!'
                return self.poziv_lijeve(ime)
            return ime
        broj = self >> T.BROJ
        assert broj.sadržaj == '0', 'Jedini broj koji smije biti lijeva varijabla je 0!'
        return broj
    
    def poziv_lijeve(self, ime):
        self >> T.OTV
        assert not self > T.ZATV, 'Funkcije s 0 argumenata nisu podržane!'
        varijabla = self >> T.IME
        self >> T.ZATV
        return Poziv(ime, [varijabla])
    
    def poziv_infix(self):
        self >> T.UGOTV
        lijevi = self.izraz()
        operator = Token(T.IME, (self >> T.OP).sadržaj)
        desni = self.izraz()
        self >> T.UGZATV
        if self.zamjena is not None:
            ime_zamjena, lijeve_zamjena = self.zamjena
            if isinstance(lijeve_zamjena[-1], Poziv): lijeve_zamjena[-1] = lijeve_zamjena[-1].parametri[0]
            if ime_zamjena == operator and lijeve_zamjena == [lijevi, desni]:
                return Token(T.IME, prevString)
        return Poziv(operator, [lijevi, desni])
    
    def poziv(self, ime):
        #assert ime.sadržaj in rt.funkcijeSada or ime.sadržaj == self.trenutna or re.match(r'I_\d+', ime.sadržaj), 'Funkcija ' + ime.sadržaj + ' nije definirana!'
        self >> T.OTV
        assert not self > T.ZATV, 'Funkcije s 0 argumenata nisu podržane!'
        desne = self.desne_varijable()
        self >> T.ZATV
        if self.zamjena is not None:
            ime_zamjena, lijeve_zamjena = self.zamjena
            if isinstance(lijeve_zamjena[-1], Poziv): lijeve_zamjena[-1] = lijeve_zamjena[-1].parametri[0]
            if ime_zamjena == ime and lijeve_zamjena == desne:
                return Token(T.IME, prevString)
        return Poziv(ime, desne)
    
    def desne_varijable(self):
        desne = [self.izraz()]
        while self >= T.ZAREZ:
            desne.append(self.izraz())
        return desne
    
    def evaluacija_izraza(self):
        self.trenutna = None
        self.zamjena = None
        if self > KRAJ: return nenavedeno
        return self.izraz()
    
    def izraz(self):
        return self.log_ILI()
    
    def log_ILI(self):
        disjunkcija = [self.log_I()]
        while self >= T.LOG_ILI: disjunkcija.append(self.log_I())
        return Log_ILI.ili_samo(disjunkcija)
    
    def log_I(self):
        konjunkcija = [self.log_literal()]
        while self >= T.LOG_I: konjunkcija.append(self.log_literal())
        return Log_I.ili_samo(konjunkcija)
    
    def log_literal(self):
        if self >= T.LOG_NE: return Log_NE(self.log_literal())
        elif self >= T.OTV:
            if self > T.MU: return self.minimizacija(otvorena=True)
            if self > T.CARD: return self.brojeća(otvorena=True)
            izraz = self.izraz()
            self >> T.ZATV
            return izraz
        else: return self.list()
    
    def list(self):
        if ime := self >= T.IME:
            if self > T.OTV:
                return self.poziv(ime)
            return ime
        if self > T.MU: return self.minimizacija(otvorena=False)
        if self > T.CARD: return self.brojeća(otvorena=False)
        if self > T.IF: return self.grananje()
        if self > T.UGOTV: return self.poziv_infix()
        return self >> T.BROJ
    
    def minimizacija(self, otvorena):
        self >> T.MU
        varijabla = self >> T.IME
        if nejednakost := self >= {T.MJEDNAKO, T.MANJE}:
            plus = 1 if nejednakost.sadržaj == '<=' else 0
            ograda = self.list()
            if otvorena: self >> T.ZATV
            relacija = self.izraz()
            return Ograničena_Minimizacija(varijabla, plus, ograda, relacija)
        else:
            if otvorena: self >> T.ZATV
            relacija = self.izraz()
            return Neograničena_Minimizacija(varijabla, relacija)
        
    def brojeća(self, otvorena):
        self >> T.CARD
        varijabla = self >> T.IME
        nejednakost = self >> {T.MJEDNAKO, T.MANJE}
        plus = 1 if nejednakost.sadržaj == '<=' else 0
        ograda = self.list()
        if otvorena: self >> T.ZATV
        relacija = self.izraz()
        return Brojeća(varijabla, plus, ograda, relacija)
    
    def grananje(self):
        self >> T.IF
        self >> T.UGOTV
        uvjeti = [self.izraz()]
        vrijednosti = []
        while not self >= T.UGZATV:
            self >> T.DVOTOČKA
            vrijednosti.append(self.izraz())
            self >> T.ZAREZ
            uvjeti.append(self.izraz())
        return Grananje(uvjeti, vrijednosti)

