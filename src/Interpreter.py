from vepar import *

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

s1 = '''
    add(x,0):=x
    add(x,y+1):=sc(add(x,y))
    # zasad zakomentirano (x+y) ::= add(x,y)   # nice to have
    
    f(x,y):=add(sc(sc(x)),y)   # opcionalno: +, *,...
    
    [Positive](0):=0
    [Positive](x+1):=1
    
    Greater(x,y):<=>Positive(sub(x,y))  # ići u: [Greater](x,y):=[Positive](sub(x,y))
    div(x,y):=pd((mu z)Greater(mul(z,y),x))
    
    mod(x,y):=sub(x,mul(y,div(x,y)))   # (x-(y*(x//y)))
    
    Divides(x,y):<=>Equal(mod(x,y),Z(x))  # moze i Equal(mod(x,y),0)
    Prime(p):<=>Equal((#d<=p)Divides(d,p), 2)
    
    factorial(0):=1
    factorial(n+1):=mul(sc(n),factorial(n))

    nextprime(p):=(mu q<=sc(factorial(p)))(Prime(q) && Greater(q,p))  # eventualno AND(...)
    
    # Ograničeno: (keyword x <(=) izraz)relacija
    '''

Lexer(s1)