from vepar import *
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
def lekser(ulaz):
    for znak in ulaz:
        if znak == '\n':
            yield ulaz.token(T.NEWLINE)
        elif znak.isspace():
            ulaz.zanemari()
        elif znak == '/':
            if ulaz >= '/':
                ulaz.pročitaj_do('\n')
                ulaz.zanemari()
                yield ulaz.token(T.NEWLINE)
            elif ulaz >= '*':
                while ...:
                    ulaz.pročitaj_do('*', više_redova=True)
                    if ulaz >= '/':
                        ulaz.zanemari()
                        break
        elif znak == '<':
            if ulaz >= '=': yield ulaz.token(T.MJEDNAKO)
            else: yield ulaz.token(T.MANJE)
        elif znak == '|':
            ulaz >> '|'
            yield ulaz.token(T.LOG_ILI)
        elif znak == '&':
            ulaz >> '&'
            yield ulaz.token(T.LOG_I)
        elif znak == ':':
            if ulaz >= '=': yield ulaz.token(T.DEF_FUN)
            else: yield ulaz.token(T.DVOTOČKA)
        elif znak.isalpha() or znak == '_':
            ulaz * {str.isalnum, '_'}
            yield ulaz.literal_ili(T.IME)
        elif znak.isdecimal():
            ulaz.prirodni_broj(znak)
            yield ulaz.token(T.BROJ)
        else:
            ulaz * {lambda c: not checkIfLiteral(ulaz.sadržaj, T) and not c.isalnum() and not c.isspace()}
            yield ulaz.literal_ili(T.OP)