import conection
# import tela
pdf = conection.Pdf(
    caminho="caminho/arquivo.pdf",
    titulo="Aula 01",
    tags=["importante", "exercícios"],
    turmas=["3A", "3B"]
)
conection.session.add(pdf)
conection.session.commit()
