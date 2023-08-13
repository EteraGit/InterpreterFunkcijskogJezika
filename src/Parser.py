from vepar import *
from AST import *
from Token import *

def checkIfLiteral(string, cls):
    for enum_var in cls:
        if str(string[-1]) == enum_var.value:
            return True
    string = string[:-1]
    for enum_var in cls:
        if string == enum_var.value:
            return True
    return False

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
                while True:
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
            elif lex >= '=':
                yield lex.token(T.FUNCTION_EQUALS)
            else:
                yield lex.token(T.DVOTOČKA)
        elif znak.isalpha() or znak == '_':
            lex * {str.isalnum, '_'}
            yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else:
            lex * {lambda c: not checkIfLiteral(lex.sadržaj, T) and not c.isalnum() and not c.isspace()}
            yield lex.literal_ili(T.OP)

"""
Beskontekstna gramatika:

program -> command | command program

command -> function_definition | infix_definition

function_definition -> IME ( left_parameters ) = expression | IME ( left_parameters ) = left_parameter | Call(IME, right_parameters)

infix_definition -> [left_parameter OP left_parameter] = expression | Call(right_parameter, OP, right_parameter)

left_parameters -> left_parameter | left_parameter , left_parameters

left_parameter -> IME | BROJ | Call(IME, left_parameters)

right_parameters -> right_parameter | right_parameter , right_parameters

right_parameter -> expression

expression -> logical_or

logical_or -> logical_and | logical_and || logical_or

logical_and -> literal | literal && logical_and

literal -> ! literal | (minimize) | (cardinality) | (expression) | term

term -> IME | BROJ | Call(IME, right_parameters) | minimize | cardinality

minimize -> MU (< or <=) term expression | (MU (< or <=) term) expression

cardinality -> CARD (< or <=) term expression | (CARD (< or <=) term) expression
"""


