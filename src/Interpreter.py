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
        commands = []
        while not self > KRAJ:
            commands.append(self.command())
        return Program(commands)
    
    def command(self):
        counter = 0
        while True:
            if self > T.FUNCTION_EQUALS:
                for index in range(counter): self.vrati()
                return self.function_definition()
            elif self > T.RELATION_EQUALS:
                for index in range(counter): self.vrati()
                return self.relation_definition()
            elif self > T.NEWLINE:
                for index in range(counter): self.vrati()
                return self.print()
            else:
                self.čitaj()
            counter += 1
    
    def function_definition(self):
        ime_funkcije = self >> T.IME
        parametri_funkcije = self.variables()
        self >> T.FUNCTION_EQUALS
        tijelo_funkcije = self.expression()
        self >> T.NEWLINE

        return Function(ime_funkcije, parametri_funkcije, tijelo_funkcije)
    
    def relation_definition(self):
        ime_relacije = self >> T.IME
        parametri_relacije = self.variables()
        self >> T.RELATION_EQUALS
        tijelo_relacije = self.expression()
        self >> T.NEWLINE

        return Relation(ime_relacije, parametri_relacije, tijelo_relacije)
    
    def print(self):
        ime_izraza = self >> T.IME
        parametri_izraza = self.expressions()
        self >> T.NEWLINE
        
        return Print(ime_izraza, parametri_izraza)

s1 = pathlib.Path('Inputs/SampleInput.txt').read_text(encoding='utf-8')

Lexer(s1)

