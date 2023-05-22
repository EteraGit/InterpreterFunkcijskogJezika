from vepar import *

class T(TipoviTokena):
    FUNCTION_EQUALS, RELATION_EQUALS, AND, OR, LEQ, MU, NEWLINE = ':=', ':<=>', '&&', '||', '<=', 'mu', '\n'
    USK, CARD, OOTV, OZATV, VOTV, VZATV, UGOTV, UGZATV, JEDNAKO, TOČKAZ, PLUS, MINUS, PUTA, DIJELJENO, ZAREZ, MANJE = '!#(){}[]=;+-*/,<'

    class BROJ(Token):
        def vrijednost(self, mem, unutar): 
            return int(self.sadržaj)
        def izvrši(self, mem, unutar):
            return int(self.sadržaj)
        def izvršiStep(self, ime, prev, mem, unutar):
            return int(self.sadržaj)

    class IME(Token):
        def vrijednost(self, mem, unutar): 
            return mem[self]
        def izvrši(self, mem, unutar):
            return mem[self]
        def izvršiStep(self, ime, prev, mem, unutar):
            return mem[self]
        
      