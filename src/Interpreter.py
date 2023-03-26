from vepar import *
from AST import *
import pathlib

class T(TipoviTokena):
    FUNCTION_EQUALS, RELATION_EQUALS, AND, OR, LEQ, MU, NEWLINE = ':=', ':<=>', '&&', '||', '<=', 'mu', '\n'
    CARD, OOTV, OZATV, VOTV, VZATV, UGOTV, UGZATV, JEDNAKO, TOČKAZ, PLUS, MINUS, PUTA, DIJELJENO, ZAREZ, MANJE = '#(){}[]=;+-*/,<'

    class BROJ(Token):
        def vrijednost(self, mem, unutar): return int(self.sadržaj)

    class IME(Token):
        def vrijednost(self, mem, unutar): return mem[self]

@lexer
def Lexer(lex):
    for znak in lex:
        if znak == '\n':
            yield lex.token(T.NEWLINE)
        elif znak.isspace():
            lex.zanemari()
        elif znak == '/':
            if lex >= '/':
                lex.pročitaj_do('\n')
                lex.zanemari()
                yield lex.token(T.NEWLINE)
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
                yield lex.token(T.RELATION_EQUALS)
            else:
                lex >> '='
                yield lex.token(T.FUNCTION_EQUALS)
        elif znak.isalpha() or znak == '_':
            lex * {str.isalnum, '_'}
            yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else:
            yield lex.literal(T)

"""
Beskontekstna gramatika:

PROGRAM -> COMMAND | COMMAND PROGRAM

COMMAND -> FUNCTION_DEFINITION | RELATION_DEFINITION | PRINT

FUNCTION_DEFINITION -> FUNCTION_NAME ( VARIABLES ) := EXPRESSION

RELATION_DEFINITION -> RELATION_NAME ( VARIABLES ) :<=> EXPRESSION

VARIABLES -> VARIABLE | VARIABLE, VARIABLES

EXPRESSION -> TERM | TERM + EXPRESSION  // zasad je samo '+' podržan, kako bi se mogao čitati drugi argument u definicijama primitivnih rekurzija

/*
Moguće je kasnije uključiti i operatore +,-,*,/,^,&&,||,... U tom slučaju bi se EXPRESSION granao na PRIBROJNIKE(TERM)
PRIBROJNICI na FAKTORE, FAKTORI NA POTENCIJE itd.
Najniža varijabla u tom grananju (npr. POTENCIJA) bi se onda granala po istom pravilu kao sadašnji TERM:
POTENCIJA -> INTEGER | VARIABLE | MINIMIZE | FUNCTION_CALL | PARENTHESIZED_EXPRESSION

Primjer:
3 * sub(x,y) + add(x,y) ^ 2

- Grana se na 2 PRIBROJNIKA: 3 * sub(x,y) i add(x,y) ^ 2
- 1. PRIBROJNIK se grana na 2 FAKTORA: 3 i sub(x,y)
- Nema znakova ^, pa je svaki FAKTOR ujedno i POTENCIJA
- Sada vrijedi 3 == INTEGER, sub(x,y) == FUNCTION_CALL
...

Naravno, ovakve pokrate sa operatorima implicitno pretpostavljaju da su to sve primitivno rekurzivne operacije.
Moglo bi se pozvati add(x^2 + 5, y) i prije nego što se definira pow na primitivno rekurzivan način, što možda nema teorijskog smisla, ali povećava
opseg izraza koji se mogu interpretirati.
*/

TERM -> INTEGER | VARIABLE | MINIMIZE | FUNCTION_CALL | PARENTHESIZED_EXPRESSION

MINIMIZE -> (MU VARIABLE < EXPRESSION) RELATION_NAME (EXPRESSIONS, VARIABLE)

FUNCTION_CALL -> FUNCTION_NAME ( EXPRESSIONS )

RELATION_CALL -> RELATION_NAME ( EXPRESSIONS )

EXPRESSIONS -> EXPRESSION | EXPRESSION, EXPRESSIONS

PARENTHESIZED_EXPRESSION -> ( EXPRESSION )
"""


