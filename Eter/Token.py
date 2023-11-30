from vepar import *

class T(TipoviTokena):
    DEF_FUN, LOG_ILI, LOG_I, MU, IF, MJEDNAKO = ':=', '||', '&&', 'mu', 'if', '<='
    OTV, ZATV, ZAREZ, LOG_NE, CARD, MANJE, VOTV, VZATV, UGOTV, UGZATV, DVOTOČKA = '(),!#<{}[]:'
    class IME(Token):
        def izvrši(self, memorija, funkcije):
            return memorija[self]
        def stablo(self):
            self.pomime = self.sadržaj
            self.djeca = []
    class BROJ(Token):
        def izvrši(self, memorija, funkcije):
            return int(self.sadržaj)
        def stablo(self):
            self.pomime = self.sadržaj
            self.djeca = []
    class OP(Token):
        def izvrši(self, memorija, funkcije):
            return str(self.sadržaj)