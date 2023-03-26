from vepar import *

class Program(AST):
    def __init__(self, commands):
        self.commands = commands

    def izvrši(self):
        globalna = Memorija()
        for command in self.commands:
            command.izvrši(mem=globalna)

class Function(AST):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def pozovi(self, arguments):
        lokalni = Memorija(zip(self.parameters, arguments))
        try:
            self.body.izvrši(mem=lokalni, unutar=self)
        except Povratak as exc:
            return exc.preneseno
        else:
            raise GreškaIzvođenja(f'{self.name} nije ništa vratila')

class Relation(AST):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def pozovi(self, arguments):
        lokalni = Memorija(zip(self.parameters, arguments))

        try:
            self.body.izvrši(mem=lokalni, unutar=self)
        except Povratak as exc:
            return exc.preneseno
        else:
            raise GreškaIzvođenja(f'{self.name} nije ništa vratila')

class CharacteristicFunction(AST):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def pozovi(self, arguments):
        lokalni = Memorija(zip(self.parameters, arguments))

        try:
            self.body.izvrši(mem=lokalni, unutar=self)
        except Povratak as exc:
            return exc.preneseno
        else:
            raise GreškaIzvođenja(f'{self.name} nije ništa vratila')

class Print(AST):
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

    #TODO poziv funkcije ili relacije, zasad krivo
    def pozovi(self, arguments):
        lokalni = Memorija(zip(self.parameters, arguments))

        try:
            self.body.izvrši(mem=lokalni, unutar=self)
        except Povratak as exc:
            return exc.preneseno
        else:
            raise GreškaIzvođenja(f'{self.name} nije ništa vratila')
        
class Add(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def vrijednost(self, mem, unutar):
        return self.left.vrijednost(mem, unutar) + self.right.vrijednost(mem, unutar)

class Expression(AST):
    def __init__(self, terms):
        self.terms = terms
    
    def vrijednost(self, mem, unutar):
        return sum(term.vrijednost(mem, unutar) for term in self.terms)
        
class Integer:
    def __init__(self, value):
        self.value = value
        
    def vrijednost(self, mem, unutar):
        return self.value

class Variable(AST):
    def __init__(self, name):
        self.name = name
        
    def vrijednost(self, mem, unutar):
        return mem[self.name]
    
class Poziv(AST):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
        
    def vrijednost(self, mem, unutar):
        return unutar.funkcije[self.name].pozovi(
            [argument.vrijednost(mem, unutar) for argument in self.arguments]
        )
        
class Return(AST):
    def izvrši(self, mem, unutar):
        raise Povratak(self.što.vrijednost(mem, unutar))
        
class Povratak(NelokalnaKontrolaToka):
    """Signal koji šalje naredba vrati."""
