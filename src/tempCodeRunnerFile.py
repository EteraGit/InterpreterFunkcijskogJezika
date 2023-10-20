    naredbe = []
    for linija in ulaz:
        if ':=' in linija: P.start = P.definicija 
        elif linija == '\n': continue
        else: P.start = P.evaluacija_izraza
        naredbe.append(P(linija))
    ast = Program(naredbe)
    ast.izvrši()