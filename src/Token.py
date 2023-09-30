from vepar import *

class T(TipoviTokena):
    DEF_FUN, NEWLINE, LOG_ILI, LOG_I, MU, IF, MJEDNAKO = ':=', '\n', '||', '&&', 'mu', 'if', '<='
    OTV, ZATV, ZAREZ, LOG_NE, CARD, MANJE, VOTV, VZATV, UGOTV, UGZATV, DVOTOČKA = '(),!#<{}[]:'
    class IME(Token):
        def izvrši(self, memorija, funkcije):
            return memorija[self]
    class BROJ(Token):
        def izvrši(self, memorija, funkcije):
            return int(self.sadržaj)
    class OP(Token):
        def izvrši(self, memorija, funkcije):
            return str(self.sadržaj)