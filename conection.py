from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

db = create_engine("sqlite:///pdfs.db")
#Abrir sessão
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()

pdf_tag = Table(
    "pdf_tag", Base.metadata,
    Column("pdf_id", Integer, ForeignKey("pdfs.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    valor = Column("valor", String)
    
    def __init__(self, valor):
        self.valor = valor
        
        
class Pdf(Base):
    __tablename__ = "pdfs"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    caminho = Column("caminho", String)
    titulo = Column("titulo", String)
    tags = relationship("Tag", secondary=pdf_tag, backref="pdfs")
    
    def __init__(self, caminho, titulo, tags):
        self.caminho = caminho
        self.titulo = titulo
        self.tags = []
        for valor in tags:
            # procura tag já existente
            tag = session.query(Tag).filter_by(valor=valor).first()
            if not tag:  
                tag = Tag(valor=valor)  # cria nova se não existir
            self.tags.append(tag)  # associa
            
        

Base.metadata.create_all(bind=db)
