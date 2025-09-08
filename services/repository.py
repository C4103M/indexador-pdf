from sqlalchemy.orm import Session
from services.models import Tag, Turma, Pdf
from sqlalchemy import func
class TagRepository:
    def __init__(self, session: Session):
        self.session = session
        
    def find_or_create(self, valor_tag: str) -> Tag:
        """Busca uma tag pelo valor, se não existir, cria uma"""
        tag = self.session.query(Tag).filter_by(valor=valor_tag).first()
        if not tag:
            tag = Tag(valor=valor_tag)
            self.session.add(tag)
        return tag

class TurmaRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def find_by_name(self, nome_turma: str) -> Turma | None:
        """Busca uma turma pelo nome"""
        return self.session.query(Turma).filter_by(nome=nome_turma).first()

    def find_all(self) -> list:
        """Pega todas as turmas"""
        return self.session.query(Turma).order_by(Turma.nome).all()
    
class PdfRepository:
    def __init__(self, session: Session):
        self.session = session
        
        self.tag_repo = TagRepository(session)
        self.turma_repo = TurmaRepository(session)

    def create(self, titulo: str, caminho: str, tags_valores: list[str], turma_nome: str = None) -> Pdf:
        """Cria um novo registro de PDF com suas tags e turma associadas."""
        
        # Cria a instância principal do PDF
        novo_pdf = Pdf(caminho=caminho, titulo=titulo)
        self.session.add(novo_pdf)
        # Processa as tags
        for valor in tags_valores:
            tag_obj = self.tag_repo.find_or_create(valor)
            novo_pdf.tags.append(tag_obj)
        print("foi chamada")
            
        # Processa a turma, se fornecida
        if turma_nome:
            turma_obj = self.turma_repo.find_by_name(turma_nome)
            if turma_obj:
                novo_pdf.turmas.append(turma_obj)
                
        #Adiciona o objeto completo à sessão e commita
        self.session.add(novo_pdf)
        self.session.commit()
        return novo_pdf
    
    def get_total_count(self) -> int:
        """Retorna a contagem total de PDFs no banco."""
        # usa a função COUNT do SQL para ser eficiente
        return self.session.query(func.count(Pdf.id)).scalar()
        
    def find_all(self, page: int = 1, per_page: int = 20) -> list[dict]:
        """
        Busca todos os PDFs de forma paginada.
        :param page: O número da página a ser buscada (começando em 1).
        :param per_page: A quantidade de itens por página.
        """
        # Calcula o 'offset' (quantos itens pular)
        # Para a página 1, o offset é 0. Para a página 2, é 'per_page', e assim por diante.
        offset = (page - 1) * per_page
        pdfs_objetos = self.session.query(Pdf).all()
        
        pdfs_objetos = self.session.query(Pdf).order_by(Pdf.titulo).offset(offset).limit(per_page).all()
        
        # 2. Usa uma list comprehension para chamar .to_dict() em cada objeto
        return [pdf.to_dict() for pdf in pdfs_objetos]

    def find_one(self, caminho_pdf):
        pdf = self.session.query(Pdf).filter_by(caminho = caminho_pdf).first()
        pdf = pdf.to_dict()
        return pdf