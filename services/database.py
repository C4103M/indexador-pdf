import conection as con
def get_options_turma():
    return con.session.query(con.Turma.nome).all()
    

