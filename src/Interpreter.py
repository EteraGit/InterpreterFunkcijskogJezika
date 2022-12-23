from vepar import *
import pathlib

class T(TipoviTokena):
    DEFINEFUNC, DEFINEREL, AND, OR, LEQ, MU, SC = ':=', ':<=>', '&&', '||', '<=', 'mu', 'sc'
    OOTV, OZATV, VOTV, VZATV, UGOTV, UGZATV, JEDNAKO, TOČKAZ, PLUS, MINUS, PUTA, DIJELJENO, ZAREZ, MANJE, ZERO = '(){}[]=;+-*/,<Z'

    class BROJ(Token):
        def vrijednost(self, mem, unutar): return int(self.sadržaj)

    class IME(Token):
        def vrijednost(self, mem, unutar): return mem[self]

@lexer
def Lexer(lex):
    for znak in lex:
        if znak.isspace():
            lex.zanemari()
        elif znak == '#':
            lex.pročitaj_do('\n')
            lex.zanemari()
        elif znak == '&':
            lex >> '&'
            yield lex.token(T.AND)
        elif znak == '|':
            lex >> '|'
            yield lex.token(T.OR)
        elif znak == '<':
            yield lex.token(T.LEQ if lex >= '=' else T.MANJE)
        elif znak == ':':
            if lex >= '<':
                lex >> '='
                lex >> '>'
                yield lex.token(T.DEFINEREL)
            else:
                lex >> '='
                yield lex.token(T.DEFINEFUNC)
        elif znak.isalpha() or znak == '_':
            lex * {str.isalnum, '_'}
            yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else:
            yield lex.literal(T)

s1 = pathlib.Path('Inputs/SampleInput.txt').read_text(encoding='utf-8')

Lexer(s1)