class P(Parser):

    def program(self):
        self.funkcije = Memorija(redefinicija=False)
        self.relacije = Memorija(redefinicija=False)
        self.karakteristične_funkcije = Memorija(redefinicija=False)
        self.define_known_functions()
        commands = []
        while not self > KRAJ:
            commands.append(self.command())
        return Program(commands)

    def define_known_functions(self):
        self.funkcije['Z'] = Function('Z', ['x'], Integer(0))
        self.funkcije['I'] = Function('I', ['x'], Variable('x'))
        self.funkcije['Sc'] = Function('Sc', ['x'], Add(Variable('x'), Integer(1)))
        return nenavedeno
    
    def command(self):
        if self > T.IME:
            return self.function()
        elif self > T.VOTV:
            return self.relation()
        elif self > T.UGOTV:
            return self.characteristic_function()
        elif self >= T.NEWLINE:
            return nenavedeno
    
    def function(self):
        self.ime_funkcije = self >> T.IME
        self.parametri_funkcije = self.parameters()
        self >> T.FUNCTION_EQUALS
        tijelo_funkcije = self.expression()
        self >> T.NEWLINE
        if self.ime_funkcije not in self.funkcije:
            self.funkcije[self.ime_funkcije] = Function(self.ime_funkcije, self.parametri_funkcije, tijelo_funkcije)

        return Function(self.ime_funkcije, self.parametri_funkcije, tijelo_funkcije)
    
    def relation(self):
        self >> T.VOTV
        self.ime_relacije = self >> T.IME
        self >> T.VZATV
        self.parametri_relacije = self.parameters()
        self >> T.RELATION_EQUALS
        tijelo_relacije = self.expression()
        self >> T.NEWLINE
        if self.ime_relacije not in self.relacije:
            self.relacije[self.ime_relacije] = Relation(self.ime_relacije, self.parametri_relacije, tijelo_relacije)

        return Relation(self.ime_relacije, self.parametri_relacije, tijelo_relacije)
    
    def characteristic_function(self):
        self >> T.UGOTV
        self.ime_relacije = self >> T.IME
        self >> T.UGZATV
        self.parametri_relacije = self.parameters()
        self >> T.FUNCTION_EQUALS
        tijelo_karakteristične_funkcije = self.expression()
        self >> T.NEWLINE
        if self.ime_relacije not in self.relacije:
            self.relacije[self.ime_relacije] = CharacteristicFunction(self.ime_relacije, self.parametri_relacije, tijelo_karakteristične_funkcije)
        
        return CharacteristicFunction(self.ime_relacije, self.parametri_relacije, tijelo_karakteristične_funkcije)

    #def print(self):
        if self >= T.NEWLINE:
            return Print(nenavedeno, nenavedeno)
        
        ime_izraza = self >> T.IME
        parametri_izraza = self.expressions()
        self >> T.NEWLINE
        
        return Print(ime_izraza, parametri_izraza)
    
    def parameters(self):
        self >> T.OOTV
        if self >= T.OZATV:
            return []
        param = [self.expression()]
        while self >= T.ZAREZ:
            param.append(self.expression())
        self >> T.OZATV
        return param
    
    def expression(self):
        terms = [self.term()]
        while self >= T.PLUS:
            terms.append(self.term())
        return Expression(terms)
    
    def parenthesized_expression(self):
        self >> T.OOTV
        expression = self.expression()
        self >> T.OZATV
        return expression
    
    def term(self):
        if self > T.BROJ:
            return Integer(self >> T.BROJ)
        elif self > T.IME:
            return self.function_call_or_name(self >> T.IME)
        elif self > T.VOTV:
            return self.relation_call()
        elif self > T.OOTV:
            return self.parenthesized_expression()
        else:
            raise self.greška()

    def function_call_or_name(self, ime):
        if ime in self.funkcije:
            funkcija = self.funkcije[ime]
            return Poziv(funkcija, self.parameters())
        elif ime == self.ime_funkcije:
            return Poziv(nenavedeno, self.parameters())
        else:
            return ime
    
    def relation_call(self):
        self >> T.VOTV
        ime_relacije = self >> T.IME
        self >> T.VZATV
        parametri_relacije = self.parameters()
        return Poziv(self.relacije[ime_relacije], parametri_relacije)

s1 = pathlib.Path('Inputs/SampleInput.txt').read_text(encoding='utf-8')

Lexer(s1)

kôd = P(s1)

