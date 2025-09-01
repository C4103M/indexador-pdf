from flet import *


def home_view(page: Page):
    # Containers laterais
    home = Container(
        content=Row(
            controls=[
                Image("./elements/home.png", width=20, height=20),
                Text("Home", weight="bold"),
            ],
            alignment=MainAxisAlignment.START,
        ),
        width=250,
        height=30,
        padding=padding.only(left=5),
    )

    arquivos = Container(
        content=Row(
            controls=[
                Image("./elements/pasta.png", width=20, height=20),
                Text("Arquivos", weight="bold"),
            ],
            alignment=MainAxisAlignment.START,
        ),
        width=250,
        height=40,
        padding=padding.only(left=5),
    )

    configuracoes = Container(
        content=Row(
            controls=[
                Image("./elements/config.png", width=20, height=20),
                Text("Configurações", weight="bold"),
            ],
            alignment=MainAxisAlignment.START,
        ),
        width=250,
        height=40,
        padding=padding.only(left=5),
    )
    col_indice = Column(controls=[home, arquivos, configuracoes], width=250)

    # Título e botão de upload
    titulo = Text("Indexador de PDF", weight="bold", size=32)
    upload_btn = Container(
        ElevatedButton(
            "Upload",
            on_click=lambda _: page.go("/cadastro"),
            width=100,
            height=40,
            style=ButtonStyle(
                bgcolor={"": "#292524"},
                color={"": "white"},
                shape={"": RoundedRectangleBorder(radius=10)},
            ),
        ),
        # margin=margin.only(right=40),
    )

    linha_titulo = Container(
        Row(
            controls=[titulo, upload_btn],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
        ),
        margin=margin.only(top=20),
    )
    barra_pesquisa = TextField(label="Pesquisar PDF",expand=True)
    linha_pesquisa = Container(
        Row(
            controls=[barra_pesquisa],
        ),
        
    )
    
    
    col_pdfs = Column(controls=[linha_titulo, linha_pesquisa], expand=True)

    # Agora em vez de adicionar direto no `page`, criamos a View
    return View(
        route="/",
        controls=[
            Row(controls=[col_indice, col_pdfs], expand=True)
        ],
        padding=padding.all(60)
    )


def cadastro_view(page: Page):
    
    # Função chamada quando o usuário seleciona um arquivo
    def on_file_selected(e: FilePickerResultEvent):
        if e.files:
            page.snack_bar = SnackBar(Text(f"Arquivo escolhido: {e.files[0].name}"))
        else:
            page.snack_bar = SnackBar(Text("Nenhum arquivo selecionado."))
        page.snack_bar.open = True
        page.update()

    # Criando o FilePicker
    file_picker = FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    # Preview do PDF (lado esquerdo)
    pdf_preview = Container(
        content=Text("Preview do PDF selecionado", size=16, weight="bold"),
        alignment=alignment.center,
        bgcolor="#f4f4f5",
        border_radius=10,
        width= 250,
        height = 250 * 1.414
    )
    # Botão de upload
    upload_btn = ElevatedButton(
        "Upload",
        on_click=lambda _: file_picker.pick_files(),
        width=150,
        height=25,
        style=ButtonStyle(
            bgcolor={"": "#292524"},
            color={"": "white"},
            shape={"": RoundedRectangleBorder(radius=4)},
        ),
    )
    #Elementos do lado esquerdo
    col_esquerda = Column(
        controls=[pdf_preview, upload_btn],
        alignment="center",
    )
    # Campo título
    titulo_field = TextField(
        label="Título do Documento",
        expand=True,
    )

    # Campo tags
    tags_field = TextField(
        label="Tags (separe por vírgula)",
        expand=True,
    )

    

    # Coluna da direita (formulário)
    col_direita = Column(
        controls=[
            titulo_field,
            tags_field,
        ],
        spacing=20,
        expand=True,
    )

    # Layout principal
    return View(
        route="/cadastro",
        controls=[
            Row(
                controls=[
                    col_esquerda,
                    col_direita,
                ],
                expand=True,
                spacing=40,
            )
        ],
        padding=padding.all(40),
    )

def main(page: Page):
    page.theme_mode = ThemeMode.LIGHT

    # Configurando rotas
    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page))
        elif page.route == "/cadastro":
            page.views.append(cadastro_view(page))
        page.update()

    page.on_route_change = route_change
    page.go("/")  # inicializa na home


app(target=main)
