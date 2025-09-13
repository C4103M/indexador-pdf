from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

# Tabela de associação para a relação N:N entre Pdf e Tag
pdf_tag = Table(
    "pdf_tag", Base.metadata,
    Column("pdf_id", Integer, ForeignKey("pdfs.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, nullable=False)
)

# Tabela de associação para a relação N:N entre Pdf e Agrupamento
# CORRIGIDO: Nomes em minúsculas e ForeignKey apontando para "agrupamentos.id"
pdf_agrupamento = Table(
    "pdf_agrupamento", Base.metadata,
    Column("pdf_id", Integer, ForeignKey("pdfs.id", ondelete="CASCADE"), primary_key=True),
    Column("agrupamento_id", Integer, ForeignKey("agrupamentos.id"), primary_key=True, nullable=False)
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    valor = Column("valor", String, unique=True)
    
    def __init__(self, valor):
        self.valor = valor

class Agrupamento(Base):
    __tablename__ = "agrupamentos" # Nome da tabela no plural
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, unique=True)
    
    def __init__(self, nome):
        self.nome = nome

class Pdf(Base):
    __tablename__ = "pdfs"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    caminho = Column("caminho", String, unique=True)
    titulo = Column("titulo", String)
    data_inclusao = Column(DateTime, server_default=func.now())
    
    # Relações N:N
    tags = relationship("Tag", secondary=pdf_tag, backref="pdfs")
    # CORRIGIDO: Relação atualizada para usar os nomes corretos
    agrupamentos = relationship(
        "Agrupamento",
        secondary=pdf_agrupamento,
        backref="pdfs",
        cascade="all, delete"
    )
    
    def __init__(self, caminho, titulo):
        self.caminho = caminho
        self.titulo = titulo
        
    def to_dict(self) -> dict:
        """Converte o objeto Pdf em um dicionário."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "caminho": self.caminho,
            "tags": [tag.valor for tag in self.tags if tag],
            # CORRIGIDO: Chave no plural e lógica da list comprehension
            "agrupamentos": [agrupamento.nome for agrupamento in self.agrupamentos if agrupamento],
            "data_inclusao": self.data_inclusao.isoformat() if self.data_inclusao else None
        }
