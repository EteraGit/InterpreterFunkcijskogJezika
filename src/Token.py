from vepar import *

class T(TipoviTokena):
    FUNCTION_EQUALS, RELATION_EQUALS, AND, OR, LEQ, MU, NEWLINE = ':=', ':<=>', '&&', '||', '<=', 'mu', '\n'
    CARD, OOTV, OZATV, VOTV, VZATV, UGOTV, UGZATV, JEDNAKO, TOČKAZ, PLUS, MINUS, PUTA, DIJELJENO, ZAREZ, MANJE = '#(){}[]=;+-*/,<'

    class BROJ(Token):
        def vrijednost(self, mem, unutar): 
            return int(self.sadržaj)

    class IME(Token):
        def vrijednost(self, mem, unutar): 
            return mem[self]
        
      