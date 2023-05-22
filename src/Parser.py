from vepar import *
from AST import *
from Token import *

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
        self.funkcije['Z'] = PythonFunction(Token(T.IME, 'Z'), [Token(T.IME, 'x')], lambda x: 0)
        self.funkcije['Sc'] = PythonFunction(Token(T.IME, 'Sc'), [Token(T.IME, 'x')], lambda x: x + 1)
        self.funkcije['I'] = PythonFunction(Token(T.IME, 'I'), [Token(T.IME, 'x')], lambda x: x)
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

        if isinstance(parametri[-1], Token) and parametri[-1].sadržaj == '0':
            baseIme = Token(T.IME, ime.sadržaj + baseString)
            if baseIme not in self.funkcije:
                function = Function(baseIme, parametri, izraz)
                self.funkcije[baseIme] = function
                return function
        elif isinstance(parametri[-1], Call) and parametri[-1].ime.sadržaj == 'Sc':
            stepIme = Token(T.IME, ime.sadržaj + stepString)
            if stepIme not in self.funkcije:
                self.funkcije[ime] = Function(ime, parametri, izraz)
                parametri.append(Token(T.IME, '#prev'))
                function = Function(stepIme, parametri, izraz)
                self.funkcije[stepIme] = function
                return function
        function = Function(ime, parametri, izraz)
        self.funkcije[ime] = function
        return function
    
    def characteristic_function_definition(self):
        self >> T.UGOTV
        ime = self >> T.IME
        self >> T.UGZATV
        parametri = self.parameters()
        if self >= T.NEWLINE:
            return Call(ime, parametri)
        self >> T.FUNCTION_EQUALS
        izraz = self.expression()
        self >> T.NEWLINE

        if isinstance(parametri[-1], Token) and parametri[-1].sadržaj == '0':
            baseIme = Token(T.IME, ime.sadržaj + baseString)
            if baseIme not in self.funkcije:
                function = Function(baseIme, parametri, izraz)
                self.funkcije[baseIme] = function
                return function
        elif isinstance(parametri[-1], Call) and parametri[-1].ime.sadržaj == 'Sc':
            stepIme = Token(T.IME, ime.sadržaj + stepString)
            if stepIme not in self.funkcije:
                self.funkcije[ime] = Function(ime, parametri, izraz)
                parametri.append(Token(T.IME, '#prev'))
                function = Function(stepIme, parametri, izraz)
                self.funkcije[stepIme] = function
                return function
        function = Function(ime, parametri, izraz)
        self.funkcije[ime] = function
        return function
    
    def relation_definition(self):
        self >> T.VOTV
        ime = self >> T.IME
        self >> T.VZATV
        parametri = self.parameters()
        if self >= T.NEWLINE:
            return Call(ime, parametri)
        self >> T.RELATION_EQUALS
        izraz = self.expression()
        self >> T.NEWLINE

        if isinstance(parametri[-1], Token) and parametri[-1].sadržaj == '0':
            baseIme = Token(T.IME, ime.sadržaj + baseString)
            if baseIme not in self.funkcije:
                function = Function(baseIme, parametri, izraz)
                self.funkcije[baseIme] = function
                return function
        elif isinstance(parametri[-1], Call) and parametri[-1].ime.sadržaj == 'Sc':
            stepIme = Token(T.IME, ime.sadržaj + stepString)
            if stepIme not in self.funkcije:
                self.funkcije[ime] = Function(ime, parametri, izraz)
                parametri.append(Token(T.IME, '#prev'))
                function = Function(stepIme, parametri, izraz)
                self.funkcije[stepIme] = function
                return function
        function = Function(ime, parametri, izraz)
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
                return nenavedeno
        else:
            return self >> T.BROJ
        
    def expression(self):
        logic = []
        istinitost = 'aff'
        if self >= T.USK:
            istinitost = 'neg'
        terms = [Literal(istinitost, self.term())]
        while l := self >= {T.AND, T.OR}:
            if l.sadržaj == '&&':
                logic.append('and')
            elif l.sadržaj == '||':
                logic.append('or')
            istinitost = 'aff'
            if self >= T.USK:
                istinitost = 'neg'
            terms.append(Literal(istinitost, self.term()))
        if len(logic) == 0 and istinitost == 'aff':
            return terms[0].term
        return Logic(terms, logic)
    
    def term(self):
        if self >= T.OOTV:
            if self > T.MU:
                return self.minimize(parentheses = True)
            elif self > T.CARD:
                return self.cardinality(parentheses = True)
            izraz = self.expression()
            self >> T.OZATV
            return izraz
        elif ime := self >= T.IME:
            return self.function_call_or_name(ime)
        elif broj := self >= T.BROJ:
            return Integer(int(broj.sadržaj))
        elif self > T.MU:
            return self.minimize(parentheses = False)
        elif self > T.CARD:
            return self.cardinality(parentheses = False)
        elif self > T.VOTV:
            return self.relation_call()
        else:
            return nenavedeno
        
    def function_call_or_name(self, ime):
        if self > T.OOTV:
            argumenti = self.arguments()
            return Call(ime, argumenti)
        else:
            return Variable(ime)
        
    def minimize(self, parentheses):
        self >> T.MU
        min_var = self >> T.IME
        if parentheses:
            self >> T.OZATV
        if self > T.OOTV:
            return self.minimize_relations(min_var)
        self >> T.VOTV
        relacija = self >> T.IME
        self >> T.VZATV
        argumenti = self.arguments()
        return Minimize(min_var, relacija, argumenti)
    
    def cardinality(self, parentheses):
        self >> T.CARD
        card_var = self >> T.IME
        inequality = self >> {T.MANJE, T.LEQ}
        bound = self.expression()
        if parentheses:
            self >> T.OZATV
        self >> T.VOTV
        relacija = self >> T.IME
        self >> T.VZATV
        argumenti = self.arguments()
        return Cardinality(card_var, inequality, bound, relacija, argumenti)
    
    def minimize_relations(self, min_var):
        logic = []
        self >> T.OOTV
        self >> T.VOTV
        relacije = [self >> T.IME]
        self >> T.VZATV
        argumenti = [self.arguments()]
        while l := self >= {T.AND, T.OR}:
            if l.sadržaj == '&&':
                logic.append('and')
            elif l.sadržaj == '||':
                logic.append('or')
            self >> T.VOTV
            relacije.append(self >> T.IME)
            self >> T.VZATV
            argumenti.append(self.arguments())
        self >> T.OZATV
        return MinimizeRelations(min_var, relacije, argumenti, logic)
        
    def relation_call(self):
        self >> T.VOTV
        ime = self >> T.IME
        self >> T.VZATV
        argumenti = self.arguments()
        return Call(ime, argumenti)

    def arguments(self):
        self >> T.OOTV
        if self >= T.OZATV:
            return []
        argumenti = [self.expression()]
        while self >= T.ZAREZ:
            argumenti.append(self.expression())
        self >> T.OZATV
        return argumenti


