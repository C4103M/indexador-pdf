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
)
from components.sidebar import sidebar
from components.buttons import btn_padrao
from sqlalchemy.orm import Session
from services.repository import TurmaRepository, PdfRepository


class HomeView:
    def __init__(self, page: Page, session: Session):
        self.page = page
        self.session = session
        self.turma_repo = TurmaRepository(self.session)
        self.pdf_repo = PdfRepository(self.session)

        self.linha_titulo = Container(
            Row(
                controls=[Text("Indexador de PDF", weight="bold", size=32), btn_padrao("Upload", lambda _: page.go("/cadastro"))],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            margin=margin.only(top=20),
        )
        self.barra_pesquisa = TextField(label="Pesquisar PDF", expand=True)

        self.linha_pesquisa = Container(Row(controls=[self.barra_pesquisa]))

        self.col_pdfs = Column(controls=[self.linha_titulo, self.linha_pesquisa], expand=True)

    def build(self):
        return View(
        route="/",
        controls=[Row(controls=[sidebar(self.page), self.col_pdfs], expand=True)],
        padding=20,
    )

def home_view(page: Page, session: Session):
    return HomeView(page, session).build()
