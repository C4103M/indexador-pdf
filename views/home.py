from flet import View, Row, Text, Container, margin, Column, TextField, MainAxisAlignment
from components.sidebar import sidebar
from components.buttons import btn_padrao

def home_view(page):
    titulo = Text("Indexador de PDF", weight="bold", size=32)

    linha_titulo = Container(
        Row(
            controls=[titulo, btn_padrao("Upload",lambda _: page.go("/cadastro"))],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
        ),
        margin=margin.only(top=20),
    )

    barra_pesquisa = TextField(label="Pesquisar PDF", expand=True)

    linha_pesquisa = Container(Row(controls=[barra_pesquisa]))

    col_pdfs = Column(controls=[linha_titulo, linha_pesquisa], expand=True)

    return View(
        route="/",
        controls=[Row(controls=[sidebar(), col_pdfs], expand=True)],
        padding=20,
    )
