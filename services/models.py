from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

pdf_tag = Table(
    "pdf_tag", Base.metadata,
    Column("pdf_id", Integer, ForeignKey("pdfs.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)
pdf_turma = Table(
    "pdf_turma", Base.metadata,
    Column("pdf_id", Integer, ForeignKey("pdfs.id"), primary_key=True),
    Column("turma_id", Integer, ForeignKey("turmas.id"), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    valor = Column("valor", String)
    
    def __init__(self, valor):
        self.valor = valor

class Turma(Base):
    __tablename__ = "turmas"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    
    def __init__(self, nome):
        self.nome = nome

        
class Pdf(Base):
    __tablename__ = "pdfs"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    caminho = Column("caminho", String)
    titulo = Column("titulo", String)
    data_inclusao = Column("data_inclusao", DateTime(timezone=True), server_default=func.now())
    # Relações N:N
    tags = relationship("Tag", secondary=pdf_tag, backref="pdfs")
    turmas = relationship("Turma", secondary=pdf_turma, backref="pdfs")
    
    def __init__(self, caminho, titulo, tags=None, turmas=None):
        self.caminho = caminho
        self.titulo = titulo
        
    def to_dict(self) -> dict:
        """Converte o objeto Pdf em um dicionário."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "caminho": self.caminho,
            # Converte a lista de objetos Tag em uma lista de strings (nomes das tags)
            "tags": [tag.valor for tag in self.tags if tag],
            # Converte a lista de objetos Turma em uma lista de strings (nomes das turmas)
            "turmas": [turma.nome for turma in self.turmas],
            "data_inclusao": self.data_inclusao
        }
        # # Turmas
        # self.tags = []
        # if tags:
        #     for valor in tags:
        #         # procura tag já existente
        #         tag = session.query(Tag).filter_by(valor=valor).first()
        #         if not tag:  
        #             tag = Tag(valor=valor)  # cria nova se não existir
        #         self.tags.append(tag)  # associa
                
        # # Turmas
        # self.turmas = []
        # if turmas:
        #     for nome in turmas:
        #         turma = session.query(Turma).filter_by(nome=nome).first()
        #         if not turma:
        #             turma = Turma(nome=nome)
        #         self.turmas.append(turma)
                
    
        