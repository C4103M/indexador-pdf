from flet import *
from sqlalchemy.orm import Session
from services.repository import PdfRepository
from components.pdf_card import PdfCard
import math

class PdfListView:
    def __init__(self, page: Page, session: Session):
        self.page = page
        self.session = session
        self.pdf_repo = PdfRepository(self.session) # Seu repositório
        # ---- Variáveis para paginação ----
        self.pagina_atual = 1
        self.itens_por_pagina = 10
        self.total_de_paginas = 1
        
        #  ---- Variáveis para controle de interface ----
        self.lista_de_pdfs = ListView(expand=True, spacing=10)
        self.status_paginacao = Text("Página 1 de 1")
        self.btn_anterior = IconButton(Icons.NAVIGATE_BEFORE, on_click=self.ir_pagina_anterior)
        self.btn_proximo = IconButton(Icons.NAVIGATE_NEXT, on_click=self.ir_pagina_proxima)
        
        # Carrega os dados iniciais
        self.carregar_dados()
        
    def carregar_dados(self):
        """Busca os dados da página atual e atualiza a UI."""
        # Simulação do repositório
        total_itens = self.pdf_repo.get_total_count()
        pdfs_da_pagina = self.pdf_repo.find_all(page=self.pagina_atual, per_page=self.itens_por_pagina)
        
        # # --- Simulação para teste ---
        # total_itens = 53
        # pdfs_da_pagina = [{"titulo": f"PDF Exemplo {(self.pagina_atual - 1) * self.itens_por_pagina + i+1}"} for i in range(self.itens_por_pagina)]
        # # ---------------------------
        # Ceil arredonda pra cima
        self.total_de_paginas = math.ceil(total_itens / self.itens_por_pagina)
        
        self.status_paginacao.value = f"Página {self.pagina_atual} de {self.total_de_paginas}"
        
        # Habilita/desabilita botões
        if self.pagina_atual == 1:
            self.btn_anterior.disabled = True
        else:
            self.btn_anterior.disabled = False
        
        # Limpa e preenche a lista
        self.lista_de_pdfs.controls.clear()
        for pdf in pdfs_da_pagina:
            pdf_card = PdfCard(self.page, self.session,pdf["caminho"])
            self.lista_de_pdfs.controls.append(pdf_card.build())
        self.page.update()
    
        
        
    def ir_pagina_anterior(self, e):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.carregar_dados()

    def ir_pagina_proxima(self, e):
        if self.pagina_atual < self.total_de_paginas:
            self.pagina_atual += 1
            self.carregar_dados()
    def build(self):
        """Constrói a interface visual desta página."""
        return Column(
            [
                Text("Lista de PDFs", size=30),
                self.lista_de_pdfs,
                Row(
                    [
                        self.btn_anterior,
                        self.status_paginacao,
                        self.btn_proximo,
                    ],
                    alignment=MainAxisAlignment.CENTER
                )
            ],
            expand=True
        )
        
def list_view(page: Page, session: Session):
    return PdfListView(page, session).build()