class P(Parser):

    def program(self):
        self.funkcije = Memorija(redefinicija=True)
        self.define_known_functions()
        commands = []
        while not self > KRAJ:
            commands.append(self.command())
        return Program(commands, self.funkcije)

    def define_known_functions(self):
        self.funkcije['Z'] = PythonFunction(Token(T.IME, 'Z'), [Token(T.IME, 'x')], lambda x: 0)
        self.funkcije['Sc'] = PythonFunction(Token(T.IME, 'Sc'), [Token(T.IME, 'x')], lambda x: x + 1)
        self.funkcije['I'] = PythonFunction(Token(T.IME, 'I'), [Token(T.IME, 'x')], lambda x: x)
        return nenavedeno

    def command(self):
        if self >= T.NEWLINE:
            return nenavedeno
        elif self > T.UGOTV:
            return self.infix_definition()
        else:
            return self.function_definition()
        
    def infix_definition(self):
        self >> T.UGOTV
        prvi, drugi, operator, izraz = None, None, None, None
        if ime := self >= T.IME:            # ako smo procitali ime, onda su 2 slucaja
            if ime not in self.funkcije:    # ako smo procitali varijablu, onda je to definicija infix funkcije
                prvi = self.left_function_call_or_name(ime)
                operator = self >> T.OP
                drugi = self.left_parameter()
                self >> T.UGZATV
                self >> {T.FUNCTION_EQUALS, T.JEDNAKO}
                izraz = self.right_parameter()
            else:                           # ako smo procitali funkciju, onda je to poziv infix funkcije           
                prvi = self.right_function_call_or_name(ime)
                operator = self >> T.OP
                drugi = self.right_parameter()
        else:                               # ako nismo procitali ime, onda je to poziv infix funkcije
            prvi = self.right_parameter()
            operator = self >> T.OP
            drugi = self.right_parameter()
        if izraz is None:                   # u svakom slucaju osim definicije infix funkcije
            self >> T.UGZATV
            if self >= T.NEWLINE:
                return Call(operator, [prvi, drugi])
            self >> {T.FUNCTION_EQUALS, T.JEDNAKO}
            izraz = self.expression()
        self >> T.NEWLINE

        if isinstance(drugi, Token) and drugi.sadržaj == '0':
            baseIme = Token(T.IME, operator.sadržaj + baseString)
            if baseIme not in self.funkcije:
                function = Function(baseIme, [prvi, drugi], izraz)
                self.funkcije[baseIme] = function
                return function
        elif isinstance(drugi, Call) and drugi.ime.sadržaj == 'Sc':
            stepIme = Token(T.IME, operator.sadržaj + stepString)
            if stepIme not in self.funkcije:
                parametri = [prvi, drugi]
                self.funkcije[operator] = Function(operator, parametri, izraz)
                parametri.append(Token(T.IME, '#prev'))
                function = Function(stepIme, parametri, izraz)
                self.funkcije[stepIme] = function
                return function
        infix = Function(operator, [prvi, drugi], izraz)
        self.funkcije[operator] = infix
        return infix
    
    def function_definition(self):
        ime = 'default'
        if self >= T.VOTV:
            ime = self >> T.IME
            self >> T.VZATV
        else:
            ime = self >> T.IME  
        if ime in self.funkcije:
            parametri = self.right_parameters()
            call = Call(ime, parametri)
            self >> T.NEWLINE
            return call
        parametri = self.left_parameters()
        self >> {T.FUNCTION_EQUALS, T.RELATION_EQUALS, T.JEDNAKO}
        izraz = self.right_parameter()
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
    
    def left_parameters(self):
        self >> T.OOTV
        if self >= T.OZATV:
            return []
        parametri = [self.left_parameter()]
        while self >= T.ZAREZ:
            parametri.append(self.left_parameter())
        self >> T.OZATV
        return parametri

    def left_parameter(self):
        if ime := self >= T.IME:
            return self.left_function_call_or_name(ime)
        elif broj := self >= T.BROJ:
            return broj
        elif self >= T.UGOTV:
            prvi = self.left_parameter()
            operator = self >> T.OP
            drugi = self.left_parameter()
            self >> T.UGZATV
            return Call(operator, [prvi, drugi])
        else:
            return nenavedeno
        
    def right_parameters(self):
        self >> T.OOTV
        if self >= T.OZATV:
            return []
        parametri = [self.right_parameter()]
        while self >= T.ZAREZ:
            parametri.append(self.right_parameter())
        self >> T.OZATV
        return parametri
        
    def right_parameter(self):
        return self.expression()  
        
    def expression(self):
        return self.logical_OR()
    
    def logical_OR(self):
        ands = [self.logical_AND()]
        while self >= T.OR:
            ands.append(self.logical_AND())
        return Logical_OR.ili_samo(ands)
    
    def logical_AND(self):
        literali = [self.literal()]
        while self >= T.AND:
            literali.append(self.literal())
        return Logical_AND.ili_samo(literali)
          
    def literal(self):
        if self >= T.USK:
            literal = Logical_NOT(self.literal())
            return literal
        elif self >= T.OOTV:
            if self > T.MU:
                return self.minimize(True)
            elif self > T.CARD:
                return self.cardinality(True)
            logical_or = self.expression()
            self >> T.OZATV
            return logical_or
        else:
            return self.term()
    
    def term(self):
        if ime := self >= T.IME:
            return self.right_function_call_or_name(ime)
        elif broj := self >= T.BROJ:
            return broj
        elif self >= T.UGOTV:
            prvi = self.expression()
            operator = self >> T.OP
            drugi = self.expression()
            self >> T.UGZATV
            return Call(operator, [prvi, drugi])
        elif self > T.IF:
            return self.branch()
        elif self > T.MU:
            return self.minimize(False)
        elif self > T.CARD:
            return self.cardinality(False)
        else:
            return nenavedeno
        
    def left_function_call_or_name(self, ime):
        if self > T.OOTV:
            argumenti = self.left_parameters()
            return Call(ime, argumenti)
        else:
            return ime
        
    def right_function_call_or_name(self, ime):
        if self > T.OOTV:
            argumenti = self.right_parameters()
            return Call(ime, argumenti)
        else:
            return ime
        
    def branch(self):
        self >> T.IF
        self >> T.VOTV
        uvjeti = [self.expression()]
        vrijednosti = []
        while not self > T.VZATV:
            self >> T.DVOTOČKA
            vrijednosti.append(self.expression())
            self >> T.ZAREZ
            uvjeti.append(self.expression())
        self >> T.VZATV
        return Branch(uvjeti, vrijednosti)

        
    def minimize(self, otvorena):
        self >> T.MU
        min_var = self >> T.IME
        inequality = None
        bound = None
        if inequality := self >= {T.MANJE, T.LEQ}:
            bound = self.term()
        if otvorena:
            self >> T.OZATV
        relacija = self.expression()
        return Minimize(min_var, inequality, bound, relacija)
    
    def cardinality(self, otvorena):
        self >> T.CARD
        card_var = self >> T.IME
        inequality = self >> {T.MANJE, T.LEQ}
        bound = self.term()
        if otvorena:
            self >> T.OZATV
        relacija = self.expression()
        return Cardinality(card_var, inequality, bound, relacija)


