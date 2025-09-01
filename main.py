import conection
import tela
pdf = conection.Pdf(caminho="./pdfs/pdf1.pdf", titulo="titulo1", tags=["tag1", "tag2", "tag3"])
conection.session.add(pdf)
conection.session.commit()
