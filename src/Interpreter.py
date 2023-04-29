from vepar import *
from AST import *
from Token import *
import pathlib
import sys

sys.setrecursionlimit(10000)

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
            elif lex >= '*':
                while 1:
                    lex.pročitaj_do('*', više_redova=True)
                    if lex >= '/':
                        lex.zanemari()
                        break
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
        self.funkcije = Memorija(redefinicija=True)
        self.relacije = Memorija(redefinicija=False)
        self.karakteristične_funkcije = Memorija(redefinicija=False)
        self.define_known_functions()
        commands = []
        while not self > KRAJ:
            commands.append(self.command())
        return Program(commands, self.funkcije, self.relacije, self.karakteristične_funkcije)

    def define_known_functions(self):
        self.funkcije['Z'] = Function(Token(T.IME, 'Z'), [Token(T.IME, 'x')], Integer(0))
        self.funkcije['Sc'] = Function(Token(T.IME, 'Sc'), [Token(T.IME, 'x')], Add([Variable('x'), Integer(1)]))
        self.funkcije['I'] = Function(Token(T.IME, 'I'), [Token(T.IME, 'x')], Variable('x'))
        return nenavedeno

    def command(self):
        if self > T.IME:
            return self.function_definition()
        elif self > T.UGOTV:
            return self.characteristic_function_definition()
        elif self > T.VOTV:
            return self.relation_definition()
        else:
            self >> T.NEWLINE
            return nenavedeno
        
    def function_definition(self):
        ime = self >> T.IME
        parametri = self.parameters()
        if self >= T.NEWLINE:
            return Call(ime, parametri)
        self >> T.FUNCTION_EQUALS
        izraz = self.expression()
        self >> T.NEWLINE

        function = Function(ime, parametri, izraz)
        if parametri[-1].sadržaj == '0':
            defaultIme = Token(T.IME, ime.sadržaj + defaultString)
            if defaultIme not in self.funkcije:
                function = Function(defaultIme, parametri, izraz)
                self.funkcije[defaultIme] = function
                return function
        self.funkcije[ime] = function
        return function
    
    def parameters(self):
        self >> T.OOTV
        if self >= T.OZATV:
            return []
        parametri = [self.parameter()]
        while self >= T.ZAREZ:
            parametri.append(self.parameter())
        self >> T.OZATV
        return parametri

    def parameter(self):
        if ime := self >= T.IME:
            if self > T.ZAREZ or self > T.OZATV:
                return ime
            elif self > T.OOTV:
                unutarnji = self.parameters()
                return Call(ime, unutarnji)
            else:
                self >> T.PLUS
                broj = self >> T.BROJ
                if int(broj.sadržaj) != 1:
                    raise SintaksnaGreška('Zadnji argument funkcijskog parametra mora biti oblika (varijabla + 1)')
                return Token(T.IME, ime.sadržaj + '+1')
        else:
            return self >> T.BROJ
        
    def expression(self):
        return self.term()
    """
        izraz = [self.term()]
        while self >= T.PLUS:
            izraz.append(self.term())
        return Add(izraz)
    """
    
    def term(self):
        if self >= T.OOTV:
            izraz = self.expression()
            self >> T.OZATV
            return izraz
        elif ime := self >= T.IME:
            return self.function_call_or_name(ime)
        elif broj := self >= T.BROJ:
            return Integer(int(broj.sadržaj))
        elif self >= T.MU:
            return self.minimize()
        elif self >= T.VOTV:
            return self.relation_call()
        else:
            return nenavedeno
        
    def function_call_or_name(self, ime):
        if self > T.OOTV:
            argumenti = self.arguments()
            return Call(ime, argumenti)
        else:
            return Variable(ime.sadržaj)
    
    def arguments(self):
        self >> T.OOTV
        if self >= T.OZATV:
            return []
        argumenti = [self.expression()]
        while self >= T.ZAREZ:
            argumenti.append(self.expression())
        self >> T.OZATV
        return argumenti

            
s1 = pathlib.Path('Inputs/SampleInput.txt').read_text(encoding='utf-8')

Lexer(s1)

kôd = P(s1)

prikaz(kôd)

kôd.izvrši()

