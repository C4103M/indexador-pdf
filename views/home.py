from flet import (
    View,
    Row,
    Text,
    Container,
    margin,
    Column,
    TextField,
    MainAxisAlignment,
    Page,
    ScrollMode,
    SnackBar,
    Colors
)
from components.sidebar import sidebar
from components.buttons import btn_padrao
from sqlalchemy.orm import Session
from services.repository import TurmaRepository, PdfRepository
from components.pdf_card import PdfCard
from services.debouncer import Debouncer

class HomeView:
    def __init__(self, page: Page, session: Session):
        self.page = page
        self.session = session
        self.turma_repo = TurmaRepository(self.session)
        self.pdf_repo = PdfRepository(self.session)

        self.debouncer = Debouncer(0.5, self._realizar_busca)

        self.linha_titulo = Container(
            Row(
                controls=[Text("Indexador de PDF", weight="bold", size=32), btn_padrao("Upload", lambda _: page.go("/cadastro"))],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            margin=margin.only(top=20),
        )
        self.barra_pesquisa = TextField(label="Pesquisar PDF", expand=True, on_change=self._on_search_change)

        # self.barra_pesquisa.on_change = self.search_pdf
        
        self.linha_pesquisa = Container(Row(controls=[self.barra_pesquisa]))
        
        self.linha_pdfs = Row(expand=True, spacing=10, wrap=True)

        self.col_pdfs = Column(controls=[self.linha_titulo, self.linha_pesquisa, self.linha_pdfs], expand=True, scroll=ScrollMode.ADAPTIVE)
        
    def _on_search_change(self, e):
        """
        Chamado a cada tecla pressionada. Apenas 'chama' o debouncer,
        passando o texto atual da barra de pesquisa.
        """
        termo_buscado = e.control.value
        self.debouncer.call(termo_buscado)
        
    # def _search_pdf(self, e):
    #     """
    #     Busca por PDFs e atualiza a interface. Agora com tratamento de erros.
    #     """
    #     try:
    #         # --- Bloco de Código Principal (o que você quer tentar fazer) ---
    #         termo_buscado = e.control.value
            
    #         # Limpa os resultados da busca anterior
    #         self.linha_pdfs.controls.clear()
            
    #         # Se o termo de busca não estiver vazio, executa a busca
    #         if termo_buscado:
    #             caminhos_pdfs = self.pdf_repo.search_by_term(termo_buscado)
                
    #             cards_para_exibir = []
    #             for caminho in caminhos_pdfs:
    #                 # Cria o componente para cada resultado
    #                 print(caminho)
    #                 componente = PdfCard(self.page, self.session, caminho)
    #                 cards_para_exibir.append(componente.build())
                
    #             # Atualiza a linha de PDFs com a nova lista de cards
    #             self.linha_pdfs.controls = cards_para_exibir

    #         # Atualiza a página para mostrar os resultados (ou a lista limpa)
    #         self.page.update()

    #     except Exception as ex:
    #         # --- Plano B (o que fazer se qualquer erro acontecer no 'try') ---
            
    #         # 1. Imprime o erro no seu terminal para que você (o desenvolvedor) saiba o que aconteceu.
    #         #    Isso torna o erro, que antes estava "escondido", visível.
    #         print(f"ERRO INESPERADO na busca de PDF: {ex}")
            
    #         # 2. Mostra uma mensagem amigável para o usuário.
    #         self.page.open(
    #             SnackBar(
    #                 Text("Ocorreu um erro ao realizar a busca. Tente novamente."),
    #                 bgcolor=Colors.RED_700,
    #                 open=True
    #             )
    #         )
    def _realizar_busca(self, termo_buscado: str):
        """
        Esta é a função de busca REAL. Ela só é executada pelo debouncer
        depois que o utilizador para de digitar.
        """
        try:
            print(f"Executando busca por: '{termo_buscado}'")
            
            # Limpa os resultados da busca anterior
            # ATENÇÃO: É preciso usar page.run_thread porque o Debouncer
            # usa uma thread
            self.page.run_thread(self.linha_pdfs.controls.clear)

            if not termo_buscado:
                self.page.run_thread(self.page.update)
                return

            caminhos_pdfs = self.pdf_repo.search_by_term(termo_buscado)
            
            cards_para_exibir = []
            for caminho in caminhos_pdfs:
                componente = PdfCard(self.page, self.session, caminho)
                cards_para_exibir.append(componente.build())
            
            # Atualiza a interface (também de forma segura)
            def atualizar_controles():
                self.linha_pdfs.controls = cards_para_exibir
                self.page.update()

            self.page.run_thread(atualizar_controles)
            
        except Exception as ex:
            print(f"ERRO na busca com debouncer: {ex}")
        
        
    def build(self):
        return View(
        route="/",
        controls=[Row(controls=[sidebar(self.page), self.col_pdfs], expand=True)],
        padding=20,
    )

def home_view(page: Page, session: Session):
    return HomeView(page, session).build()
