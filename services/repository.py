from sqlalchemy.orm import Session
from services.models import Tag, Agrupamento, Pdf
from sqlalchemy import func, or_
from pathlib import Path
from services.config import standard_dir, dir_pdfs
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
    
    def search_by_name(self, search_term: str) -> list[Tag]:
        """
        Busca por tags cujo nome contenha o termo de busca.
        A busca ignora maiúsculas e minúsculas.

        :param search_term: O texto a ser procurado (ex: "finan").
        :return: Uma lista de objetos Tag que correspondem à busca.
        """
        if not search_term:
            return [] # Retorna lista vazia se a busca for vazia

        # Formata o termo de busca para encontrar qualquer tag que contenha o texto
        search_pattern = f"%{search_term}%"
        
        # Executa a query usando .ilike() para uma busca case-insensitive
        return self.session.query(Tag).filter(
            Tag.valor.ilike(search_pattern)
        ).order_by(Tag.valor).all()
    

class AgrupamentoRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def find_by_name(self, nome_agrupamento: str) -> Agrupamento | None:
        """Busca um agrupamento pelo nome"""
        # CORRIGIDO: Query no modelo Agrupamento
        return self.session.query(Agrupamento).filter_by(nome=nome_agrupamento).first()

    def find_all(self) -> list[Agrupamento]:
        """Pega todos os agrupamentos"""
        # CORRIGIDO: Query no modelo Agrupamento
        return self.session.query(Agrupamento).order_by(Agrupamento.nome).all()
    
    def create(self, nome):
        novo_agrupamento = Agrupamento(nome)
        self.session.add(novo_agrupamento)
        self.session.commit()
    
    def delete(self, nome):
        agp = self.find_by_name(nome)
        if agp:
            for pdf in agp.pdfs[:]:  # [:] para copiar a lista e evitar problema durante iteração
                agp.pdfs.remove(pdf)
            self.session.delete(agp)
            self.session.commit()
        
        
class PdfRepository:
    def __init__(self, session: Session):
        self.session = session
        
        self.tag_repo = TagRepository(session)
        self.turma_repo = AgrupamentoRepository(session)
        
    def get_pdf_path(self, filename: str) -> str:
        return str(Path(dir_pdfs) / filename)
    
    def create(self, titulo: str, caminho: str, tags_valores: list[str], agrupamento_nome: str = None) -> Pdf:
        """Cria um novo registro de PDF com suas tags e turma associadas."""
        
        # Cria a instância principal do PDF
        nome_arquivo = Path(caminho).name
        novo_pdf = Pdf(caminho=nome_arquivo, titulo=titulo)
        self.session.add(novo_pdf)
        # Processa as tags
        for valor in tags_valores:
            tag_obj = self.tag_repo.find_or_create(valor)
            novo_pdf.tags.append(tag_obj)
        # print("foi chamada")
            
        # Processa a turma, se fornecida
        if agrupamento_nome:
            agrupamento_obj = self.agrupamento_repo.find_by_name(agrupamento_nome)
            if agrupamento_obj:
                novo_pdf.agrupamentos.append(agrupamento_obj)
                
        #Adiciona o objeto completo à sessão e commita
        self.session.add(novo_pdf)
        self.session.commit()
        return novo_pdf
    
    def update(self, pdf_id, novo_titulo: str, novas_tags: list[str], novo_agrupamento):
        pdf = self.session.get(Pdf, pdf_id)
        if not pdf:
            raise ValueError(f"PDF com id {pdf_id} não encontrado.")
        if novo_titulo:
            pdf.titulo = novo_titulo

        if novas_tags is not None:
            # Limpa as tags atuais
            pdf.tags.clear()
            # Adiciona as novas tags
            for valor in novas_tags:
                tag_obj = self.tag_repo.find_or_create(valor)
                pdf.tags.append(tag_obj)
                
        if novo_agrupamento is not None:
            pdf.agrupamentos.clear()  # limpa agrupamentos antigos
            agrupamento_obj = self.agrupamento_repo.find_by_name(novo_agrupamento)
            if agrupamento_obj:
                pdf.agrupamentos.append(agrupamento_obj)
        # 5️⃣ Commit das alterações
        self.session.commit()
    
    def delete(self, pdf_id):
        pdf = self.session.get(Pdf, pdf_id)
        if pdf:
            self.session.delete(pdf)
            self.session.commit()

            # Apaga tags sem PDFs
            self.session.query(Tag).filter(~Tag.pdfs.any()).delete(synchronize_session=False)
            self.session.commit()
    
    def get_total_count(self) -> int:
        """Retorna a contagem total de PDFs no banco."""
        # usa a função COUNT do SQL para ser eficiente
        return self.session.query(func.count(Pdf.id)).scalar()
        
    def find_all(self, page: int = 1, per_page: int = 20) -> list[dict]:
        """
        Busca todos os PDFs de forma paginada.
        """
        offset = (page - 1) * per_page
        
        # CORRIGIDO: Removida a linha duplicada e desnecessária
        pdfs_objetos = self.session.query(Pdf).order_by(Pdf.titulo).offset(offset).limit(per_page).all()
        
        return [pdf.to_dict() for pdf in pdfs_objetos]

    def find_one(self, caminho_pdf) -> dict | None:
        # print(">>> DEBUG find_one - caminho_pdf:", caminho_pdf, type(caminho_pdf))
        query = self.session.query(Pdf).filter_by(caminho = caminho_pdf)
        # print(">>> DEBUG SQL:", str(query))
        pdf = query.first()
        
        if pdf:
            d = pdf.to_dict()
            d["caminho"] = self.get_pdf_path(d["caminho"])
            return d
        return None
    
    def find_by_id(self, pdf_id) -> dict | None:
        # print(">>> DEBUG find_one - caminho_pdf:", caminho_pdf, type(caminho_pdf))
        query = self.session.query(Pdf).filter_by(id = pdf_id)
        # print(">>> DEBUG SQL:", str(query))
        pdf = query.first()
        
        if pdf:
            d = pdf.to_dict()
            d["caminho"] = self.get_pdf_path(d["caminho"])
            return d
        return None
    
    def search_by_term(self, search_term: str) -> list[Pdf]:
        """
        Busca por PDFs que estejam associados a tags que contenham o termo de busca.
        Retorna uma lista de objetos Pdf.

        :param search_term: O texto a ser procurado nas tags (ex: "certificado").
        :return: Uma lista de objetos Pdf únicos que correspondem à busca.
        """
        if not search_term:
            return []
        
        search_pattern = f"%{search_term}%"

        # Busca os objetos Pdf completos que correspondem aos critérios
        pdfs_encontrados = self.session.query(Pdf).filter(
            or_(
                Pdf.titulo.ilike(search_pattern),
                # Usa .any() para verificar a existência de tags correspondentes.
                # É mais limpo e muitas vezes mais eficiente que um JOIN explícito.
                Pdf.tags.any(Tag.valor.ilike(search_pattern))
            )
        ).distinct().all()
        
        # Extrai apenas os caminhos dos objetos Pdf encontrados
        return [pdf.caminho for pdf in pdfs_encontrados]