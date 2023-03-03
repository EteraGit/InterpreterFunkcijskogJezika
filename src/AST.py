from vepar import *

class Program(AST):

    def __init__(self, commands):
        self.commands = commands

    def izvrši(self):
        rt.mem = Memorija()
        for command in self.commands:
            command.izvrši(rt.mem, self.funkcije)

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
        
class Return(AST):

    def izvrši(self, mem, unutar):
        raise Povratak(self.što.vrijednost(mem, unutar))
        
class Povratak(NelokalnaKontrolaToka):
    """Signal koji šalje naredba vrati."""
